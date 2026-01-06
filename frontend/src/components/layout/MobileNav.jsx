import React from 'react';
import { FiMenu, FiMessageSquare, FiHome } from 'react-icons/fi';

const MobileNav = ({ onMenuClick, activeView = 'chat' }) => {
  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-surface border-t border-border z-50">
      <div className="flex justify-around items-center h-14">
        {/* Menu button */}
        <button
          onClick={() => onMenuClick('menu')}
          className={`flex flex-col items-center justify-center p-2 ${activeView === 'menu' ? 'text-primary' : 'text-text-light'}`}
        >
          <FiMenu size={20} />
          <span className="text-xs mt-0.5">Menu</span>
        </button>

        {/* Home/Chat button */}
        <button
          onClick={() => onMenuClick('chat')}
          className={`flex flex-col items-center justify-center p-2 ${activeView === 'chat' ? 'text-primary' : 'text-text-light'}`}
        >
          <FiHome size={20} />
          <span className="text-xs mt-0.5">Chat</span>
        </button>

        {/* Recent Chats button */}
        <button
          onClick={() => onMenuClick('recent')}
          className={`flex flex-col items-center justify-center p-2 ${activeView === 'recent' ? 'text-primary' : 'text-text-light'}`}
        >
          <FiMessageSquare size={20} />
          <span className="text-xs mt-0.5">Recent</span>
        </button>
      </div>
    </div>
  );
};

export default MobileNav;