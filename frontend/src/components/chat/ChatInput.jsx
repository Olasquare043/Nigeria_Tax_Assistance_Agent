
import React, { useState, useRef } from 'react';
import { FiSend, FiPaperclip } from 'react-icons/fi';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';

const ChatInput = ({ onSend, loading = false, disabled = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !loading && !disabled) {
      onSend(message);
      setMessage('');
      
      
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e) => {
    setMessage(e.target.value);
    
    
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-border pt-4">
      <div className="flex gap-2 items-end">
        {/* Attach button (placeholder for future features) */}
        <button
          type="button"
          disabled={disabled}
          className="p-2.5 text-text-light hover:text-primary hover:bg-primary/5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Attach file (coming soon)"
        >
          <FiPaperclip size={20} />
        </button>
        
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about tax reforms..."
            disabled={disabled || loading}
            rows={1}
      
            className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 pr-12 bg-white text-gray-900 placeholder:text-gray-500 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            style={{ 
              minHeight: '44px', 
              maxHeight: '120px',
              // Fallback:
              color: '#000000',
              backgroundColor: '#ffffff'
            }}
          />
          
          {/* Character count */}
          {message.length > 100 && (
            <div className="absolute bottom-2 right-12 text-xs text-text-light">
              {message.length}/500
            </div>
          )}
        </div>
        
        {/* Send button */}
        <Button
          type="submit"
          disabled={!message.trim() || loading || disabled}
          className="px-4 py-3"
        >
          {loading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <FiSend size={18} />
          )}
        </Button>
      </div>
      
      {/* Helper text */}
      <div className="mt-2 text-xs text-text-light text-center">
        Press Enter to send • Shift+Enter for new line
      </div>
    </form>
  );
};

export default ChatInput;
