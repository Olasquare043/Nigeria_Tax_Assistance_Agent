
import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import WelcomeMessage from './WelcomeMessage';
import ErrorDisplay from '../ui/ErrorDisplay';

const ChatWindow = ({ 
  messages = [], 
  onSend, 
  loading = false, 
  error = null,
  onErrorDismiss,
  onQuickTopicSelect
}) => {
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Show welcome message if no messages
  const showWelcome = messages.length === 0;

  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div className="border-b border-border px-6 py-4">
        <h1 className="text-xl font-bold text-text"> TAXIFY AI ASSISTANT Q&A</h1>
        <p className="text-sm text-text-light mt-1">Get clear answers about Nigeria's new tax laws</p>
      </div>

      {/* Messages container */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-y-auto px-4 lg:px-6 py-4"
      >
        {error && (
          <div className="mb-4">
            <ErrorDisplay error={error} onDismiss={onErrorDismiss} />
          </div>
        )}

        {showWelcome ? (
          <WelcomeMessage onQuickTopicSelect={onQuickTopicSelect} />
        ) : (
          <div className="space-y-1">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {loading && (
              <div className="flex justify-start mb-6">
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  </div>
                  <div className="bg-surface border border-border rounded-2xl rounded-tl-none px-4 py-3">
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse delay-150"></div>
                      <div className="w-2 h-2 bg-gray-300 rounded-full animate-pulse delay-300"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-border px-4 lg:px-6 py-4">
        <ChatInput onSend={onSend} loading={loading} disabled={!!error} />
      </div>
    </div>
  );
};

export default ChatWindow;
