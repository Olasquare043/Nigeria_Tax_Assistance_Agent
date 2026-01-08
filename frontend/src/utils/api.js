const API_BASE_URL = 'http://localhost:8000/api';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

/**
 * Fetch wrapper with error handling and auth support
 */
const fetchAPI = async (endpoint, options = {}, requireAuth = false) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if required or available
  const authToken = getAuthToken();
  if (requireAuth && authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  } else if (authToken) {
    // Optional: include token even if not required (for convenience)
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  console.log('🌐 API Call:', { 
    url, 
    method: options.method || 'GET',
    auth: !!authToken 
  });
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('🌐 API Error:', { 
        status: response.status, 
        error: errorText,
        endpoint 
      });
      
      // Handle 401 Unauthorized (token expired/invalid)
      if (response.status === 401 && authToken) {
        console.warn('⚠️ Token expired or invalid, logging out');
        localStorage.removeItem('auth_token');
        // Dispatch event for components to react
        window.dispatchEvent(new CustomEvent('auth-expired'));
      }
      
      throw new Error(`HTTP ${response.status}: ${errorText.slice(0, 100)}`);
    }

    const data = await response.json();
    console.log('🌐 API Success:', { 
      endpoint, 
      data: data ? 'received' : 'empty',
      auth: !!authToken 
    });
    return data;
    
  } catch (error) {
    console.error('🌐 Fetch error:', error);
    throw error;
  }
};

/**
 * AUTH API functions
 */
export const authAPI = {
  // Login user
  login: async (email, password) => {
    return fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  // Register new user
  register: async (userData) => {
    return fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Get current user profile (requires auth)
  getCurrentUser: async () => {
    return fetchAPI('/auth/me', {}, true);
  },

  // Update user profile (requires auth)
  updateProfile: async (profileData) => {
    return fetchAPI('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }, true);
  },

  // Change password (requires auth)
  changePassword: async (currentPassword, newPassword) => {
    return fetchAPI('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }, true);
  },

  // Request password reset
  forgotPassword: async (email) => {
    return fetchAPI('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  // Reset password with token
  resetPassword: async (token, newPassword) => {
    return fetchAPI('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({
        token,
        new_password: newPassword,
      }),
    });
  },

  // Logout (client-side cleanup)
  logout: async () => {
    // Optional: Call backend logout endpoint if you want server-side cleanup
    try {
      await fetchAPI('/auth/logout', {
        method: 'POST',
      }, true);
    } catch (error) {
      console.log('Logout API call failed (expected for JWT):', error.message);
    }
    
    // Always clear client-side token
    localStorage.removeItem('auth_token');
    return { success: true };
  },
};

/**
 * CHAT API functions
 * These work both anonymously and with authentication
 */
export const chatAPI = {
  // Send a message - works anonymously or authenticated
  sendMessage: async (sessionId, message) => {
    return fetchAPI('/chat', {
      method: 'POST',
      body: JSON.stringify({ 
        session_id: sessionId, 
        message: message 
      }),
    }, false); // Don't require auth for chat
  },

  // Get chat history for a session
  getHistory: async (sessionId) => {
    return fetchAPI(`/history/${sessionId}`);
  },

  // Create new session - works anonymously or authenticated
  createSession: async () => {
    return fetchAPI('/new-session', {
      method: 'POST',
    }, false);
  },

  // Get user's conversations (requires authentication)
  getUserConversations: async () => {
    return fetchAPI('/my-conversations', {}, true);
  },

  // Delete a conversation (requires authentication)
  deleteConversation: async (sessionId) => {
    return fetchAPI(`/conversations/${sessionId}`, {
      method: 'DELETE',
    }, true);
  },

  // Ingest documents (admin function - requires auth)
  ingestDocuments: async (forceRebuild = false) => {
    return fetchAPI('/ingest', {
      method: 'POST',
      body: JSON.stringify({ force_rebuild: forceRebuild }),
    }, true);
  },

  // Get ingest status
  getIngestStatus: async () => {
    return fetchAPI('/ingest/status');
  },

  // Health check
  getHealth: async () => {
    return fetchAPI('/health');
  },
};

// Export utility functions
export { fetchAPI, getAuthToken, API_BASE_URL };