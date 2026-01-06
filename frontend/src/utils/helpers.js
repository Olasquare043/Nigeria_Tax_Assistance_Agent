export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
};

/**
Generate session ID or get from localStorage
 */
export const getSessionId = () => {
  let sessionId = localStorage.getItem('tax_reform_session_id');
  
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('tax_reform_session_id', sessionId);
  }
  
  return sessionId;
};

/**
Show text with trailing dots
 */
export const truncateText = (text, maxLength = 100) => {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength) + '...';
};

/**
Check if we're on mobile
 */
export const isMobile = () => {
  return window.innerWidth < 768;
};