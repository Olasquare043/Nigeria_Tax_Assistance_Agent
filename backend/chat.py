from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, ConfigDict
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

# ===== AI ENGINE IMPORT PATH =====
CURRENT_DIR = Path(__file__).resolve().parent  # backend/
PROJECT_ROOT = CURRENT_DIR.parent  # project_root/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# AI Engine imports
try:
    from ai_engine.tax_engine.agent_graph import build_graph
    from langchain_core.messages import HumanMessage, AIMessage
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
        print("✅ AI Engine graph built successfully")
    except Exception as e:
        print(f"❌ AI Engine initialization failed: {e}")
        AI_ENGINE_AVAILABLE = False

# Pydantic Models
class Citation(BaseModel):
    chunk_id: str
    source: str
    pages: str
    quote: str
    
    model_config = ConfigDict(from_attributes=True)

class MessageRead(BaseModel):
    id: int
    role: str
    text: str
    timestamp: datetime
    citations: Optional[List[Citation]] = None
    route: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    citations: Optional[List[Citation]] = None
    timestamp: datetime
    route: str = "qa"
    refusal: bool = False

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageRead]

# Helper Functions - REAL DATABASE OPERATIONS
def get_or_create_conversation(db: Session, session_id: str) -> int:
    """Get existing conversation or create new one"""
    try:
        print(f"🔍 Looking for conversation: {session_id}")
        result = db.execute(
            text("SELECT id FROM conversations_table WHERE session_id = :session_id"),
            {"session_id": session_id}
        ).fetchone()
        
        if result:
            conversation_id = result[0]
            # Update timestamp
            db.execute(
                text("UPDATE conversations_table SET updated_at = NOW() WHERE id = :id"),
                {"id": conversation_id}
            )
            db.commit()
            print(f" Found existing conversation: {conversation_id}")
            return conversation_id
        else:
            # Create new conversation
            print(f" Creating new conversation for: {session_id}")
            result = db.execute(
                text("INSERT INTO conversations_table (session_id) VALUES (:session_id)"),
                {"session_id": session_id}
            )
            db.commit()
            
            # Get the new ID
            result = db.execute(
                text("SELECT id FROM conversations_table WHERE session_id = :session_id"),
                {"session_id": session_id}
            ).fetchone()
            
            if result:
                conversation_id = result[0]
                print(f" Created new conversation: {conversation_id}")
                return conversation_id
            else:
                print(" Failed to retrieve new conversation ID")
                raise Exception("Failed to retrieve new conversation ID")
                
    except Exception as e:
        db.rollback()
        print(f" Database error in get_or_create_conversation: {e}")
        traceback.print_exc()
        # Return fake ID to allow chat to continue
        return 1

def save_message(db: Session, conversation_id: int, role: str, message_text: str,  
                 citations: Optional[List[Dict]] = None, route: str = None, refusal: bool = False):
    """Save message to database"""
    try:
        print(f"💾 Attempting to save {role} message for conv {conversation_id}")
        
        citations_json = json.dumps(citations) if citations else None
        
        result = db.execute(
            text("""
                INSERT INTO messages_table 
                (conversation_id, role, text, citations, route, refusal)
                VALUES (:conversation_id, :role, :message_text, :citations, :route, :refusal)
            """),
            {
                "conversation_id": conversation_id,
                "role": role,
                "message_text": message_text,  
                "citations": citations_json,
                "route": route,
                "refusal": refusal
            }
        )
        db.commit()
        message_id = result.lastrowid
        print(f"✅ Saved {role} message to DB, ID: {message_id}")
        return True
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        traceback.print_exc()
        db.rollback()
        return False  # Allow chat to continue even if save fails

def get_conversation_history(db: Session, session_id: str, limit: int = 50) -> List[Dict]:
    """Get conversation history for a session"""
    try:
        result = db.execute(
            text("""
                SELECT m.id, m.role, m.text, m.timestamp, m.citations, m.route
                FROM messages_table m
                JOIN conversations_table c ON m.conversation_id = c.id
                WHERE c.session_id = :session_id
                ORDER BY m.timestamp ASC
                LIMIT :limit
            """),
            {"session_id": session_id, "limit": limit}
        )
        
        messages = []
        for row in result:
            citations = None
            if row[4]:
                try:
                    citations_raw = json.loads(row[4])
                    citations = [Citation(**cite) for cite in citations_raw]
                except:
                    pass
            
            messages.append({
                "id": row[0],
                "role": row[1],
                "text": row[2],
                "timestamp": row[3],
                "citations": citations,
                "route": row[5]
            })
        return messages
    except Exception as e:
        print(f"⚠️ Error fetching history: {e}")
        return []

def get_recent_conversation_history(db: Session, session_id: str, last_n_messages: int = 5) -> List[Dict]:
    """Get only the last N messages from conversation history"""
    try:
        result = db.execute(
            text("""
                SELECT m.id, m.role, m.text, m.timestamp, m.citations, m.route
                FROM messages_table m
                JOIN conversations_table c ON m.conversation_id = c.id
                WHERE c.session_id = :session_id
                ORDER BY m.timestamp DESC
                LIMIT :limit
            """),
            {"session_id": session_id, "limit": last_n_messages}
        )
        
        messages = []
        for row in result:
            citations = None
            if row[4]:
                try:
                    citations_raw = json.loads(row[4])
                    citations = [Citation(**cite) for cite in citations_raw]
                except:
                    pass
            
            messages.append({
                "id": row[0],
                "role": row[1],
                "text": row[2],
                "timestamp": row[3],
                "citations": citations,
                "route": row[5]
            })
        
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        return messages
    except Exception as e:
        print(f"⚠️ Error fetching recent history: {e}")
        return []

# AI Client
class AIClient:
    @staticmethod
    def get_response(session_id: str, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """Get response from AI engine with conversation history"""
        if not AI_ENGINE_AVAILABLE or not ai_graph:
            return AIClient._fallback_response(user_message)
        
        try:
            # Prepare messages for LangGraph
            messages = []
            
            # Add conversation history if available
            if conversation_history:
                print(f"📜 Adding {len(conversation_history)} recent messages from history")
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["text"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["text"]))
            
            # Add current user message
            messages.append(HumanMessage(content=user_message))
            
            print(f"📤 Total messages sent to AI: {len(messages)}")
            
            # Call LangGraph WITH history
            out = ai_graph.invoke(
                {"messages": messages},  # Send all messages
                config={"configurable": {"thread_id": session_id}},
            )
            
            # Extract route from LangGraph state
            route = out.get("route", "qa")
            
            # Get the last message
            msgs = out.get("messages", [])
            if not msgs:
                raise Exception("No response from AI")
            
            last = msgs[-1]
            content = last.content if hasattr(last, "content") else str(last)
            
            # Try to parse as JSON (QA/compare/claim_check responses)
            try:
                payload = json.loads(content)
                
                answer = payload.get("answer", "")
                citations_raw = payload.get("citations", [])
                refusal = bool(payload.get("refusal", False))
                
                # Convert citations 
                citations = []
                for cite in citations_raw:
                    citations.append(Citation(
                        chunk_id=cite.get("chunk_id", ""),
                        source=cite.get("source", "unknown"),
                        pages=cite.get("pages", "p.?"),
                        quote=cite.get("quote", "")
                    ))
                
                return {
                    "answer": answer,
                    "citations": citations,  # Could be empty list []
                    "route": route,
                    "refusal": refusal
                }
            except json.JSONDecodeError:
                # Non-JSON response (e.g., smalltalk, clarify)
                return {
                    "answer": content,
                    "citations": [],  
                    "route": route,
                    "refusal": False
                }
                
        except Exception as e:
            print(f"⚠️ AI Engine error: {e}")
            traceback.print_exc()
            return AIClient._fallback_response(user_message)
    
    @staticmethod
    def _fallback_response(user_message: str) -> Dict:
        """Fallback when AI engine fails"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["vat", "value added tax"]):
            answer = "The VAT system is being reformed. Ask about VAT derivation or rates."
            route = "qa"
        elif any(word in user_lower for word in ["hello", "hi", "hey"]):
            answer = "Hello! I can help with Nigerian Tax Reform questions."
            route = "smalltalk"
        else:
            answer = "I can help with Nigerian Tax Reform questions. Try asking about VAT, exemptions, or timelines."
            route = "clarify"
        
        return {
            "answer": answer,
            "citations": [], 
            "route": route,
            "refusal": False
        }

# API Endpoints
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Main chat endpoint with AI integration"""
    print(f"📨 Chat request: session={request.session_id}, message='{request.message[:50]}...'")
    
    try:
        # Validate input
        if not request.session_id or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session ID and message are required"
            )
        
        # Get/create conversation
        conversation_id = get_or_create_conversation(db, request.session_id)
        
        # Save user message
        save_message(db, conversation_id, "user", request.message) 
        
        # Get only the last 5 messages from conversation history
        recent_history = get_recent_conversation_history(db, request.session_id, last_n_messages=5)
        
        # Get AI response WITH recent history
        ai_response = AIClient.get_response(
            session_id=request.session_id,
            user_message=request.message,
            conversation_history=recent_history  # Pass only last 5 messages
        )
        
        print(f"🤖 AI Response - Route: {ai_response['route']}, Citations: {len(ai_response['citations'])}")
        
        # Save AI response
        citations_for_db = None
        if ai_response["citations"]:
            citations_for_db = [cite.model_dump() for cite in ai_response["citations"]]
        
        save_message(
            db, conversation_id, "assistant", 
            ai_response["answer"],  
            citations_for_db,
            ai_response["route"],
            ai_response["refusal"]
        )
        
        # Return response
        return ChatResponse(
            answer=ai_response["answer"],
            session_id=request.session_id,
            citations=ai_response["citations"],  
            timestamp=datetime.now(),
            route=ai_response["route"],
            refusal=ai_response["refusal"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"🔥 Chat error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get conversation history"""
    try:
        messages = get_conversation_history(db, session_id)
        
        # Convert to MessageRead format
        message_list = []
        for msg in messages:
            message_list.append(MessageRead(**msg))
        
        return HistoryResponse(
            session_id=session_id,
            messages=message_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching history: {str(e)}"
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
async def create_new_session(db: Session = Depends(get_db)):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        conversation_id = get_or_create_conversation(db, session_id)
        
        return {
            "session_id": session_id,
            "message": "New session created",
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )

# ===== DATABASE DEBUG ENDPOINT =====
@router.get("/debug/db-test")
async def debug_db_test(db: Session = Depends(get_db)):
    """Test database connection and saving"""
    try:
        print("🔍 Running database debug test...")
        
        # Test 1: Check connection
        db.execute(text("SELECT 1"))
        print("✅ Database connection OK")
        
        # Test 2: Count existing records
        conv_count = db.execute(text("SELECT COUNT(*) FROM conversations_table")).scalar() or 0
        msg_count = db.execute(text("SELECT COUNT(*) FROM messages_table")).scalar() or 0
        print(f"📊 Existing: {conv_count} conversations, {msg_count} messages")
        
        # Test 3: Create test conversation
        test_session = f"debug-test-{datetime.now().timestamp()}"
        print(f"📝 Creating test session: {test_session}")
        conv_id = get_or_create_conversation(db, test_session)
        
        # Test 4: Save test messages
        print("💾 Saving test messages...")
        success1 = save_message(db, conv_id, "user", "Test user message", [], "qa", False)
        success2 = save_message(db, conv_id, "assistant", "Test AI response", 
                               [{"chunk_id": "test", "source": "test.pdf", "pages": "p.1", "quote": "Test quote"}], 
                               "qa", False)
        
        # Test 5: Verify save
        new_msg_count = db.execute(text("SELECT COUNT(*) FROM messages_table")).scalar() or 0
        messages_added = new_msg_count - msg_count
        
        return {
            "database_working": True,
            "test_save_success": success1 and success2,
            "initial_counts": {"conversations": conv_count, "messages": msg_count},
            "final_counts": {"conversations": conv_count + 1, "messages": new_msg_count},
            "messages_added": messages_added,
            "test_session": test_session,
            "test_conversation_id": conv_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Database test failed: {error_msg}")
        return {
            "database_working": False,
            "error": error_msg,
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/debug/db-status")
async def debug_db_status(db: Session = Depends(get_db)):
    """Check current database status"""
    try:
        conv_count = db.execute(text("SELECT COUNT(*) FROM conversations_table")).scalar() or 0
        msg_count = db.execute(text("SELECT COUNT(*) FROM messages_table")).scalar() or 0
        
        # Get recent conversations
        recent_conv = db.execute(
            text("""
                SELECT session_id, created_at, 
                       (SELECT COUNT(*) FROM messages_table m WHERE m.conversation_id = c.id) as message_count
                FROM conversations_table c
                ORDER BY created_at DESC
                LIMIT 5
            """)
        ).fetchall()
        
        recent_conversations = []
        for row in recent_conv:
            recent_conversations.append({
                "session_id": row[0],
                "created_at": row[1].isoformat() if row[1] else None,
                "message_count": row[2] or 0
            })
        
        return {
            "status": "connected",
            "counts": {
                "conversations": conv_count,
                "messages": msg_count
            },
            "recent_conversations": recent_conversations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

