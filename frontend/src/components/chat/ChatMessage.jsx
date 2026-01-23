// import React from 'react';
// import { FiUser, FiFileText, FiAlertCircle, FiMessageSquare } from 'react-icons/fi';
// import { formatDate } from '../../utils/helpers';

// const ChatMessage = ({ message }) => {
//   const isUser = message.role === 'user';
  
//   return (
//     <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
//       {/* Avatar */}
//       <div className={`flex-shrink-0 ${isUser ? 'order-2' : 'order-1'}`}>
//         <div className={`w-8 h-8 rounded-md flex items-center justify-center ${isUser ? 'bg-primary text-white' : 'bg-secondary text-white'}`}>
//           {isUser ? <FiUser size={18} /> : <FiFileText size={18} />}
//         </div>
//       </div>
      
//       {/* Message Bubble */}
//       <div className={`flex-1 ${isUser ? 'order-1 text-right' : 'order-2'}`}>
//         <div className={`inline-block max-w-[85%] lg:max-w-[70%] rounded-lg px-4 py-3 professional-card ${isUser ? 'bg-primary text-white' : 'bg-surface'}`}>
//           <p className="whitespace-pre-wrap leading-relaxed">{message.text}</p>
//         </div>
        
//         {/* Timestamp */}
//         <div className={`mt-1.5 text-xs text-text-light ${isUser ? 'text-right' : 'text-left'}`}>
//           {formatDate(message.timestamp)}
//         </div>
        
//         {/* Route Indicator (for assistant messages) */}
//         {!isUser && message.route && message.route !== "qa" && (
//           <div className="mt-2 text-left">
//             <span className="inline-block px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full border border-gray-300">
//               {message.route === "clarify" && "🤔 Seeking Clarification"}
//               {message.route === "compare" && "📊 Comparison Mode"}
//               {message.route === "claim_check" && "🔍 Fact Checking"}
//               {message.route === "smalltalk" && "💬 General Chat"}
//               {message.route === "qa" && "❓ Q&A"}
//               {!["clarify", "compare", "claim_check", "smalltalk", "qa"].includes(message.route) && 
//                 `Mode: ${message.route}`}
//             </span>
//           </div>
//         )}
        
//         {/* Refusal Warning */}
//         {!isUser && message.refusal && (
//           <div className="mt-3 text-left">
//             <div className="flex items-start gap-2 p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded-r">
//               <FiAlertCircle className="text-yellow-500 mt-0.5 flex-shrink-0" size={16} />
//               <div className="flex-1">
//                 <p className="text-sm text-yellow-800 font-medium">
//                   Limited Response
//                 </p>
//                 <p className="text-xs text-yellow-700 mt-0.5">
//                   This query may be outside the scope of Nigerian tax reform topics.
//                 </p>
//               </div>
//             </div>
//           </div>
//         )}
        
//         {/* Citations (for assistant messages) */}
//         {!isUser && message.citations && message.citations.length > 0 && (
//           <div className="mt-4 space-y-2">
//             <div className="text-xs font-medium text-text-light uppercase tracking-wider flex items-center gap-2">
//               <FiFileText size={12} />
//               Reference Sources
//             </div>
//             <div className="space-y-2">
//               {message.citations.map((source, index) => (
//                 <div 
//                   key={index} 
//                   className="citation-item"
//                 >
//                   <div className="flex items-start justify-between">
//                     <div>
//                       <div className="font-semibold text-primary text-sm">
//                         {source.source || "Document"}
//                       </div>
//                       {source.pages && source.pages !== "p.?" && (
//                         <div className="text-text-light text-xs mt-0.5">
//                           Pages: {source.pages}
//                         </div>
//                       )}
//                     </div>
//                     {source.chunk_id && (
//                       <div className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">
//                         ID: {source.chunk_id.substring(0, 8)}...
//                       </div>
//                     )}
//                   </div>
                  
//                   {source.quote && (
//                     <div className="mt-2 pt-2 border-t border-gray-200">
//                       <p className="text-text text-sm italic leading-snug">
//                         "{source.quote}"
//                       </p>
//                     </div>
//                   )}
//                 </div>
//               ))}
//             </div>
//           </div>
//         )}
        
//         {/* Error State */}
//         {message.isError && (
//           <div className="mt-3 text-left">
//             <div className="flex items-start gap-2 p-3 bg-red-50 border-l-4 border-red-400 rounded-r">
//               <FiAlertCircle className="text-red-500 mt-0.5 flex-shrink-0" size={16} />
//               <div className="flex-1">
//                 <p className="text-sm text-red-800">
//                   {message.text}
//                 </p>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default ChatMessage;

import React from 'react';
import { FiUser, FiFileText, FiAlertCircle, FiHash, FiBookOpen } from 'react-icons/fi';
import { formatDate } from '../../utils/helpers';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  
  // Dynamic rounded corners based on sender
  const bubbleRadius = isUser 
    ? "rounded-2xl rounded-tr-none" 
    : "rounded-2xl rounded-tl-none";

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-8 animate-in fade-in slide-in-from-bottom-2 duration-300`}>
      
      {/* Avatar with Ring Effect */}
      <div className="flex-shrink-0">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center shadow-sm border
          ${isUser 
            ? 'bg-primary border-primary-dark text-white' 
            : 'bg-white border-gray-200 text-secondary'}`}>
          {isUser ? <FiUser size={18} /> : <FiBookOpen size={18} />}
        </div>
      </div>
      
      {/* Content Area */}
      <div className={`flex flex-col max-w-[85%] lg:max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        
        {/* Route Indicator (Subtle pill above the bubble for context) */}
        {!isUser && message.route && message.route !== "qa" && (
          <div className="mb-1.5 flex items-center gap-1.5 px-2 py-0.5 bg-gray-50 text-gray-500 text-[10px] font-bold uppercase tracking-wider rounded border border-gray-100">
            <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
            {message.route.replace('_', ' ')}
          </div>
        )}

        {/* Main Message Bubble */}
        <div className={`px-4 py-3 shadow-sm border transition-all ${bubbleRadius} 
          ${isUser 
            ? 'bg-primary border-primary-dark text-white' 
            : 'bg-white border-gray-100 text-gray-800'}`}>
          <p className="text-[15px] whitespace-pre-wrap leading-relaxed">
            {message.text}
          </p>
        </div>
        
        {/* Timestamp */}
        <div className="mt-1.5 px-1 text-[11px] font-medium text-gray-400">
          {formatDate(message.timestamp)}
        </div>
        
        {/* Refusal Warning (Styled as a soft notice) */}
        {!isUser && message.refusal && (
          <div className="mt-3 w-full max-w-sm overflow-hidden rounded-lg border border-amber-100 bg-amber-50/50">
            <div className="flex items-start gap-3 p-3">
              <FiAlertCircle className="text-amber-500 mt-0.5 flex-shrink-0" size={16} />
              <div>
                <p className="text-xs font-bold text-amber-900 uppercase tracking-tight">Scope Notice</p>
                <p className="text-xs text-amber-800/80 leading-snug">
                  This query may be outside the scope of Nigerian tax reform topics.
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Citations (Accordion-style or Grid) */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-4 w-full space-y-3">
            <div className="flex items-center gap-2 px-1">
              <div className="h-[1px] flex-1 bg-gray-100" />
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Sources</span>
              <div className="h-[1px] flex-1 bg-gray-100" />
            </div>
            
            <div className="grid grid-cols-1 gap-2">
              {message.citations.map((source, index) => (
                <div key={index} className="group relative bg-white border border-gray-100 p-3 rounded-xl hover:border-primary/30 hover:shadow-md transition-all">
                  <div className="flex items-start justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
                        <FiFileText size={14} />
                      </div>
                      <span className="font-bold text-gray-700 text-sm truncate max-w-[150px]">
                        {source.source || "Document Reference"}
                      </span>
                    </div>
                    {source.pages && (
                      <span className="text-[10px] bg-gray-50 text-gray-500 px-2 py-0.5 rounded-full border border-gray-100">
                        p. {source.pages}
                      </span>
                    )}
                  </div>
                  
                  {source.quote && (
                    <div className="relative pl-3 border-l-2 border-gray-100 group-hover:border-primary/20">
                      <p className="text-[13px] text-gray-500 italic leading-snug line-clamp-2 group-hover:line-clamp-none transition-all">
                        "{source.quote}"
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Error State */}
        {message.isError && (
          <div className="mt-3 flex items-center gap-2 px-3 py-2 bg-red-50 text-red-700 rounded-lg border border-red-100 text-sm">
            <FiAlertCircle size={14} />
            <span>{message.text}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;