// import React from 'react';
// import { FiMessageSquare, FiClock, FiHash } from 'react-icons/fi';
// import { formatDate } from '../../utils/helpers';

// const RecentChats = ({ chats = [], onSelectChat }) => {
//   if (chats.length === 0) {
//     return (
//       <div>
//         <h3 className="font-semibold text-text mb-3">Recent Conversations</h3>
//         <div className="bg-gray-50 border border-dashed border-border rounded-lg p-4 text-center">
//           <FiMessageSquare className="mx-auto text-gray-400 mb-2" size={24} />
//           <p className="text-sm text-text-light">No recent conversations</p>
//           <p className="text-xs text-text-light mt-1">Start a new chat to see it here</p>
//         </div>
//       </div>
//     );
//   }

//   // Group by session for debugging
//   const uniqueSessions = [...new Set(chats.map(chat => chat.sessionId))];
//   console.log(' RecentChats:', {
//     total: chats.length,
//     uniqueSessions: uniqueSessions.length,
//     sessions: uniqueSessions.map(s => s.substring(0, 8) + '...')
//   });

//   return (
//     <div>
//       <div className="flex items-center justify-between mb-3">
//         <h3 className="font-semibold text-text">Recent Conversations</h3>
//         <span className="text-xs text-text-light bg-gray-100 px-2 py-1 rounded">
//           {uniqueSessions.length} session{uniqueSessions.length !== 1 ? 's' : ''}
//         </span>
//       </div>
      
//       <div className="space-y-2">
//         {chats.map((chat) => (
//           <button
//             key={chat.id}
//             onClick={() => onSelectChat && onSelectChat(chat)}
//             className="w-full text-left p-3 bg-surface border border-border hover:border-primary hover:shadow-sm rounded-lg transition-all group"
//             title={`Click to load this conversation (Session: ${chat.sessionId?.substring(0, 8)}...)`}
//           >
//             <div className="flex items-start gap-3">
//               <div className="p-1.5 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white">
//                 <FiMessageSquare size={14} />
//               </div>
//               <div className="flex-1 min-w-0">
//                 <div className="flex items-start justify-between">
//                   <h4 className="font-medium text-text text-sm truncate">
//                     {chat.title}
//                   </h4>
//                   {chat.isActive && (
//                     <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">
//                       Active
//                     </span>
//                   )}
//                 </div>
//                 <p className="text-xs text-text-light mt-0.5 truncate">
//                   {chat.preview}
//                 </p>
                
//                 <div className="flex items-center gap-2 mt-2 text-xs text-text-light">
//                   <div className="flex items-center gap-1">
//                     <FiClock size={10} />
//                     <span>{formatDate(chat.date)}</span>
//                   </div>
                  
//                   <span className="text-gray-300">•</span>
                  
//                   <div className="flex items-center gap-1" title={`Session ID: ${chat.sessionId}`}>
//                     <FiHash size={10} />
//                     <span className="truncate max-w-[80px]">
//                       {chat.sessionId?.substring(0, 8)}...
//                     </span>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           </button>
//         ))}
//       </div>
      
//       {/* Debug info (remove in production) */}
//       {process.env.NODE_ENV === 'development' && (
//         <div className="mt-3 pt-3 border-t border-border text-xs text-gray-500">
//           <div>Debug: {chats.length} total, {uniqueSessions.length} unique sessions</div>
//           <div className="truncate">
//             Sessions: {uniqueSessions.map(s => s.substring(0, 8)).join(', ')}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default RecentChats;


import React, { useState } from 'react';
import { FiMessageSquare, FiClock, FiHash, FiTrash2, FiAlertTriangle } from 'react-icons/fi';
import { formatDate } from '../../utils/helpers';

const RecentChats = ({ chats = [], onSelectChat, onClearChats }) => {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  // Debug log to check props
  console.log('RecentChats props:', {
    chatCount: chats.length,
    hasClearFunction: !!onClearChats,
    clearFunction: onClearChats
  });

  if (chats.length === 0) {
    return (
      <div>
        <h3 className="font-semibold text-text mb-3">Recent Conversations</h3>
        <div className="bg-gray-50 border border-dashed border-border rounded-lg p-4 text-center">
          <FiMessageSquare className="mx-auto text-gray-400 mb-2" size={24} />
          <p className="text-sm text-text-light">No recent conversations</p>
          <p className="text-xs text-text-light mt-1">Start a new chat to see it here</p>
        </div>
      </div>
    );
  }

  const handleClearAll = async () => {
    if (!onClearChats) {
      console.error('❌ onClearChats function not provided!');
      alert('Clear functionality is not available');
      return;
    }

    console.log('🔄 Clearing all recent chats...');
    setIsClearing(true);
    
    try {
      // Call the parent function to clear chats
      await onClearChats();
      setShowConfirm(false);
      console.log('✅ All recent chats cleared successfully');
    } catch (error) {
      console.error('❌ Failed to clear chats:', error);
      alert('Failed to clear chats. Please try again.');
    } finally {
      setIsClearing(false);
    }
  };

  // Group by session
  const uniqueSessions = [...new Set(chats.map(chat => chat.sessionId))];

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-text">Recent Conversations</h3>
          <span className="text-xs text-text-light bg-gray-100 px-2 py-1 rounded">
            {chats.length} chat{chats.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        {/* Only show Clear All button if onClearChats is provided */}
        {onClearChats && (
          <button
            onClick={() => setShowConfirm(true)}
            className="text-sm text-red-500 hover:text-red-700 hover:bg-red-50 px-3 py-1 rounded-md transition-colors flex items-center gap-2 border border-red-200"
            title="Clear all conversations from list"
            aria-label="Clear all recent chats"
          >
            <FiTrash2 size={14} />
            <span>Clear All</span>
          </button>
        )}
      </div>
      
      <div className="space-y-2">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => {
              console.log('📱 Selecting chat:', { 
                id: chat.id, 
                title: chat.title,
                sessionId: chat.sessionId?.substring(0, 8) 
              });
              onSelectChat && onSelectChat(chat);
            }}
            className="w-full text-left p-3 bg-surface border border-border hover:border-primary hover:shadow-sm rounded-lg transition-all group"
            title={`Click to load: ${chat.title} (Session: ${chat.sessionId?.substring(0, 8)}...)`}
          >
            <div className="flex items-start gap-3">
              <div className="p-1.5 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white">
                <FiMessageSquare size={14} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <h4 className="font-medium text-text text-sm truncate">
                    {chat.title}
                  </h4>
                  {chat.isActive && (
                    <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">
                      Active
                    </span>
                  )}
                </div>
                <p className="text-xs text-text-light mt-0.5 truncate">
                  {chat.preview}
                </p>
                
                <div className="flex items-center gap-2 mt-2 text-xs text-text-light">
                  <div className="flex items-center gap-1">
                    <FiClock size={10} />
                    <span>{formatDate(chat.date)}</span>
                  </div>
                  
                  <span className="text-gray-300">•</span>
                  
                  <div className="flex items-center gap-1" title={`Session ID: ${chat.sessionId}`}>
                    <FiHash size={10} />
                    <span className="truncate max-w-[80px]">
                      {chat.sessionId?.substring(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
      
      {/* Confirmation Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-full bg-red-100 text-red-600">
                <FiAlertTriangle size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">Clear Recent Chats</h3>
                <p className="text-sm text-gray-600 mt-1">
                  This will remove {chats.length} chat{chats.length !== 1 ? 's' : ''} from your recent list.
                </p>
              </div>
            </div>
            
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> This only clears the recent chats list from the sidebar. 
                Your chat history is still saved in the database and can be accessed by starting a new chat session.
              </p>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                disabled={isClearing}
              >
                Cancel
              </button>
              <button
                onClick={handleClearAll}
                disabled={isClearing}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isClearing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Clearing...
                  </>
                ) : (
                  <>
                    <FiTrash2 size={14} />
                    Clear All
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Debug info - Remove in production */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-3 pt-3 border-t border-border text-xs text-gray-500">
          <div>Debug: {chats.length} chats, {uniqueSessions.length} unique sessions</div>
          <div className="truncate">
            Has clear function: {onClearChats ? 'Yes' : 'No'}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecentChats;