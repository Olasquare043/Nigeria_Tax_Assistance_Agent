
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import Sidebar from '../components/layout/Sidebar';
import ChatWindow from '../components/chat/ChatWindow';
import Header from '../components/layout/Header';
import MobileNav from '../components/layout/MobileNav';
import ErrorDisplay from '../components/ui/ErrorDisplay';
import OfficialSourcesModal from '../components/ui/OfficialSourcesModal';
import LegalDisclaimerModal from '../components/ui/LegalDisclaimerModal';
import FAQsModal from '../components/ui/FAQsModal';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const {
    messages,
    loading,
    error,
    sessionId,
    recentChats,
    sendMessage,
    startNewChat,
    loadChat,
    clearRecentChats, 
    setError
  } = useChat(); 

  const { user, logout } = useAuth();
  const navigate = useNavigate();

 ent
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [mobileView, setMobileView] = useState('chat');

  const [showOfficialModal, setShowOfficialModal] = useState(false);
  const [showDisclaimerModal, setShowDisclaimerModal] = useState(false);
  const [showFAQsModal, setShowFAQsModal] = useState(false);

  
  useEffect(() => {
    console.log('🔍 Dashboard State - User:', user?.email);
    console.log('🔍 Dashboard State - Session ID:', sessionId);
    console.log('🔍 Dashboard State - Message count:', messages.length);
    console.log('🔍 Dashboard State - Recent chats:', recentChats.length);
    console.log('🔍 Dashboard State - Has clear function:', !!clearRecentChats);
  }, [user, sessionId, messages, recentChats, clearRecentChats]);

  // Close sidebar on desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsSidebarOpen(false);
        setMobileView('chat');
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Initial check

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle sending messages
  const handleSendMessage = async (message) => {
    await sendMessage(message);
  };

  // Handle loading a specific chat from recent chats
  const handleSelectChat = async (chat) => {
    if (chat && chat.sessionId) {
      console.log('📂 Loading chat from recent:', chat.title);
      try {
        await loadChat(chat);

        if (window.innerWidth < 1024) {
          setIsSidebarOpen(false);
          setMobileView('chat');
        }
      } catch (err) {
        console.error('Error loading chat:', err);
        setError('Could not load chat. Starting new chat instead.');
        startNewChat();
      }
    }
  };


  const handleQuickTopicSelect = (question) => {
    handleSendMessage(question);
    if (window.innerWidth < 1024) {
      setIsSidebarOpen(false);
      setMobileView('chat');
    }
  };

  // Handle mobile navigation
  const handleMobileNavClick = (view) => {
    setMobileView(view);
    if (view === 'menu') {
      setIsSidebarOpen(true);
    } else {
      setIsSidebarOpen(false);
    }
  };

  // Handle logout
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Determine what to show based on mobile view
  const showSidebar = window.innerWidth >= 1024 || isSidebarOpen;
  const showChat = window.innerWidth >= 1024 || mobileView === 'chat';

  return (
    <div className="h-screen bg-background overflow-hidden">
      {/* Official Banner for Desktop */}
      <div className="hidden lg:block absolute top-0 left-0 right-0 bg-primary text-white py-2 px-4 text-center text-xl z-50">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>TAXIFY AI ASSISTANT</span>
            <span className="text-sm bg-white/20 px-2 py-1 rounded">
              {user ? `Welcome, ${user.username}` : 'Guest Mode'}
            </span>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <button
                onClick={() => navigate('/profile')}
                className="text-sm hover:underline"
              >
                Profile
              </button>
            )}
            <button
              onClick={handleLogout}
              className="text-sm bg-white/20 hover:bg-white/30 px-3 py-1 rounded transition-colors"
            >
              {user ? 'Logout' : 'Go to Home'}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Header */}
      <Header 
        onMenuClick={() => setIsSidebarOpen(true)} 
        user={user}
        onLogout={handleLogout}
      />

      {/* Main Layout */}
      <div className="flex h-full pt-14 lg:pt-10">
        {/* Sidebar (Desktop: always, Mobile: when open) */}
        {showSidebar && (
          <div className="fixed lg:relative inset-y-0 left-0 z-30 lg:z-auto w-64 lg:w-72 h-full bg-surface border-r border-border lg:block shadow-lg lg:shadow-none">
            <Sidebar
              recentChats={recentChats}
              onNewChat={startNewChat}
              onSelectChat={handleSelectChat}
              onQuickTopicSelect={handleQuickTopicSelect}
              isMobile={window.innerWidth < 1024}
              onClose={() => setIsSidebarOpen(false)}
              onOfficialSourcesClick={() => setShowOfficialModal(true)}
              onDisclaimerClick={() => setShowDisclaimerModal(true)}
              onFAQsClick={() => setShowFAQsModal(true)}
              onClearRecentChats={clearRecentChats} 
              user={user}
              onProfileClick={() => navigate('/profile')}
              onLogout={handleLogout}
            />
          </div>
        )}

        {/* Chat Window */}
        {showChat && (
          <div className="flex-1 h-full">
            <ChatWindow
              messages={messages}
              onSend={handleSendMessage}
              loading={loading}
              error={error}
              onErrorDismiss={() => setError(null)}
              onQuickTopicSelect={handleQuickTopicSelect}
              user={user}
            />
          </div>
        )}

        {/* Mobile Navigation */}
        {window.innerWidth < 1024 && (
          <MobileNav
            onMenuClick={handleMobileNavClick}
            activeView={mobileView}
          />
        )}

        {/* mobile sidebar */}
        {isSidebarOpen && window.innerWidth < 1024 && (
          <div
            className="fixed inset-0 bg-black/50 z-20"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}
      </div>

      {/* Global Error  */}
      {error && (
        <div className="fixed bottom-20 lg:bottom-4 right-4 z-50 max-w-sm">
          <ErrorDisplay
            error={error}
            onDismiss={() => setError(null)}
          />
        </div>
      )}

      {/* Connection Status Indicator */}
      <div className="fixed bottom-4 left-4 z-40 hidden lg:block">
        <div className="flex items-center gap-2 text-xs text-text-light bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border">
          <div className={`w-2 h-2 rounded-full ${sessionId ? 'bg-success' : 'bg-warning'}`}></div>
          <span>{sessionId ? 'Connected' : 'Connecting...'}</span>
          {sessionId && (
            <span className="text-xs opacity-70">
              {sessionId.substring(0, 8)}...
            </span>
          )}
          {user && (
            <span className="text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">
              {user.username}
            </span>
          )}
        </div>
      </div>

      {/* Official Sources Modal */}
      <OfficialSourcesModal
        isOpen={showOfficialModal}
        onClose={() => setShowOfficialModal(false)}
      />

      {/* Legal Disclaimer Modal */}
      <LegalDisclaimerModal
        isOpen={showDisclaimerModal}
        onClose={() => setShowDisclaimerModal(false)}
      />

      {/* FAQs Modal */}
      <FAQsModal
        isOpen={showFAQsModal}
        onClose={() => setShowFAQsModal(false)}
      />
    </div>
  );
}

export default Dashboard;

