const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Fetch wrapper with error handling
 */
const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  console.log('🌐 API Call:', { url, method: options.method || 'GET' });
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('🌐 API Error:', { status: response.status, error: errorText });
      throw new Error(`HTTP ${response.status}: ${errorText.slice(0, 100)}`);
    }

    const data = await response.json();
    console.log('🌐 API Success:', { endpoint, data: data ? 'received' : 'empty' });
    return data;
    
  } catch (error) {
    console.error('🌐 Fetch error:', error);
    throw error;
  }
};

/**
 * Chat API functions - UPDATED FOR NEW BACKEND STRUCTURE
 */
const chatAPI = {
  // Send a message - RETURNS {answer, session_id, citations, route, refusal, timestamp}
  sendMessage: async (sessionId, message) => {
    return fetchAPI('/chat', {
      method: 'POST',
      body: JSON.stringify({ 
        session_id: sessionId, 
        message: message 
      }),
    });
  },

  // Get chat history
  getHistory: async (sessionId) => {
    return fetchAPI(`/history/${sessionId}`);
  },

  // Create new session
  createSession: async () => {
    return fetchAPI('/new-session', {
      method: 'POST',
    });
  },

  // NEW: Ingest documents (admin function)
  ingestDocuments: async (forceRebuild = false) => {
    return fetchAPI('/ingest', {
      method: 'POST',
      body: JSON.stringify({ force_rebuild: forceRebuild }),
    });
  },

  // NEW: Get ingest status
  getIngestStatus: async () => {
    return fetchAPI('/ingest/status');
  },
};

/**
 * Mock API for testing (when backend is not ready)
 */
const mockAPI = {
  sendMessage: async (sessionId, message) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const responses = {
      'vat': {
        answer: "The 2024 Tax Reform Bill proposes a VAT increase from 7.5% to 10%, with improved revenue sharing formula. 85% of VAT goes to states and local governments, while 15% goes to the Federal Government.",
        citations: [
          { 
            chunk_id: "vat_001", 
            source: "2024 Finance Bill", 
            pages: "p.15-18", 
            quote: "Value added tax rate shall be increased to 10% effective July 2024." 
          },
          { 
            chunk_id: "vat_002", 
            source: "Revenue Sharing Formula", 
            pages: "Annex 2, p.5", 
            quote: "85% of VAT revenue allocated to states and local governments." 
          }
        ],
        route: "qa",
        refusal: false
      },
      'business': {
        answer: "Small businesses with annual turnover below ₦25 million are exempt from Company Income Tax. The reform introduces a simplified tax filing process for SMEs.",
        citations: [
          { 
            chunk_id: "sme_001", 
            source: "Small Business Tax Exemption", 
            pages: "Section 12(3), p.22", 
            quote: "Enterprises with annual turnover under ₦25 million exempt from CIT." 
          }
        ],
        route: "qa",
        refusal: false
      },
      'default': {
        answer: "I can help you understand the 2024 Nigerian Tax Reform Bills. Please ask specific questions about VAT changes, small business impacts, implementation timeline, or state revenue sharing.",
        citations: [],
        route: "clarify",
        refusal: false
      }
    };

    const lowerMsg = message.toLowerCase();
    let response;
    
    if (lowerMsg.includes('vat') || lowerMsg.includes('value added')) {
      response = responses.vat;
    } else if (lowerMsg.includes('business') || lowerMsg.includes('sme') || lowerMsg.includes('small')) {
      response = responses.business;
    } else {
      response = responses.default;
    }

    return {
      answer: response.answer,
      session_id: sessionId,
      citations: response.citations,
      route: response.route,
      refusal: response.refusal,
      timestamp: new Date().toISOString()
    };
  },
  
  getHistory: async (sessionId) => {
    return { 
      session_id: sessionId, 
      messages: [] 
    };
  },
  
  createSession: async () => {
    return { 
      session_id: `mock_${Date.now()}`, 
      message: "Mock session created",
      conversation_id: 999
    };
  }
};

export { chatAPI, mockAPI };