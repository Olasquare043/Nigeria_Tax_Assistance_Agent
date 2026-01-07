import React, { useState, useEffect } from 'react';
import { useChat } from './hooks/useChat';
import Sidebar from './components/layout/Sidebar';
import ChatWindow from './components/chat/ChatWindow';
import Header from './components/layout/Header';
import MobileNav from './components/layout/MobileNav';
import ErrorDisplay from './components/ui/ErrorDisplay';
import OfficialSourcesModal from './components/ui/OfficialSourcesModal';
import LegalDisclaimerModal from './components/ui/LegalDisclaimerModal';
import FAQsModal from './components/ui/FAQsModal';

function App() {
  const {
    messages,
    loading,
    error,
    sessionId,
    recentChats,
    sendMessage,
    startNewChat,
    loadChat,
    setError
  } = useChat();

  // Mobile state management
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [mobileView, setMobileView] = useState('chat');

  // Modal states
  const [showOfficialModal, setShowOfficialModal] = useState(false);
  const [showDisclaimerModal, setShowDisclaimerModal] = useState(false);
  const [showFAQsModal, setShowFAQsModal] = useState(false);

  // Debug logging
  useEffect(() => {
    console.log(':mag: App State - Session ID:', sessionId);
    console.log(':mag: App State - Message count:', messages.length);
    console.log(':mag: App State - Recent chats:', recentChats.length);
  }, [sessionId, messages, recentChats]);

  // Enhanced Debug logging
  useEffect(() => {
    console.log('🔍 Current active session:', sessionId?.substring(0, 12) + '...');
    console.log('🔍 Messages in current session:', messages.length);
    console.log('🔍 Recent chats count:', recentChats.length);
    
    // Check for unique sessions
    const uniqueSessions = [...new Set(recentChats.map(chat => chat.sessionId))];
    console.log('🔍 Unique sessions in recent:', uniqueSessions.length);
  }, [sessionId, messages, recentChats]);

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

  // ✅ FIXED: Handle loading a specific chat from recent chats
  const handleSelectChat = async (chat) => {
    if (chat && chat.sessionId) {
      console.log(':open_file_folder: Loading chat from recent:', chat.title);
      try {
        await loadChat(chat);

        // Close sidebar on mobile after loading chat
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

  // Handle quick topic selection
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

  // Determine what to show based on mobile view
  const showSidebar = window.innerWidth >= 1024 || isSidebarOpen;
  const showChat = window.innerWidth >= 1024 || mobileView === 'chat';

  return (
    <div className="h-screen bg-background overflow-hidden">
      {/* Official Banner for Desktop */}
      <div className="hidden lg:block absolute top-0 left-0 right-0 bg-primary text-white py-2 px-4 text-center text-xl z-50">
        <div className="container mx-auto flex items-center justify-center gap-2">
          <span>Nigeria Tax Reform Bills Q&A Assistant</span>
        </div>
      </div>

      {/* Mobile Header */}
      <Header onMenuClick={() => setIsSidebarOpen(true)} />

      {/* Main Layout */}
      <div className="flex h-full pt-14 lg:pt-10">
        {/* Sidebar (Desktop: always, Mobile: when open) */}
        {showSidebar && (
          <div className="fixed lg:relative inset-y-0 left-0 z-30 lg:z-auto w-64 lg:w-72 h-full bg-surface border-r border-border lg:block shadow-lg lg:shadow-none">
            <Sidebar
              recentChats={recentChats}
              onNewChat={startNewChat}
              onSelectChat={handleSelectChat} // ✅ This should be the function above
              onQuickTopicSelect={handleQuickTopicSelect}
              isMobile={window.innerWidth < 1024}
              onClose={() => setIsSidebarOpen(false)}
              onOfficialSourcesClick={() => setShowOfficialModal(true)}
              onDisclaimerClick={() => setShowDisclaimerModal(true)}
              onFAQsClick={() => setShowFAQsModal(true)}
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

export default App;


// import React, { useState, useEffect } from 'react';
// import { useChat } from './hooks/useChat';
// import Sidebar from './components/layout/Sidebar';
// import ChatWindow from './components/chat/ChatWindow';
// import Header from './components/layout/Header';
// import MobileNav from './components/layout/MobileNav';
// import ErrorDisplay from './components/ui/ErrorDisplay';
// import OfficialSourcesModal from './components/ui/OfficialSourcesModal';
// import LegalDisclaimerModal from './components/ui/LegalDisclaimerModal';
// import FAQsModal from './components/ui/FAQsModal';

// function App() {
//   const {
//     messages,
//     loading,
//     error,
//     sessionId,
//     recentChats,
//     sendMessage,
//     startNewChat,
//     loadChat,
//     clearRecentChats,
//     setError
//   } = useChat();

//   // Mobile state management
//   const [isSidebarOpen, setIsSidebarOpen] = useState(false);
//   const [mobileView, setMobileView] = useState('chat');

//   // Modal states
//   const [showOfficialModal, setShowOfficialModal] = useState(false);
//   const [showDisclaimerModal, setShowDisclaimerModal] = useState(false);
//   const [showFAQsModal, setShowFAQsModal] = useState(false);

//   // Debug logging
//   useEffect(() => {
//     console.log('🔍 App State - Session ID:', sessionId?.substring(0, 12) + '...');
//     console.log('🔍 App State - Message count:', messages.length);
//     console.log('🔍 App State - Recent chats:', recentChats.length);
    
//     // Check for unique sessions
//     const uniqueSessions = [...new Set(recentChats.map(chat => chat.sessionId))];
//     console.log('🔍 Unique sessions in recent:', uniqueSessions.length);
    
//     if (uniqueSessions.length > 0) {
//       console.log('🔍 Session IDs:', uniqueSessions.map(s => s.substring(0, 8) + '...'));
//     }
//   }, [sessionId, messages, recentChats]);

//   // Close sidebar on desktop
//   useEffect(() => {
//     const handleResize = () => {
//       if (window.innerWidth >= 1024) {
//         setIsSidebarOpen(false);
//         setMobileView('chat');
//       }
//     };

//     window.addEventListener('resize', handleResize);
//     handleResize(); // Initial check

//     return () => window.removeEventListener('resize', handleResize);
//   }, []);

//   // Handle sending messages
//   const handleSendMessage = async (message) => {
//     await sendMessage(message);
//   };

//   // Handle loading a specific chat from recent chats
//   const handleSelectChat = async (chat) => {
//     if (chat && chat.sessionId) {
//       console.log('📂 Loading chat from recent:', {
//         title: chat.title,
//         sessionId: chat.sessionId?.substring(0, 12) + '...'
//       });
      
//       try {
//         await loadChat(chat);
        
//         // Close sidebar on mobile after loading chat
//         if (window.innerWidth < 1024) {
//           setIsSidebarOpen(false);
//           setMobileView('chat');
//         }
//       } catch (err) {
//         console.error('Error loading chat:', err);
//         setError('Could not load chat. Starting new chat instead.');
//         await startNewChat();
//       }
//     }
//   };

//   // Handle quick topic selection
//   const handleQuickTopicSelect = (question) => {
//     handleSendMessage(question);
//     if (window.innerWidth < 1024) {
//       setIsSidebarOpen(false);
//       setMobileView('chat');
//     }
//   };

//   // Handle mobile navigation
//   const handleMobileNavClick = (view) => {
//     setMobileView(view);
//     if (view === 'menu') {
//       setIsSidebarOpen(true);
//     } else {
//       setIsSidebarOpen(false);
//     }
//   };

//   // Handle clearing recent chats
//   const handleClearRecentChats = () => {
//     if (clearRecentChats) {
//       clearRecentChats();
//       console.log('🧹 Recent chats cleared from sidebar');
//     }
//   };

//   // Determine what to show based on mobile view
//   const showSidebar = window.innerWidth >= 1024 || isSidebarOpen;
//   const showChat = window.innerWidth >= 1024 || mobileView === 'chat';

//   // Calculate session stats for display
//   const uniqueSessions = [...new Set(recentChats.map(chat => chat.sessionId))];
//   const sessionCount = uniqueSessions.length;

//   return (
//     <div className="h-screen bg-background overflow-hidden">
//       {/* Official Banner for Desktop */}
//       <div className="hidden lg:block absolute top-0 left-0 right-0 bg-primary text-white py-2 px-4 text-center text-sm z-50">
//         <div className="container mx-auto flex items-center justify-center gap-2">
//           <span className="font-medium">Official:</span>
//           <span>Nigeria Tax Reform Bills 2024 Q&A Assistant</span>
//           <span className="ml-2 px-2 py-0.5 bg-white/20 rounded text-xs">BETA</span>
//           {sessionCount > 0 && (
//             <span className="ml-2 text-xs opacity-80">
//               {sessionCount} active session{sessionCount !== 1 ? 's' : ''}
//             </span>
//           )}
//         </div>
//       </div>

//       {/* Mobile Header */}
//       <Header onMenuClick={() => setIsSidebarOpen(true)} />

//       {/* Main Layout */}
//       <div className="flex h-full pt-14 lg:pt-10">
//         {/* Sidebar (Desktop: always, Mobile: when open) */}
//         {showSidebar && (
//           <div className="fixed lg:relative inset-y-0 left-0 z-30 lg:z-auto w-64 lg:w-72 h-full bg-surface border-r border-border lg:block shadow-lg lg:shadow-none">
//             <Sidebar
//               recentChats={recentChats}
//               onNewChat={startNewChat}
//               onSelectChat={handleSelectChat}
//               onQuickTopicSelect={handleQuickTopicSelect}
//               isMobile={window.innerWidth < 1024}
//               onClose={() => setIsSidebarOpen(false)}
//               onOfficialSourcesClick={() => setShowOfficialModal(true)}
//               onDisclaimerClick={() => setShowDisclaimerModal(true)}
//               onFAQsClick={() => setShowFAQsModal(true)}
//               onClearRecentChats={handleClearRecentChats}
//             />
//           </div>
//         )}

//         {/* Chat Window */}
//         {showChat && (
//           <div className="flex-1 h-full">
//             <ChatWindow
//               messages={messages}
//               onSend={handleSendMessage}
//               loading={loading}
//               error={error}
//               onErrorDismiss={() => setError(null)}
//               onQuickTopicSelect={handleQuickTopicSelect}
//             />
//           </div>
//         )}

//         {/* Mobile Navigation */}
//         {window.innerWidth < 1024 && (
//           <MobileNav
//             onMenuClick={handleMobileNavClick}
//             activeView={mobileView}
//           />
//         )}

//         {/* Overlay for mobile sidebar */}
//         {isSidebarOpen && window.innerWidth < 1024 && (
//           <div 
//             className="fixed inset-0 bg-black/50 z-20"
//             onClick={() => setIsSidebarOpen(false)}
//           />
//         )}
//       </div>

//       {/* Global Error Toast */}
//       {error && (
//         <div className="fixed bottom-20 lg:bottom-4 right-4 z-50 max-w-sm">
//           <ErrorDisplay 
//             error={error} 
//             onDismiss={() => setError(null)}
//           />
//         </div>
//       )}

//       {/* Session Status Indicator */}
//       <div className="fixed bottom-4 left-4 z-40 hidden lg:block">
//         <div className="flex items-center gap-2 text-xs text-text-light bg-white/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-border">
//           <div className={`w-2 h-2 rounded-full ${sessionId ? 'bg-success' : 'bg-warning'}`}></div>
//           <span>{sessionId ? 'Connected' : 'Connecting...'}</span>
//           {sessionId && (
//             <span className="text-xs opacity-70" title={`Session: ${sessionId}`}>
//               {sessionId.substring(0, 8)}...
//             </span>
//           )}
//           {sessionCount > 0 && (
//             <span className="ml-2 text-xs bg-primary/10 text-primary px-1.5 py-0.5 rounded">
//               {sessionCount} session{sessionCount !== 1 ? 's' : ''}
//             </span>
//           )}
//         </div>
//       </div>

//       {/* Debug Panel - Remove in production */}
//       {/* {process.env.NODE_ENV === 'development' && (
//         <div className="fixed top-4 right-4 z-50 bg-black/80 text-white text-xs p-3 rounded-lg max-w-xs">
//           <div className="font-bold mb-2">Debug Info</div>
//           <div>Session: {sessionId?.substring(0, 8)}...</div>
//           <div>Messages: {messages.length}</div>
//           <div>Recent Chats: {recentChats.length}</div>
//           <div>Unique Sessions: {sessionCount}</div>
//           <button 
//             onClick={() => {
//               console.log('Recent Chats:', recentChats);
//               console.log('Current Session:', sessionId);
//               console.log('All Messages:', messages);
//             }}
//             className="mt-2 text-blue-300 hover:text-blue-100 text-xs"
//           >
//             Log Details
//           </button>
//         </div>
//       )} */}

//       {/* Official Sources Modal */}
//       <OfficialSourcesModal
//         isOpen={showOfficialModal}
//         onClose={() => setShowOfficialModal(false)}
//       />

//       {/* Legal Disclaimer Modal */}
//       <LegalDisclaimerModal
//         isOpen={showDisclaimerModal}
//         onClose={() => setShowDisclaimerModal(false)}
//       />

//       {/* FAQs Modal */}
//       <FAQsModal
//         isOpen={showFAQsModal}
//         onClose={() => setShowFAQsModal(false)}
//       />
//     </div>
//   );
// }

// export default App;