
import React from 'react';
import { FiMessageSquare, FiFileText, FiHelpCircle, FiInfo, FiShield } from 'react-icons/fi';
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
  onFAQsClick 
}) => {
  const footerLinks = [
    { id: 'official', label: 'Official Sources', icon: FiShield, onClick: onOfficialSourcesClick },
    { id: 'faq', label: 'FAQs', icon: FiHelpCircle, onClick: onFAQsClick }, 
    { id: 'disclaimer', label: 'Legal Disclaimer', icon: FiInfo, onClick: onDisclaimerClick } 
  ];

  return (
    <div className={`flex flex-col h-full bg-surface ${isMobile ? 'w-full' : 'w-64 lg:w-72'}`}>
      {/* Header with official styling */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-text">Tax Reform</h2>
            <p className="text-xs text-text-light mt-0.5">Official Q&A Assistant</p>
          </div>
          {isMobile && (
            <button
              onClick={onClose}
              className="p-1.5 text-text-light hover:text-text hover:bg-border rounded"
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
            icon={FiMessageSquare}
          >
            Start New Inquiry
          </Button>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
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

      {/* Official Footer - UPDATED */}
      <div className="border-t border-border p-4 space-y-2 bg-gray-50">
        <div className="text-xs text-text-light mb-2">Official Resources</div>

        {footerLinks.map((link) => (
          <button
            key={link.id}
            onClick={link.onClick}
            className="flex items-center gap-3 w-full p-2 text-text-light hover:text-text hover:bg-white rounded transition-colors text-sm"
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
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
