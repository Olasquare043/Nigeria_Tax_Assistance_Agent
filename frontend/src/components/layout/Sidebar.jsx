
// import React from 'react';
// import { FiMessageSquare, FiFileText, FiHelpCircle, FiInfo, FiShield } from 'react-icons/fi';
// import Button from '../ui/Button';
// import RecentChats from '../common/RecentChats';
// import QuickTopics from '../common/QuickTopics';

// const Sidebar = ({
//   recentChats = [],
//   onNewChat,
//   onSelectChat,
//   onQuickTopicSelect,
//   isMobile = false,
//   onClose,
//   onOfficialSourcesClick,
//   onDisclaimerClick, 
//   onFAQsClick 
// }) => {
//   const footerLinks = [
//     { id: 'official', label: 'Official Sources', icon: FiShield, onClick: onOfficialSourcesClick },
//     { id: 'faq', label: 'FAQs', icon: FiHelpCircle, onClick: onFAQsClick }, 
//     { id: 'disclaimer', label: 'Legal Disclaimer', icon: FiInfo, onClick: onDisclaimerClick } 
//   ];

//   return (
//     <div className={`flex flex-col h-full bg-surface ${isMobile ? 'w-full' : 'w-64 lg:w-72'}`}>
//       {/* Header with official styling */}
//       <div className="p-4 border-b border-border">
//         <div className="flex items-center justify-between">
//           <div>
//             <h2 className="text-lg font-bold text-text">Tax Reform</h2>
//             <p className="text-xs text-text-light mt-0.5">Official Q&A Assistant</p>
//           </div>
//           {isMobile && (
//             <button
//               onClick={onClose}
//               className="p-1.5 text-text-light hover:text-text hover:bg-border rounded"
//             >
//               ✕
//             </button>
//           )}
//         </div>

//         <div className="mt-4">
//           <Button
//             onClick={onNewChat}
//             variant="primary"
//             className="w-full official-button"
//             icon={FiMessageSquare}
//           >
//             Start New Inquiry
//           </Button>
//         </div>
//       </div>

//       {/* Scrollable content */}
//       <div className="flex-1 overflow-y-auto p-4 space-y-6">
//         {/* Recent Chats */}
//         <RecentChats
//           chats={recentChats}
//           onSelectChat={onSelectChat}
//         />

//         {/* Quick Topics */}
//         <QuickTopics
//           onSelectTopic={onQuickTopicSelect}
//         />
//       </div>

//       {/* Official Footer - UPDATED */}
//       <div className="border-t border-border p-4 space-y-2 bg-gray-50">
//         <div className="text-xs text-text-light mb-2">Official Resources</div>

//         {footerLinks.map((link) => (
//           <button
//             key={link.id}
//             onClick={link.onClick}
//             className="flex items-center gap-3 w-full p-2 text-text-light hover:text-text hover:bg-white rounded transition-colors text-sm"
//           >
//             <link.icon size={16} />
//             <span>{link.label}</span>
//           </button>
//         ))}

//         {/* Official Badge */}
//         <div className="pt-4 border-t border-border mt-2">
//           <div className="flex items-center justify-center gap-2 text-xs text-text-light">
//             <div className="w-2 h-2 bg-primary rounded-full"></div>
//             <span>Official Information Source</span>
//             <div className="w-2 h-2 bg-primary rounded-full"></div>
//           </div>
//           <p className="text-center text-xs text-text-light mt-1">
//             v1.0 • Ministry of Finance
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Sidebar;



import React from 'react';
import { FiMessageSquare, FiFileText, FiHelpCircle, FiInfo, FiShield, FiTrash2, FiPlus } from 'react-icons/fi';
import Button from '../ui/Button';
import RecentChats from '../common/RecentChats';
import QuickTopics from '../common/QuickTopics';

const Sidebar = ({
  recentChats = [],
  onNewChat,
  onSelectChat,
  onQuickTopicSelect,
  isMobile = false,
  onClose,
  onOfficialSourcesClick,
  onDisclaimerClick,
  onFAQsClick,
  onClearRecentChats // NEW: Add this prop from App.jsx
}) => {
  const footerLinks = [
    { id: 'official', label: 'Official Sources', icon: FiShield, onClick: onOfficialSourcesClick },
    { id: 'faq', label: 'FAQs', icon: FiHelpCircle, onClick: onFAQsClick },
    { id: 'disclaimer', label: 'Legal Disclaimer', icon: FiInfo, onClick: onDisclaimerClick }
  ];

  // Count unique sessions
  const uniqueSessions = [...new Set(recentChats.map(chat => chat.sessionId))];
  const sessionCount = uniqueSessions.length;
  const chatCount = recentChats.length;

  return (
    <div className={`flex flex-col h-full bg-surface ${isMobile ? 'w-full' : 'w-64 lg:w-72'}`}>
      {/* Header with official styling */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-text">Tax Reform 2024</h2>
            <p className="text-xs text-text-light mt-0.5">Official Q&A Assistant</p>
          </div>
          {isMobile && (
            <button
              onClick={onClose}
              className="p-1.5 text-text-light hover:text-text hover:bg-border rounded"
              aria-label="Close sidebar"
            >
              ✕
            </button>
          )}
        </div>

        <div className="mt-4">
          <Button
            onClick={onNewChat}
            variant="primary"
            className="w-full official-button"
            icon={FiPlus}
          >
            New Chat Session
          </Button>
          <p className="text-xs text-text-light mt-2 text-center">
            Starts a completely new conversation
          </p>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Session Stats */}
        {chatCount > 0 && (
          <div className="bg-gray-50 border border-border rounded-lg p-3">
            <div className="flex items-center justify-between text-sm">
              <div>
                <span className="font-medium text-text">{chatCount}</span>
                <span className="text-text-light ml-1">recent chats</span>
              </div>
              <div>
                <span className="font-medium text-text">{sessionCount}</span>
                <span className="text-text-light ml-1">session{sessionCount !== 1 ? 's' : ''}</span>
              </div>
            </div>
            {sessionCount > 1 && (
              <div className="mt-2 text-xs text-text-light">
                Click any chat to switch between conversations
              </div>
            )}
          </div>
        )}

        {/* Recent Chats */}
        <RecentChats
          chats={recentChats}
          onSelectChat={onSelectChat}
        />

        {/* Quick Topics */}
        <QuickTopics
          onSelectTopic={onQuickTopicSelect}
        />
      </div>

      {/* Management Section */}
      {chatCount > 0 && onClearRecentChats && (
        <div className="border-t border-border p-4">
          <button
            onClick={() => {
              if (window.confirm('Clear all recent chat history? This will remove the list but keep your conversations in the database.')) {
                onClearRecentChats();
              }
            }}
            className="flex items-center justify-center gap-2 w-full p-2.5 text-text-light hover:text-error hover:bg-red-50 border border-border hover:border-red-200 rounded-lg transition-colors text-sm"
          >
            <FiTrash2 size={16} />
            Clear Recent History
          </button>
          <p className="text-xs text-text-light mt-2 text-center">
            This only clears the sidebar list, not your chat data
          </p>
        </div>
      )}

      {/* Official Footer */}
      <div className="border-t border-border p-4 space-y-2 bg-gray-50">
        <div className="text-xs text-text-light mb-2">Official Resources</div>

        {footerLinks.map((link) => (
          <button
            key={link.id}
            onClick={link.onClick}
            className="flex items-center gap-3 w-full p-2 text-text-light hover:text-text hover:bg-white rounded transition-colors text-sm"
            aria-label={link.label}
          >
            <link.icon size={16} />
            <span>{link.label}</span>
          </button>
        ))}

        {/* Official Badge */}
        <div className="pt-4 border-t border-border mt-2">
          <div className="flex items-center justify-center gap-2 text-xs text-text-light">
            <div className="w-2 h-2 bg-primary rounded-full"></div>
            <span>Official Information Source</span>
            <div className="w-2 h-2 bg-primary rounded-full"></div>
          </div>
          <p className="text-center text-xs text-text-light mt-1">
            v1.0 • Ministry of Finance
          </p>
          <p className="text-center text-xs text-text-light mt-1">
            {sessionCount} active session{sessionCount !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;