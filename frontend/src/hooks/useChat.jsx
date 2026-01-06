import { useState, useEffect, useCallback } from 'react';
import { chatAPI, mockAPI } from '../utils/api';
import { truncateText } from '../utils/helpers';

// Use real API since backend is ready with AI engine
const USE_MOCK_API = false; // Set to false to use real backend
const api = USE_MOCK_API ? mockAPI : chatAPI;

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
        
        // 1. Try to get existing session from localStorage
        let existingSessionId = localStorage.getItem('tax_reform_session_id');
        
        if (existingSessionId) {
          console.log('📂 Found existing session:', existingSessionId.substring(0, 12) + '...');
          
          // Verify session exists in backend
          try {
            const history = await api.getHistory(existingSessionId);
            console.log('✅ Session exists in backend');
            
            // Set session ID
            setSessionId(existingSessionId);
            
            // Load messages from backend
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
              console.log(`📜 Loaded ${formattedMessages.length} messages from history`);
            }
            
          } catch (historyError) {
            console.log('❌ Session not found in backend, creating new:', historyError.message);
            await createNewSession();
          }
        } else {
          // No session in localStorage, create new one
          console.log('🆕 No existing session, creating new...');
          await createNewSession();
        }
        
        // Load recent chats from localStorage
        const savedChats = localStorage.getItem('recent_chats');
        if (savedChats) {
          setRecentChats(JSON.parse(savedChats));
        }
        
      } catch (err) {
        console.error('❌ Error initializing session:', err);
        // Fallback to local session ID
        const fallbackId = `fallback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('tax_reform_session_id', fallbackId);
        setSessionId(fallbackId);
      }
    };
    
    const createNewSession = async () => {
      try {
        console.log('📞 Calling backend to create new session...');
        const response = await api.createSession();
        const newSessionId = response.session_id;
        
        console.log('✅ Backend created session:', newSessionId.substring(0, 12) + '...');
        
        // Save to localStorage and state
        localStorage.setItem('tax_reform_session_id', newSessionId);
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

  // Save recent chats to localStorage
  useEffect(() => {
    if (recentChats.length > 0) {
      localStorage.setItem('recent_chats', JSON.stringify(recentChats));
    }
  }, [recentChats]);

  // Send message function - UPDATED FOR NEW RESPONSE STRUCTURE
  const sendMessage = useCallback(async (message) => {
    if (!message.trim() || loading) return;

    setLoading(true);
    setError(null);

    console.log('📱 Sending message:', { 
      sessionId: sessionId?.substring(0, 12) + '...',
      message: truncateText(message, 50) 
    });

    // Add user message immediately to UI
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
      
      console.log('✅ Backend response:', {
        answerLength: response.answer?.length,
        citations: response.citations?.length || 0,
        route: response.route,
        refusal: response.refusal
      });

      // Add assistant response to UI - UPDATED FIELDS
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        text: response.answer, // CHANGED: was response.reply
        citations: response.citations || [],
        route: response.route || 'qa', // NEW FIELD
        refusal: response.refusal || false, // NEW FIELD
        timestamp: response.timestamp || new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update recent chats
      updateRecentChats(message, response.answer);

    } catch (err) {
      console.error('❌ Error sending message:', err);
      setError(`Failed to send message: ${err.message}`);
      
      // Add error message to chat
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
  const updateRecentChats = (userMessage, assistantReply) => {
    const newChat = {
      id: Date.now(),
      title: truncateText(userMessage, 30),
      preview: truncateText(assistantReply, 50),
      date: new Date().toISOString(),
      sessionId: sessionId
    };

    setRecentChats(prev => {
      const updated = [newChat, ...prev.slice(0, 4)];
      console.log('📋 Updated recent chats:', updated.length, 'chats');
      return updated;
    });
  };

  // Start new chat
  const startNewChat = async () => {
    try {
      console.log('🔄 Starting new chat session...');
      
      const response = await api.createSession();
      const newSessionId = response.session_id;
      
      console.log('✅ New session created:', newSessionId.substring(0, 12) + '...');
      
      setSessionId(newSessionId);
      localStorage.setItem('tax_reform_session_id', newSessionId);
      setMessages([]);
      
      const newChat = {
        id: Date.now(),
        title: 'New Chat',
        preview: 'Started new conversation',
        date: new Date().toISOString(),
        sessionId: newSessionId
      };
      
      setRecentChats(prev => [newChat, ...prev.slice(0, 4)]);
      
    } catch (err) {
      console.error('Error creating new chat:', err);
      const fallbackId = `new_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setSessionId(fallbackId);
      localStorage.setItem('tax_reform_session_id', fallbackId);
      setMessages([]);
      setError('Could not create new session. Using local session.');
    }
  };

  // Load a specific chat from recent chats
  const loadChat = async (chat) => {
    try {
      console.log('📂 Loading chat:', chat.title);
      
      setSessionId(chat.sessionId);
      localStorage.setItem('tax_reform_session_id', chat.sessionId);
      
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
        console.log(`📜 Loaded ${formattedMessages.length} messages`);
      } else {
        setMessages([]);
        console.log('No messages found for this session');
      }
      
    } catch (err) {
      console.error('Error loading chat:', err);
      setError('Could not load chat history. Starting new chat.');
      startNewChat();
    }
  };

  return {
    messages,
    loading,
    error,
    sessionId,
    recentChats,
    sendMessage,
    startNewChat,
    loadChat,
    setError
  };
};