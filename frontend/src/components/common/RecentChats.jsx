import React from 'react';
import { FiMessageSquare, FiClock } from 'react-icons/fi';
import { formatDate } from '../../utils/helpers';

const RecentChats = ({ chats = [], onSelectChat }) => {
  if (chats.length === 0) {
    return (
      <div>
        <h3 className="font-semibold text-text mb-3">Recent Chats</h3>
        <div className="bg-gray-50 border border-dashed border-border rounded-lg p-4 text-center">
          <FiMessageSquare className="mx-auto text-gray-400 mb-2" size={24} />
          <p className="text-sm text-text-light">No recent chats</p>
          <p className="text-xs text-text-light mt-1">Start a new conversation</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="font-semibold text-text mb-3">Recent Chats</h3>
      <div className="space-y-2">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat && onSelectChat(chat)} 
            className="w-full text-left p-3 bg-surface border border-border hover:border-primary hover:shadow-sm rounded-lg transition-all group"
          >
            <div className="flex items-start gap-3">
              <div className="p-1.5 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white">
                <FiMessageSquare size={14} />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-text text-sm truncate">
                  {chat.title}
                </h4>
                <p className="text-xs text-text-light mt-0.5 truncate">
                  {chat.preview}
                </p>
                <div className="flex items-center gap-1.5 mt-2 text-xs text-text-light">
                  <FiClock size={12} />
                  <span>{formatDate(chat.date)}</span>
                </div>
                {/* Optional: Show session ID for debugging */}
                <div className="text-xs text-gray-400 mt-1 truncate">
                  ID: {chat.sessionId?.substring(0, 8)}...
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default RecentChats;
