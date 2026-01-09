import { useState, useEffect, useCallback } from 'react';
import { chatAPI } from '../utils/api'; 
import { truncateText } from '../utils/helpers';


const api = chatAPI; 

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState('');
  const [recentChats, setRecentChats] = useState([]);

  // Initialize session with backend
  useEffect(() => {
    const initSession = async () => {
      try {
        console.log('🔄 Initializing chat session...');
        
        // 1. Load recent chats from localStorage
        const savedChats = localStorage.getItem('recent_chats');
        if (savedChats) {
          const parsedChats = JSON.parse(savedChats);
          setRecentChats(parsedChats);
          console.log(`📂 Loaded ${parsedChats.length} recent chats from storage`);
        }
        
        // 2. Check for active session in localStorage
        let activeSessionId = localStorage.getItem('tax_reform_active_session');
        
        if (activeSessionId && activeSessionId !== 'undefined') {
          console.log(' Found active session:', activeSessionId.substring(0, 12) + '...');
          
          try {
            // Verify session exists in backend
            const history = await api.getHistory(activeSessionId);
            console.log(' Session exists in backend');
            
            // Set active session ID
            setSessionId(activeSessionId);
            
            // Load messages for this session
            if (history.messages && history.messages.length > 0) {
              const formattedMessages = history.messages.map(msg => ({
                id: msg.id || Date.now(),
                role: msg.role,
                text: msg.text,
                timestamp: msg.timestamp,
                citations: msg.citations || [],
                route: msg.route || 'qa',
                refusal: msg.refusal || false
              }));
              setMessages(formattedMessages);
              console.log(`📜 Loaded ${formattedMessages.length} messages`);
            }
            
          } catch (historyError) {
            console.log(' Active session not found, creating new:', historyError.message);
            await createNewSession();
          }
        } else {
          // No active session, create new one
          console.log(' No active session, creating new...');
          await createNewSession();
        }
        
      } catch (err) {
        console.error(' Error initializing session:', err);
        // Fallback to local session ID
        const fallbackId = `fallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('tax_reform_active_session', fallbackId);
        setSessionId(fallbackId);
      }
    };
    
    const createNewSession = async () => {
      try {
        console.log(' Creating new session via backend...');
        const response = await api.createSession();
        const newSessionId = response.session_id;
        
        console.log(' Created new session:', newSessionId.substring(0, 12) + '...');
        
        // Save as active session
        localStorage.setItem('tax_reform_active_session', newSessionId);
        setSessionId(newSessionId);
        setMessages([]);
        
        return newSessionId;
      } catch (err) {
        console.error('Failed to create session via backend:', err);
        throw err;
      }
    };
    
    initSession();
  }, []);

  // Save recent chats to localStorage whenever they change
  useEffect(() => {
    if (recentChats.length > 0) {
      localStorage.setItem('recent_chats', JSON.stringify(recentChats));
      console.log('💾 Saved recent chats to localStorage:', recentChats.length);
    }
  }, [recentChats]);

  // Send message function
  const sendMessage = useCallback(async (message) => {
    if (!message.trim() || loading) return;

    setLoading(true);
    setError(null);

    console.log(' Sending message:', { 
      sessionId: sessionId?.substring(0, 12) + '...',
      message: truncateText(message, 50) 
    });

    //  user message added  to UI
    const userMessage = {
      id: Date.now(),
      role: 'user',
      text: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Call backend API
      const response = await api.sendMessage(sessionId, message);
      
      console.log(' Backend response:', {
        answerLength: response.answer?.length,
        citations: response.citations?.length || 0,
        route: response.route,
        refusal: response.refusal
      });

      //  assistant response to UI
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        text: response.answer,
        citations: response.citations || [],
        route: response.route || 'qa',
        refusal: response.refusal || false,
        timestamp: response.timestamp || new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update recent chats with THIS session's conversation
      updateRecentChats(message, response.answer, sessionId);

    } catch (err) {
      console.error(' Error sending message:', err);
      setError(`Failed to send message: ${err.message}`);
      
      // error message 
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        text: "Sorry, I encountered an error. Please try again or check your connection.",
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, [sessionId, loading]);

  // Update recent chats 
  const updateRecentChats = useCallback((userMessage, assistantReply, chatSessionId) => {
    //unique conversation ID
    const conversationId = `${chatSessionId}_${Date.now()}`;
    
    const newChat = {
      id: conversationId,
      title: truncateText(userMessage, 30) || 'New Message',
      preview: truncateText(assistantReply, 50) || 'AI response',
      date: new Date().toISOString(),
      sessionId: chatSessionId,
      conversationId: conversationId
    };

    setRecentChats(prev => {
      const filtered = prev.filter(chat => 
        !(chat.sessionId === chatSessionId && 
          Math.abs(new Date(chat.date).getTime() - new Date().getTime()) < 5000) 
      );
      
      const updated = [newChat, ...filtered.slice(0, 14)]; 
      
      console.log('📋 Updated recent chats:', {
        added: newChat.title,
        session: chatSessionId.substring(0, 12) + '...',
        total: updated.length,
        uniqueSessions: [...new Set(updated.map(c => c.sessionId))].length
      });
      
      return updated;
    });
  }, []);

  
  const startNewChat = useCallback(async () => {
    try {
      console.log('🔄 Starting COMPLETELY NEW chat session...');
      
      // new backend session
      const response = await api.createSession();
      const newSessionId = response.session_id;
      
      console.log(' Created NEW session:', newSessionId.substring(0, 12) + '...');
      
      
      setSessionId(newSessionId);
      localStorage.setItem('tax_reform_active_session', newSessionId);
      setMessages([]); 
      
      
      const newChat = {
        id: `${newSessionId}_${Date.now()}`,
        title: 'New Chat',
        preview: 'Started new conversation',
        date: new Date().toISOString(),
        sessionId: newSessionId,
        conversationId: `${newSessionId}_${Date.now()}`
      };
      
      setRecentChats(prev => {
        const updated = [newChat, ...prev.slice(0, 14)];
        console.log('📋 Added new chat with session:', newSessionId.substring(0, 12) + '...');
        return updated;
      });
      
      return newSessionId;
      
    } catch (err) {
      console.error('Error creating new chat:', err);
      // Fallback
      const fallbackId = `new_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(fallbackId);
      localStorage.setItem('tax_reform_active_session', fallbackId);
      setMessages([]);
      setError('Could not create new session. Using local session.');
      return fallbackId;
    }
  }, []);

  // Loading different chat session from recent chats
  const loadChat = useCallback(async (chat) => {
    try {
      console.log('📂 Loading different chat session:', {
        title: chat.title,
        sessionId: chat.sessionId?.substring(0, 12) + '...'
      });
      
      
      setSessionId(chat.sessionId);
      localStorage.setItem('tax_reform_active_session', chat.sessionId);
      
      const history = await api.getHistory(chat.sessionId);
      

      if (history.messages && history.messages.length > 0) {
        const formattedMessages = history.messages.map(msg => ({
          id: msg.id || Date.now(),
          role: msg.role,
          text: msg.text,
          timestamp: msg.timestamp,
          citations: msg.citations || [],
          route: msg.route || 'qa',
          refusal: msg.refusal || false
        }));
        setMessages(formattedMessages);
        console.log(` Loaded ${formattedMessages.length} messages for session ${chat.sessionId.substring(0, 12)}...`);
      } else {
        setMessages([]);
        console.log('No messages found for this session');
      }
      
      return true;
      
    } catch (err) {
      console.error('Error loading chat:', err);
      setError('Could not load chat history. Starting new chat instead.');
      await startNewChat();
      throw err;
    }
  }, [startNewChat]);

  // Clear all recent chats (optional utility)
  const clearRecentChats = useCallback(() => {
    setRecentChats([]);
    localStorage.removeItem('recent_chats');
    console.log(' Cleared all recent chats');
  }, []);

  return {
    messages,
    loading,
    error,
    sessionId,
    recentChats,
    sendMessage,
    startNewChat,
    loadChat,
    clearRecentChats,
    setError
  };
};


