import React from 'react';
import { FiUser, FiFileText, FiAlertCircle, FiMessageSquare } from 'react-icons/fi';
import { formatDate } from '../../utils/helpers';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 ${isUser ? 'order-2' : 'order-1'}`}>
        <div className={`w-8 h-8 rounded-md flex items-center justify-center ${isUser ? 'bg-primary text-white' : 'bg-secondary text-white'}`}>
          {isUser ? <FiUser size={18} /> : <FiFileText size={18} />}
        </div>
      </div>
      
      {/* Message Bubble */}
      <div className={`flex-1 ${isUser ? 'order-1 text-right' : 'order-2'}`}>
        <div className={`inline-block max-w-[85%] lg:max-w-[70%] rounded-lg px-4 py-3 professional-card ${isUser ? 'bg-primary text-white' : 'bg-surface'}`}>
          <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
        </div>
        
        {/* Timestamp */}
        <div className={`mt-1.5 text-xs text-text-light ${isUser ? 'text-right' : 'text-left'}`}>
          {formatDate(message.timestamp)}
        </div>
        
        {/* Route Indicator (for assistant messages) */}
        {!isUser && message.route && message.route !== "qa" && (
          <div className="mt-2 text-left">
            <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full border border-gray-300">
              {message.route === "clarify" && "🤔 Seeking Clarification"}
              {message.route === "compare" && "📊 Comparison Mode"}
              {message.route === "claim_check" && "🔍 Fact Checking"}
              {message.route === "smalltalk" && "💬 General Chat"}
              {message.route === "qa" && "❓ Q&A"}
              {!["clarify", "compare", "claim_check", "smalltalk", "qa"].includes(message.route) && 
                `Mode: ${message.route}`}
            </span>
          </div>
        )}
        
        {/* Refusal Warning */}
        {!isUser && message.refusal && (
          <div className="mt-3 text-left">
            <div className="flex items-start gap-2 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded-r">
              <FiAlertCircle className="text-yellow-500 mt-0.5 flex-shrink-0" size={16} />
              <div className="flex-1">
                <p className="text-sm text-yellow-800 font-medium">
                  Limited Response
                </p>
                <p className="text-xs text-yellow-700 mt-0.5">
                  This query may be outside the scope of Nigerian tax reform topics.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Citations (for assistant messages) */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="text-xs font-medium text-text-light uppercase tracking-wider flex items-center gap-2">
              <FiFileText size={12} />
              Reference Sources
            </div>
            <div className="space-y-2">
              {message.citations.map((source, index) => (
                <div 
                  key={index} 
                  className="citation-item"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-semibold text-primary text-sm">
                        {source.source || "Document"}
                      </div>
                      {source.pages && source.pages !== "p.?" && (
                        <div className="text-text-light text-xs mt-0.5">
                          Pages: {source.pages}
                        </div>
                      )}
                    </div>
                    {source.chunk_id && (
                      <div className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
                        ID: {source.chunk_id.substring(0, 8)}...
                      </div>
                    )}
                  </div>
                  
                  {source.quote && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-text text-sm italic leading-snug">
                        "{source.quote}"
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Error State */}
        {message.isError && (
          <div className="mt-3 text-left">
            <div className="flex items-start gap-2 p-3 bg-red-50 border-l-4 border-red-400 rounded-r">
              <FiAlertCircle className="text-red-500 mt-0.5 flex-shrink-0" size={16} />
              <div className="flex-1">
                <p className="text-sm text-red-800">
                  {message.text}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;