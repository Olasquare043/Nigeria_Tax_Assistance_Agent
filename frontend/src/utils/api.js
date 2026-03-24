const API_ROOT_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const API_BASE_URL = `${API_ROOT_URL}/api`;

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('auth_token');
};

const parseJSONSafely = (value) => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

const buildErrorMessage = (status, payload, rawText) => {
  if (payload && typeof payload === 'object') {
    const parts = [];

    if (typeof payload.message === 'string' && payload.message.trim()) {
      parts.push(payload.message.trim());
    }

    if (
      typeof payload.detail === 'string' &&
      payload.detail.trim() &&
      payload.detail.trim() !== payload.message?.trim()
    ) {
      parts.push(payload.detail.trim());
    }

    if (parts.length > 0) {
      return parts.join('. ');
    }
  }

  if (typeof rawText === 'string' && rawText.trim()) {
    return rawText.trim();
  }

  return `Request failed with status ${status}.`;
};

/**
 * Fetch wrapper with error handling and auth support
 */
const fetchAPI = async (
  endpoint,
  options = {},
  requireAuth = false,
  useApiPrefix = true
) => {
  const baseUrl = useApiPrefix ? API_BASE_URL : API_ROOT_URL;
  const url = `${baseUrl}${endpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if required or available
  const authToken = getAuthToken();
  if (requireAuth && authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  } else if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  console.log('API Call:', {
    url,
    method: options.method || 'GET',
    auth: !!authToken,
  });

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorText = await response.text();
      const errorPayload = parseJSONSafely(errorText);

      console.error('API Error:', {
        status: response.status,
        error: errorPayload || errorText,
        endpoint,
      });

      // Handle 401 Unauthorized (token expired/invalid)
      if (response.status === 401 && authToken) {
        console.warn('Token expired or invalid, logging out');
        localStorage.removeItem('auth_token');
        window.dispatchEvent(new CustomEvent('auth-expired'));
      }

      const apiError = new Error(
        buildErrorMessage(response.status, errorPayload, errorText)
      );
      apiError.status = response.status;
      apiError.payload = errorPayload;
      apiError.code = errorPayload?.code || errorPayload?.error || null;
      apiError.detail = errorPayload?.detail || null;

      throw apiError;
    }

    const data = await response.json();
    console.log('API Success:', {
      endpoint,
      data: data ? 'received' : 'empty',
      auth: !!authToken,
    });
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
};

/**
 * AUTH API functions
 */
export const authAPI = {
  login: async (email, password) => {
    return fetchAPI('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register: async (userData) => {
    return fetchAPI('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  getCurrentUser: async () => {
    return fetchAPI('/auth/me', {}, true);
  },

  updateProfile: async (profileData) => {
    return fetchAPI('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    }, true);
  },

  changePassword: async (currentPassword, newPassword) => {
    return fetchAPI('/auth/change-password', {
      method: 'PUT',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }, true);
  },

  forgotPassword: async (email) => {
    return fetchAPI('/auth/forgot-password', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  resetPassword: async (token, newPassword) => {
    return fetchAPI('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify({
        token,
        new_password: newPassword,
      }),
    });
  },

  logout: async () => {
    try {
      await fetchAPI('/auth/logout', {
        method: 'POST',
      }, true);
    } catch (error) {
      console.log('Logout API call failed (expected for JWT):', error.message);
    }

    localStorage.removeItem('auth_token');
    return { success: true };
  },
};

/**
 * CHAT API functions
 * These work both anonymously and with authentication
 */
export const chatAPI = {
  sendMessage: async (sessionId, message) => {
    return fetchAPI('/chat', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        message,
      }),
    }, false);
  },

  getHistory: async (sessionId) => {
    return fetchAPI(`/history/${sessionId}`);
  },

  createSession: async () => {
    return fetchAPI('/new-session', {
      method: 'POST',
    }, false);
  },

  getUserConversations: async () => {
    return fetchAPI('/my-conversations', {}, true);
  },

  deleteConversation: async (sessionId) => {
    return fetchAPI(`/conversations/${sessionId}`, {
      method: 'DELETE',
    }, true);
  },

  ingestDocuments: async (forceRebuild = false) => {
    return fetchAPI('/ingest', {
      method: 'POST',
      body: JSON.stringify({ force_rebuild: forceRebuild }),
    }, true);
  },

  getIngestStatus: async () => {
    return fetchAPI('/ingest/status');
  },

  getHealth: async () => {
    return fetchAPI('/health', {}, false, false);
  },
};

export { fetchAPI, getAuthToken, API_BASE_URL, API_ROOT_URL };
