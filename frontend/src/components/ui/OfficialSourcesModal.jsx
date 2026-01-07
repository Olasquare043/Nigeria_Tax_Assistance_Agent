
// import React from 'react';
// import { FiX, FiExternalLink, FiFileText, FiShield } from 'react-icons/fi';

// const OfficialSourcesModal = ({ isOpen, onClose }) => {
//   if (!isOpen) return null;

//   const officialSources = [
//     {
//       name: "Tax Reform Bill 2024",
//       description: "The comprehensive tax reform legislation currently under consideration by the National Assembly.",
//       type: "Legislation",
//       status: "Pending"
//     },
//     {
//       name: "Finance Act 2024",
//       description: "Annual finance act containing tax amendments and fiscal measures for the year.",
//       type: "Legislation",
//       status: "Enacted"
//     },
//     {
//       name: "FIRS Guidelines & Circulars",
//       description: "Official guidelines, practice notes, and circulars issued by the Federal Inland Revenue Service.",
//       type: "Regulatory",
//       status: "Current"
//     },
//     {
//       name: "National Assembly Publications",
//       description: "Committee reports, hearing transcripts, and explanatory memoranda from the National Assembly.",
//       type: "Parliamentary",
//       status: "Official"
//     },
//     {
//       name: "Ministry of Finance Reports",
//       description: "Policy papers, white papers, and technical reports from the Federal Ministry of Finance.",
//       type: "Government",
//       status: "Official"
//     }
//   ];

//   return (
//     <div className="fixed inset-0 z-50 overflow-y-auto">
//       {/* Backdrop */}
//       <div 
//         className="fixed inset-0 bg-black/50 transition-opacity"
//         onClick={onClose}
//       />

//       {/* Modal */}
//       <div className="flex min-h-full items-center justify-center p-4">
//         <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
//           {/* Header */}
//           <div className="bg-primary text-white p-6">
//             <div className="flex items-center justify-between">
//               <div className="flex items-center gap-3">
//                 <FiShield size={24} />
//                 <div>
//                   <h2 className="text-xl font-bold">Official Sources</h2>
//                   <p className="text-primary-100 text-sm mt-1">
//                     Nigeria Tax Reform Bills 2024 Q&A Assistant
//                   </p>
//                 </div>
//               </div>
//               <button
//                 onClick={onClose}
//                 className="text-white hover:text-primary-100 p-1 rounded-full hover:bg-white/10 transition-colors"
//               >
//                 <FiX size={24} />
//               </button>
//             </div>
//           </div>

//           {/* Content */}
//           <div className="p-6 overflow-y-auto max-h-[60vh]">
//             <div className="mb-6">
//               <p className="text-gray-700 mb-4">
//                 This assistant provides answers based on verified official documents and publications 
//                 related to Nigeria's 2024 Tax Reform Bills. All responses are sourced from the following 
//                 authoritative documents:
//               </p>
              
//               <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
//                 <div className="flex items-start gap-3">
//                   <FiFileText className="text-blue-600 mt-1 flex-shrink-0" size={20} />
//                   <div>
//                     <p className="text-blue-800 font-medium">Information Accuracy</p>
//                     <p className="text-blue-700 text-sm mt-1">
//                       While we strive for accuracy, this tool provides informational guidance only. 
//                       For specific tax advice, please consult a qualified tax professional or the 
//                       Federal Inland Revenue Service (FIRS).
//                     </p>
//                   </div>
//                 </div>
//               </div>
//             </div>

//             {/* Sources List */}
//             <div className="space-y-4">
//               <h3 className="font-semibold text-gray-900 text-lg">Primary Source Documents</h3>
              
//               {officialSources.map((source, index) => (
//                 <div 
//                   key={index}
//                   className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
//                 >
//                   <div className="flex items-start justify-between">
//                     <div>
//                       <div className="flex items-center gap-2">
//                         <h4 className="font-medium text-gray-900">{source.name}</h4>
//                         <span className={`px-2 py-1 text-xs rounded-full ${
//                           source.status === 'Enacted' 
//                             ? 'bg-green-100 text-green-800'
//                             : source.status === 'Pending'
//                             ? 'bg-yellow-100 text-yellow-800'
//                             : 'bg-blue-100 text-blue-800'
//                         }`}>
//                           {source.status}
//                         </span>
//                       </div>
//                       <p className="text-gray-600 text-sm mt-2">{source.description}</p>
//                       <div className="flex items-center gap-3 mt-3">
//                         <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
//                           {source.type}
//                         </span>
//                         <span className="text-xs text-gray-500">• Official Document</span>
//                       </div>
//                     </div>
//                     <button className="text-primary hover:text-primary-dark p-2">
//                       <FiExternalLink size={18} />
//                     </button>
//                   </div>
//                 </div>
//               ))}
//             </div>

//             {/* Footer */}
//             <div className="mt-8 pt-6 border-t border-gray-200">
//               <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
//                 <div className="w-2 h-2 bg-primary rounded-full"></div>
//                 <span>Official Information Source • Ministry of Finance</span>
//                 <div className="w-2 h-2 bg-primary rounded-full"></div>
//               </div>
//               <p className="text-center text-xs text-gray-500 mt-2">
//                 Last updated: December 2024 • Version 1.0
//               </p>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default OfficialSourcesModal;


import React from 'react';
import { FiX, FiExternalLink, FiFileText, FiShield } from 'react-icons/fi';

const OfficialSourcesModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const officialSources = [
    {
      name: "Nigeria Tax Act, 2025",
      description: "The principal tax legislation consolidating multiple former tax laws as part of the national tax reform programme.",
      type: "Legislation",
      status: "Enacted"
    },
    {
      name: "Nigeria Tax Administration Act, 2025",
      description: "Legislation establishing the legal and administrative framework for tax administration in Nigeria.",
      type: "Legislation",
      status: "Enacted"
    },
    {
      name: "Nigeria Revenue Service (Establishment) Act, 2025",
      description: "Act establishing the Nigeria Revenue Service (NRS) as the federal tax administration authority, replacing the former FIRS.",
      type: "Legislation",
      status: "Enacted"
    },
    {
      name: "Joint Revenue Board (Establishment) Act, 2025",
      description: "Act establishing the Joint Revenue Board to coordinate tax administration between federal and state tax authorities.",
      type: "Legislation",
      status: "Enacted"
    },
    {
      name: "Finance Act 2024",
      description: "The annual Finance Act containing fiscal and tax policy amendments for the 2024 financial year.",
      type: "Legislation",
      status: "Enacted"
    },
    {
      name: "NRS / FIRS Guidelines & Circulars",
      description: "Official guidelines, practice notes, and circulars issued by the Nigeria Revenue Service (formerly FIRS).",
      type: "Regulatory",
      status: "Current"
    },
    {
      name: "National Assembly Publications",
      description: "Committee reports, votes and proceedings, and explanatory memoranda from the National Assembly.",
      type: "Parliamentary",
      status: "Official"
    },
    {
      name: "Ministry of Finance Reports",
      description: "Policy papers, white papers, and technical publications from the Federal Ministry of Finance.",
      type: "Government",
      status: "Official"
    }
  ];

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
          
          {/* Header */}
          <div className="bg-primary text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FiShield size={24} />
                <div>
                  <h2 className="text-xl font-bold">Official Sources</h2>
                  <p className="text-primary-100 text-sm mt-1">
                    Nigeria Tax Reform Q&A Assistant
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-primary-100 p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <FiX size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <div className="mb-6">
              <p className="text-gray-700 mb-4">
                This assistant provides answers based on verified public records and 
                official documents relating to Nigeria’s Tax Reform Acts and associated 
                fiscal legislation. All responses are informed by the following authoritative sources:
              </p>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <FiFileText className="text-blue-600 mt-1 flex-shrink-0" size={20} />
                  <div>
                    <p className="text-blue-800 font-medium">Information Accuracy</p>
                    <p className="text-blue-700 text-sm mt-1">
                      While we strive for accuracy, this tool provides informational guidance only. 
                      For specific tax advice, please consult a qualified tax professional or the 
                      Nigeria Revenue Service (NRS).
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sources List */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900 text-lg">Primary Source Documents</h3>
              
              {officialSources.map((source, index) => (
                <div 
                  key={index}
                  className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-gray-900">{source.name}</h4>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          source.status === 'Enacted' 
                            ? 'bg-green-100 text-green-800'
                            : source.status === 'Pending'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {source.status}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mt-2">{source.description}</p>
                      <div className="flex items-center gap-3 mt-3">
                        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                          {source.type}
                        </span>
                        <span className="text-xs text-gray-500">• Official Document</span>
                      </div>
                    </div>
                    <button className="text-primary hover:text-primary-dark p-2">
                      <FiExternalLink size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                <span>Official Information Sources • Government of the Federal Republic of Nigeria</span>
                <div className="w-2 h-2 bg-primary rounded-full"></div>
              </div>
              <p className="text-center text-xs text-gray-500 mt-2">
                Last updated: January 2026 • Version 1.1
              </p>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default OfficialSourcesModal;
