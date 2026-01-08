import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../utils/api'; // Import from our API module

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('auth_token') || null);
  const navigate = useNavigate();

  // Load user from token on mount
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          // Use authAPI instead of direct fetch
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Error loading user:', error);
          localStorage.removeItem('auth_token');
          setToken(null);
          setUser(null);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  // Login function
  const login = useCallback(async (email, password) => {
    try {
      const data = await authAPI.login(email, password);

      // Save token
      localStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);

      // Link anonymous chats to user
      await linkAnonymousChats();

      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Register function
  const register = useCallback(async (userData) => {
    try {
      const data = await authAPI.register(userData);

      // Auto-login after registration
      localStorage.setItem('auth_token', data.access_token);
      setToken(data.access_token);
      setUser(data.user);

      // Link anonymous chats to user
      await linkAnonymousChats();

      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.log('Logout cleanup:', error.message);
    }
    
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    navigate('/');
  }, [navigate]);

  // Link anonymous chats to user after login
  const linkAnonymousChats = useCallback(async () => {
    try {
      // Get anonymous session IDs from localStorage
      const anonymousSessionId = localStorage.getItem('tax_reform_active_session');
      const recentChats = JSON.parse(localStorage.getItem('recent_chats') || '[]');
      
      if (anonymousSessionId || recentChats.length > 0) {
        console.log('🔗 Linking anonymous chats to user account...');
        
        // Clear anonymous session ID to start fresh with user context
        localStorage.removeItem('tax_reform_active_session');
        
        console.log('✅ Anonymous chats will be linked on next chat request');
      }
    } catch (error) {
      console.error('Error linking chats:', error);
    }
  }, []);

  // Update profile
  const updateProfile = useCallback(async (profileData) => {
    try {
      const data = await authAPI.updateProfile(profileData);
      setUser(data.user);
      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Change password
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    try {
      const data = await authAPI.changePassword(currentPassword, newPassword);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Forgot password
  const forgotPassword = useCallback(async (email) => {
    try {
      const data = await authAPI.forgotPassword(email);
      return { success: true, demoToken: data.demo_token }; // demo_token is for testing
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Reset password
  const resetPassword = useCallback(async (resetToken, newPassword) => {
    try {
      const data = await authAPI.resetPassword(resetToken, newPassword);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};