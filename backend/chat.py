from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, ConfigDict, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import sys
import os
from pathlib import Path
from sqlalchemy.orm import Session
import traceback

# Database
from database import get_db
from sqlalchemy import text

# Import auth and rate limiting
from auth import get_current_user_dependency as get_current_user
from rate_limiter import rate_limit, get_client_ip
from errors import (
    AppException, ValidationException, NotFoundError,
    AuthenticationError, create_error_response
)

# AI engine import path
CURRENT_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = CURRENT_DIR.parent  # project_root/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# AI Engine imports
try:
    from ai_engine.tax_engine.agent_graph import build_graph
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    AI_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI Engine import failed: {e}")
    AI_ENGINE_AVAILABLE = False

router = APIRouter()

# Initialize AI Graph
ai_graph = None
if AI_ENGINE_AVAILABLE:
    try:
        ai_graph = build_graph()
        print(" AI Engine graph built successfully")
    except Exception as e:
        print(f" AI Engine initialization failed: {e}")
        traceback.print_exc()
        AI_ENGINE_AVAILABLE = False

# Pydanti models
class Citation(BaseModel):
    chunk_id: str
    source: str
    pages: str
    quote: str
    
    model_config = ConfigDict(from_attributes=True)

class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    citations: Optional[List[Citation]] = None
    metadata: Optional[Dict] = None
    
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    new_session: bool = False
    
    @validator('message')
    def validate_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:
            raise ValueError('Message is too long')
        return v

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    citations: Optional[List[Citation]] = None
    created_at: datetime
    route: str = "qa"
    refusal: bool = False
    conversation_title: Optional[str] = None

class HistoryResponse(BaseModel):
    session_id: str
    title: Optional[str]
    messages: List[MessageRead]
    created_at: datetime
    updated_at: datetime

class ConversationItem(BaseModel):
    session_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    last_message: Optional[str] = None

def get_or_create_conversation(
    db: Session, 
    session_id: str, 
    user_id: Optional[int] = None
) -> int:
    """Get existing conversation or create new one"""
    try:
        print(f"🔍 Conversation lookup - Session: {session_id}, User: {user_id}")
        
        # Check if conversation exists
        if user_id:
            result = db.execute(
                text("""
                    SELECT id, user_id FROM conversations 
                    WHERE session_id = :session_id
                """),
                {"session_id": session_id}
            ).fetchone()
        else:
            result = db.execute(
                text("SELECT id, user_id FROM conversations WHERE session_id = :session_id"),
                {"session_id": session_id}
            ).fetchone()
        
        if result:
            conv_id, existing_user_id = result
            
            # Update conversation with user_id if not set
            if user_id and not existing_user_id:
                db.execute(
                    text("""
                        UPDATE conversations 
                        SET updated_at = NOW(), user_id = :user_id 
                        WHERE id = :id
                    """),
                    {"user_id": user_id, "id": conv_id}
                )
            else:
                db.execute(
                    text("UPDATE conversations SET updated_at = NOW() WHERE id = :id"),
                    {"id": conv_id}
                )
            db.commit()
            
            print(f" Found existing conversation: {conv_id}")
            return conv_id
        else:
            # Create new conversation
            print(f" Creating new conversation for session: {session_id}")
            
            if user_id:
                result = db.execute(
                    text("""
                        INSERT INTO conversations (session_id, user_id, title) 
                        VALUES (:session_id, :user_id, :title)
                    """),
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "title": "New Conversation"
                    }
                )
            else:
                result = db.execute(
                    text("""
                        INSERT INTO conversations (session_id, title) 
                        VALUES (:session_id, :title)
                    """),
                    {"session_id": session_id, "title": "New Conversation"}
                )
            
            db.commit()
            
            # Get the new ID
            result = db.execute(
                text("SELECT id FROM conversations WHERE session_id = :session_id"),
                {"session_id": session_id}
            ).fetchone()
            
            if result:
                conv_id = result[0]
                print(f" Created new conversation: {conv_id}")
                return conv_id
            else:
                raise AppException(
                    error_code="CONVERSATION_CREATION_FAILED",
                    message="Failed to create conversation",
                    status_code=500
                )
                
    except AppException:
        raise
    except Exception as e:
        db.rollback()
        print(f" Database error: {e}")
        traceback.print_exc()
        raise AppException(
            error_code="DATABASE_ERROR",
            message="Failed to access conversation",
            status_code=500,
            detail=str(e)
        )

def save_message(
    db: Session, 
    conversation_id: int, 
    role: str, 
    content: str,  
    citations: Optional[List[Dict]] = None, 
    metadata: Optional[Dict] = None
):
    """Save message to database"""
    try:
        citations_json = json.dumps(citations) if citations else None
        metadata_json = json.dumps(metadata) if metadata else None
        
        result = db.execute(
            text("""
                INSERT INTO messages 
                (conversation_id, role, content, citations, metadata)
                VALUES (:conversation_id, :role, :content, :citations, :metadata)
            """),
            {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "citations": citations_json,
                "metadata": metadata_json
            }
        )
        db.commit()
        message_id = result.lastrowid
        
        # Update conversation title if it's the first user message
        if role == "user":
            msg_count = db.execute(
                text("SELECT COUNT(*) FROM messages WHERE conversation_id = :conv_id"),
                {"conv_id": conversation_id}
            ).scalar()
            
            if msg_count == 1:  # First user message
                title = content[:50] + "..." if len(content) > 50 else content
                db.execute(
                    text("UPDATE conversations SET title = :title WHERE id = :id"),
                    {"title": title, "id": conversation_id}
                )
                db.commit()
        
        print(f" Saved {role} message, ID: {message_id}")
        return True
        
    except Exception as e:
        print(f" Failed to save message: {e}")
        db.rollback()
        return False

def get_conversation_history(
    db: Session, 
    session_id: str, 
    limit: int = 100
) -> List[Dict]:
    """Get conversation history - FIXED for AI agent compatibility"""
    try:
        result = db.execute(
            text("""
                SELECT m.id, m.role, m.content, m.created_at, m.citations, m.metadata
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.session_id = :session_id
                ORDER BY m.created_at ASC
                LIMIT :limit
            """),
            {"session_id": session_id, "limit": limit}
        )
        
        messages = []
        for row in result:
            # Ensure content is always a string for AI agent
            content = str(row[2]) if row[2] is not None else ""
            
            citations = None
            if row[4]:
                try:
                    citations_raw = json.loads(row[4])
                    citations = [Citation(**cite) for cite in citations_raw]
                except:
                    pass
            
            metadata = None
            if row[5]:
                try:
                    metadata = json.loads(row[5])
                except:
                    pass
            
            messages.append({
                "id": row[0],
                "role": row[1],  # "user" or "assistant"
                "content": content,  # String content
                "created_at": row[3],
                "citations": citations,
                "metadata": metadata
            })
        return messages
        
    except Exception as e:
        print(f"⚠️ Error fetching history: {e}")
        traceback.print_exc()
        return []

# AIclient with fixed integration
class AIClient:
    @staticmethod
    def get_response(
        session_id: str, 
        user_message: str, 
        conversation_history: List[Dict] = None
    ) -> Dict:
        """Get response from AI engine - FIXED VERSION"""
        if not AI_ENGINE_AVAILABLE or not ai_graph:
            print(" AI Engine not available, using fallback")
            return AIClient._fallback_response(user_message)
        
        try:
            print(f" Calling AI Agent for session: {session_id}")
            messages = []
            
            # Add conversation history if available
            if conversation_history:
                print(f"📜 Adding {len(conversation_history)} recent messages from history")
                for msg in conversation_history:
                    if msg["role"] == "user":
                        # Create HumanMessage object
                        messages.append(HumanMessage(content=str(msg["content"])))
                    elif msg["role"] == "assistant":
                        # Create AIMessage object - check if it's JSON or plain text
                        content = msg["content"]
                        if isinstance(content, dict):
                            # If it's already a dict (like from previous AI response)
                            content = json.dumps(content)
                        messages.append(AIMessage(content=str(content)))
            
            # Add current user message as HumanMessage
            messages.append(HumanMessage(content=user_message))
            
            print(f"📤 Total messages being sent to AI: {len(messages)}")
            
            # Debug
            for i, msg in enumerate(messages):
                print(f"  [{i}] {type(msg).__name__}: {msg.content[:80]}...")
            
            # Call LangGraph with the correct state structure (The graph expects a dict with "messages" key containing LangChain messages)
            out = ai_graph.invoke(
                {"messages": messages},
                config={"configurable": {"thread_id": session_id}},
            )
            
            print(f" AI Graph invoked successfully")
            
            # Extract the AI response
            ai_messages = out.get("messages", [])
            
            if not ai_messages:
                print(" No messages in AI response")
                raise AppException(
                    error_code="AI_NO_RESPONSE",
                    message="AI engine did not return a response",
                    status_code=500
                )
            
            # Get the last AI message
            last_message = ai_messages[-1]
            print(f"📥 Last message type: {type(last_message)}")
            
            # Handle both JSON and plain text responses
            if isinstance(last_message, AIMessage):
                content = last_message.content
            elif isinstance(last_message, dict):
                content = last_message.get("content", "")
            else:
                content = str(last_message)
            
            print(f" AI Response content length: {len(content)}")
            print(f" AI Response preview: {content[:200]}...")
            
            # Try to parse as JSON (your agent should return JSON)
            try:
                payload = json.loads(content)
                print(f" AI response parsed as JSON")
                
                answer = payload.get("answer", "")
                citations_raw = payload.get("citations", [])
                route = payload.get("route", "qa")
                refusal = bool(payload.get("refusal", False))
                
                # Convert citations to Citation objects
                citations = []
                for cite in citations_raw:
                    if isinstance(cite, dict):
                        citations.append(Citation(
                            chunk_id=cite.get("chunk_id", ""),
                            source=cite.get("source", "unknown"),
                            pages=cite.get("pages", "p.?"),
                            quote=cite.get("quote", "")
                        ))
                
                return {
                    "answer": answer,
                    "citations": citations,
                    "route": route,
                    "refusal": refusal
                }
                
            except json.JSONDecodeError:
            
                print(f" AI response not JSON, treating as plain text")
                return {
                    "answer": content,
                    "citations": [],  
                    "route": "qa",
                    "refusal": False
                }
                
        except AppException as ae:
            print(f" AppException in AI client: {ae}")
            raise
        except Exception as e:
            print(f" AI Engine error: {e}")
            traceback.print_exc()
            return AIClient._fallback_response(user_message)
    
    @staticmethod
    def _fallback_response(user_message: str) -> Dict:
        """Fallback when AI engine fails"""
        print(f"🔄 Using fallback response for: {user_message[:50]}...")
        user_lower = user_message.lower()
        
        # Simple keyword-based responses
        if any(word in user_lower for word in ["hello", "hi", "hey", "greetings"]):
            answer = "Hello! I'm here to help you understand Nigerian Tax Reform Bills. How can I assist you today?"
        elif any(word in user_lower for word in ["vat", "value added tax"]):
            answer = "The Value Added Tax (VAT) system is being reformed. The standard rate remains 7.5%, but there are changes to exemptions and collection methods."
        elif any(word in user_lower for word in ["tax", "reform", "bill"]):
            answer = "The 2024 Tax Reform Bills aim to simplify Nigeria's tax system. Key changes include revised VAT distribution, new taxpayer categories, and digital tax collection."
        else:
            answer = "I can help you understand Nigerian Tax Reform Bills. Try asking about VAT changes, tax exemptions, or how the reforms affect individuals and businesses."
        
        return {
            "answer": answer,
            "citations": [],
            "route": "fallback",
            "refusal": False
        }

# API endpoints with rate limiting
@router.post("/chat", response_model=ChatResponse)
@rate_limit("chat")  # 50 messages per hour
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Main chat endpoint - UPDATED with proper AI integration"""
    try:
        # Generate or use session ID
        if chat_request.new_session or not chat_request.session_id:
            session_id = str(uuid.uuid4())
        else:
            session_id = chat_request.session_id
        
        user_id = current_user.get("id") if current_user else None
        
        print(f"💬 Chat request - Session: {session_id}, User: {user_id}")
        print(f"💬 User message: {chat_request.message}")
        
        # Get or create conversation
        conversation_id = get_or_create_conversation(db, session_id, user_id)
        
        # Save user message
        save_message(db, conversation_id, "user", chat_request.message.strip())
        
        # Get recent history (last 6 messages for context)
        recent_history = get_conversation_history(db, session_id, limit=6)
        print(f" Recent history loaded: {len(recent_history)} messages")
        
        # Get AI response
        ai_response = AIClient.get_response(
            session_id=session_id,
            user_message=chat_request.message,
            conversation_history=recent_history
        )
        
        print(f" AI Response - Route: {ai_response['route']}, Citations: {len(ai_response['citations'] or [])}")
        
        # Save AI response
        citations_for_db = None
        if ai_response["citations"]:
            citations_for_db = [cite.model_dump() for cite in ai_response["citations"]]
        
        save_message(
            db, conversation_id, "assistant",
            ai_response["answer"],
            citations_for_db,
            {"route": ai_response["route"], "refusal": ai_response["refusal"]}
        )
        
        # Get conversation title
        title_result = db.execute(
            text("SELECT title FROM conversations WHERE session_id = :session_id"),
            {"session_id": session_id}
        ).fetchone()
        title = title_result[0] if title_result else None
        
        # Log successful chat
        try:
            db.execute(
                text("""
                    INSERT INTO system_logs (level, service, message, ip_address, user_id)
                    VALUES ('INFO', 'chat', 'Chat message processed', :ip, :user_id)
                """),
                {"ip": get_client_ip(request), "user_id": user_id}
            )
            db.commit()
        except Exception as log_error:
            print(f" Failed to log to database: {log_error}")
        
        return ChatResponse(
            answer=ai_response["answer"],
            session_id=session_id,
            citations=ai_response["citations"],
            created_at=datetime.now(),
            route=ai_response["route"],
            refusal=ai_response["refusal"],
            conversation_title=title
        )
        
    except AppException as ae:
        print(f" AppException in chat endpoint: {ae}")
        raise
    except Exception as e:
        print(f" Chat error: {e}")
        traceback.print_exc()
        
        # Log error
        try:
            db.execute(
                text("""
                    INSERT INTO system_logs (level, service, message, ip_address, user_id, details)
                    VALUES ('ERROR', 'chat', 'Chat processing failed', :ip, :user_id, :details)
                """),
                {
                    "ip": get_client_ip(request),
                    "user_id": current_user.get("id") if current_user else None,
                    "details": json.dumps({"error": str(e)})
                }
            )
            db.commit()
        except:
            pass
        
        raise AppException(
            error_code="CHAT_PROCESSING_ERROR",
            message="Failed to process your message",
            status_code=500,
            detail="Please try again in a moment"
        )

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    try:
        # Check if conversation exists and user has access
        if current_user:
            result = db.execute(
                text("""
                    SELECT c.id, c.title, c.created_at, c.updated_at
                    FROM conversations c
                    WHERE c.session_id = :session_id 
                    AND (c.user_id = :user_id OR c.user_id IS NULL)
                """),
                {"session_id": session_id, "user_id": current_user["id"]}
            ).fetchone()
        else:
            result = db.execute(
                text("""
                    SELECT c.id, c.title, c.created_at, c.updated_at
                    FROM conversations c
                    WHERE c.session_id = :session_id AND c.user_id IS NULL
                """),
                {"session_id": session_id}
            ).fetchone()
        
        if not result:
            raise NotFoundError(
                resource="Conversation",
                detail="Conversation not found or you don't have access"
            )
        
        conv_id, title, created_at, updated_at = result
        
        # Get messages
        messages_data = get_conversation_history(db, session_id)
        messages = [MessageRead(**msg) for msg in messages_data]
        
        return HistoryResponse(
            session_id=session_id,
            title=title,
            messages=messages,
            created_at=created_at,
            updated_at=updated_at
        )
        
    except AppException:
        raise
    except Exception as e:
        print(f" Error in get_history: {e}")
        traceback.print_exc()
        raise AppException(
            error_code="HISTORY_FETCH_ERROR",
            message="Failed to fetch conversation history",
            status_code=500,
            detail=str(e)
        )

@router.get("/my-conversations", response_model=List[ConversationItem])
async def get_user_conversations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for authenticated user"""
    if not current_user:
        raise AuthenticationError(
            message="Authentication required",
            detail="Please login to view your conversations"
        )
    
    try:
        result = db.execute(
            text("""
                SELECT 
                    c.session_id,
                    c.title,
                    c.created_at,
                    c.updated_at,
                    COUNT(m.id) as message_count,
                    MAX(m.created_at) as last_message_time
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.user_id = :user_id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
            """),
            {"user_id": current_user["id"]}
        ).fetchall()
        
        conversations = []
        for row in result:
            conversations.append(ConversationItem(
                session_id=row[0],
                title=row[1],
                created_at=row[2],
                updated_at=row[3],
                message_count=row[4] or 0
            ))
        
        return conversations
        
    except Exception as e:
        print(f" Error in get_user_conversations: {e}")
        raise AppException(
            error_code="CONVERSATIONS_FETCH_ERROR",
            message="Failed to fetch your conversations",
            status_code=500,
            detail=str(e)
        )

@router.get("/history/{session_id}/recent")
async def get_recent_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get only recent conversation history (last 5 messages)"""
    try:
        messages = get_recent_conversation_history(db, session_id, last_n_messages=5)
        
        # Convert to MessageRead format
        message_list = []
        for msg in messages:
            message_list.append(MessageRead(**msg))
        
        return {
            "session_id": session_id,
            "messages": message_list,
            "count": len(message_list),
            "note": "Showing last 5 messages only"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recent history: {str(e)}"
        )

@router.post("/new-session")
async def create_new_session(
    current_user: Optional[dict] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        user_id = current_user.get("id") if current_user else None
        
        # Create conversation
        conversation_id = get_or_create_conversation(db, session_id, user_id)
        
        return {
            "session_id": session_id,
            "message": "New session created",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f" Error in create_new_session: {e}")
        raise AppException(
            error_code="SESSION_CREATION_ERROR",
            message="Failed to create new session",
            status_code=500,
            detail=str(e)
        )

# Admin endpoints
@router.get("/debug/conversations")
async def debug_conversations(db: Session = Depends(get_db)):
    """Debug endpoint to list all conversations"""
    try:
        result = db.execute(
            text("""
                SELECT 
                    c.id, c.session_id, c.user_id, c.title,
                    c.created_at, c.updated_at,
                    COUNT(m.id) as message_count
                FROM conversations c
                LEFT JOIN messages m ON c.id = m.conversation_id
                GROUP BY c.id
                ORDER BY c.updated_at DESC
                LIMIT 20
            """)
        ).fetchall()
        
        return {
            "conversations": [
                {
                    "id": row[0],
                    "session_id": row[1],
                    "user_id": row[2],
                    "title": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None,
                    "message_count": row[6]
                }
                for row in result
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@router.delete("/conversations/{session_id}")
async def delete_conversation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    if not current_user:
        raise AuthenticationError(
            message="Authentication required",
            detail="Please login to delete conversations"
        )
    
    try:
        # Verify ownership
        result = db.execute(
            text("SELECT id FROM conversations WHERE session_id = :session_id AND user_id = :user_id"),
            {"session_id": session_id, "user_id": current_user["id"]}
        ).fetchone()
        
        if not result:
            raise NotFoundError(
                resource="Conversation",
                detail="Conversation not found or you don't have permission to delete it"
            )
        
        # Delete conversation
        db.execute(
            text("DELETE FROM conversations WHERE session_id = :session_id"),
            {"session_id": session_id}
        )
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except AppException:
        raise
    except Exception as e:
        db.rollback()
        print(f" Error deleting conversation: {e}")
        raise AppException(
            error_code="CONVERSATION_DELETION_ERROR",
            message="Failed to delete conversation",
            status_code=500,
            detail=str(e)
        )
