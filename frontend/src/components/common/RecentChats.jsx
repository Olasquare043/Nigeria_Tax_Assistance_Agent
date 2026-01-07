// import React from 'react';
// import { FiMessageSquare, FiClock } from 'react-icons/fi';
// import { formatDate } from '../../utils/helpers';

// const RecentChats = ({ chats = [], onSelectChat }) => {
//   // Add this to RecentChats component for debugging:
//   const handleClick = (chat) => {
//     console.log('🖱️ RecentChats onClick:', chat);
//     if (onSelectChat) {
//       onSelectChat(chat);
//     } else {
//       console.error('❌ onSelectChat prop is undefined!');
//     }
//   };

//   if (chats.length === 0) {
//     return (
//       <div>
//         <h3 className="font-semibold text-text mb-3">Recent Chats</h3>
//         <div className="bg-gray-50 border border-dashed border-border rounded-lg p-4 text-center">
//           <FiMessageSquare className="mx-auto text-gray-400 mb-2" size={24} />
//           <p className="text-sm text-text-light">No recent chats</p>
//           <p className="text-xs text-text-light mt-1">Start a new conversation</p>
//         </div>
//       </div>
//     );
//   }

//   return (
//     <div>
//       <h3 className="font-semibold text-text mb-3">Recent Chats</h3>
//       <div className="space-y-2">
//         {chats.map((chat) => (
//           <button
//             key={chat.id}
//             onClick={() => handleClick(chat)}
//             className="w-full text-left p-3 bg-surface border border-border hover:border-primary hover:shadow-sm rounded-lg transition-all group"
//           >
//             <div className="flex items-start gap-3">
//               <div className="p-1.5 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white">
//                 <FiMessageSquare size={14} />
//               </div>
//               <div className="flex-1 min-w-0">
//                 <h4 className="font-medium text-text text-sm truncate">
//                   {chat.title}
//                 </h4>
//                 <p className="text-xs text-text-light mt-0.5 truncate">
//                   {chat.preview}
//                 </p>
//                 <div className="flex items-center gap-1.5 mt-2 text-xs text-text-light">
//                   <FiClock size={12} />
//                   <span>{formatDate(chat.date)}</span>
//                 </div>
//                 {/* Optional: Show session ID for debugging */}
//                 <div className="text-xs text-gray-400 mt-1 truncate">
//                   ID: {chat.sessionId?.substring(0, 8)}...
//                 </div>
//               </div>
//             </div>
//           </button>
//         ))}
//       </div>
//     </div>
//   );
// };

// export default RecentChats;



import React from 'react';
import { FiMessageSquare, FiClock, FiHash } from 'react-icons/fi';
import { formatDate } from '../../utils/helpers';

const RecentChats = ({ chats = [], onSelectChat }) => {
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

  // Group by session for debugging
  const uniqueSessions = [...new Set(chats.map(chat => chat.sessionId))];
  console.log('📊 RecentChats:', {
    total: chats.length,
    uniqueSessions: uniqueSessions.length,
    sessions: uniqueSessions.map(s => s.substring(0, 8) + '...')
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-text">Recent Conversations</h3>
        <span className="text-xs text-text-light bg-gray-100 px-2 py-1 rounded">
          {uniqueSessions.length} session{uniqueSessions.length !== 1 ? 's' : ''}
        </span>
      </div>
      
      <div className="space-y-2">
        {chats.map((chat) => (
          <button
            key={chat.id}
            onClick={() => onSelectChat && onSelectChat(chat)}
            className="w-full text-left p-3 bg-surface border border-border hover:border-primary hover:shadow-sm rounded-lg transition-all group"
            title={`Click to load this conversation (Session: ${chat.sessionId?.substring(0, 8)}...)`}
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
      
      {/* Debug info (remove in production) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-3 pt-3 border-t border-border text-xs text-gray-500">
          <div>Debug: {chats.length} total, {uniqueSessions.length} unique sessions</div>
          <div className="truncate">
            Sessions: {uniqueSessions.map(s => s.substring(0, 8)).join(', ')}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecentChats;