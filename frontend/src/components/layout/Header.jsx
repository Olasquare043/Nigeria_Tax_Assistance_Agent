import React from 'react';
import { FiMenu, FiUser, FiLogOut } from 'react-icons/fi';
import { Link } from 'react-router-dom';

const Header = ({ onMenuClick, user, onLogout }) => {
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
          <h1 className="font-bold text-text">TAXIFY ASSISTANT Q&A</h1>
          {user && (
            <p className="text-xs text-text-light">Welcome, {user.username}</p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {user ? (
            <div className="flex items-center gap-2">
              <Link
                to="/profile"
                className="p-2 text-text-light hover:text-text hover:bg-border rounded-lg"
              >
                <FiUser size={18} />
              </Link>
              <button
                onClick={onLogout}
                className="p-2 text-text-light hover:text-red-500 hover:bg-border rounded-lg"
                title="Logout"
              >
                <FiLogOut size={18} />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="text-sm text-primary hover:underline px-2"
            >
              Login
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;