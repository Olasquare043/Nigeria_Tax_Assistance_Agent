import React from 'react';
import { FiMenu } from 'react-icons/fi';

const Header = ({ onMenuClick }) => {
  return (
    <header className="lg:hidden sticky top-0 bg-surface border-b border-border z-40">
      <div className="px-4 h-14 flex items-center justify-between">
        <button
          onClick={onMenuClick}
          className="p-2 text-text-light hover:text-text hover:bg-border rounded-lg"
        >
          <FiMenu size={20} />
        </button>
        
        <div className="flex-1 text-center">
          <h1 className="font-bold text-text">Tax Reform  Q&A</h1>
        </div>
        
        <div className="w-10"></div> {/* Spacer for balance */}
      </div>
    </header>
  );
};

export default Header;