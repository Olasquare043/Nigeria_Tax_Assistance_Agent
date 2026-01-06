
import React from 'react';
import { FiX, FiHelpCircle, FiChevronDown, FiChevronUp } from 'react-icons/fi';

const FAQsModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const [openFAQ, setOpenFAQ] = React.useState(null);

  const faqs = [
    {
      id: 1,
      question: "What is the Nigeria Tax Reform Bills 2024 Q&A Assistant?",
      answer: "This is an official AI-powered assistant designed to provide information and answers about the proposed 2024 Tax Reform Bills in Nigeria. It helps citizens, businesses, and stakeholders understand the reforms by answering questions based on official government documents and publications."
    },
    {
      id: 2,
      question: "How accurate is the information provided?",
      answer: "The assistant is trained on official government documents including the Tax Reform Bill 2024, Finance Act 2024, FIRS guidelines, and National Assembly publications. However, as legislation is subject to change during the parliamentary process, users should verify critical information with official sources."
    },
    {
      id: 3,
      question: "Can I use this information for legal or tax decisions?",
      answer: "No. This assistant provides informational guidance only. For legal, financial, or tax decisions, you must consult qualified professionals such as tax practitioners, lawyers, or directly contact the Federal Inland Revenue Service (FIRS)."
    },
    {
      id: 4,
      question: "What topics can I ask about?",
      answer: "You can ask about various aspects of the 2024 Tax Reform Bills including: proposed tax rates, new tax categories, compliance requirements, implementation timelines, impact on individuals and businesses, exemptions, and procedural changes."
    },
    {
      id: 5,
      question: "How current is the information?",
      answer: "The assistant is updated regularly with the latest official publications. The current version includes information up to December 2024. Check the 'Official Sources' section for details on specific documents used."
    },
    {
      id: 6,
      question: "Is my conversation data stored?",
      answer: "Conversations are temporarily stored to improve the service and maintain chat continuity during your session. However, personal identifying information is not collected. For detailed privacy information, please refer to our privacy policy."
    },
    {
      id: 7,
      question: "How can I provide feedback or report issues?",
      answer: "You can provide feedback through the Ministry of Finance website or contact the Digital Services Unit. Your feedback helps improve the accuracy and usefulness of this service for all users."
    },
    {
      id: 8,
      question: "Is this service available 24/7?",
      answer: "Yes, the assistant is available 24 hours a day, 7 days a week. However, during high traffic periods or system maintenance, there may be temporary delays in responses."
    }
  ];

  const toggleFAQ = (id) => {
    setOpenFAQ(openFAQ === id ? null : id);
  };

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
          <div className="bg-blue-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FiHelpCircle size={24} />
                <div>
                  <h2 className="text-xl font-bold">Frequently Asked Questions</h2>
                  <p className="text-blue-100 text-sm mt-1">
                    Nigeria Tax Reform Bills 2024 Q&A Assistant
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-blue-100 p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <FiX size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <div className="mb-6">
              <p className="text-gray-700">
                Find answers to common questions about using the Tax Reform Q&A Assistant. 
                If you don't find your question answered here, feel free to ask the assistant directly.
              </p>
            </div>

            {/* FAQs Accordion */}
            <div className="space-y-3">
              {faqs.map((faq) => (
                <div 
                  key={faq.id}
                  className="border border-gray-200 rounded-lg overflow-hidden"
                >
                  <button
                    onClick={() => toggleFAQ(faq.id)}
                    className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-medium text-gray-900">{faq.question}</span>
                    {openFAQ === faq.id ? (
                      <FiChevronUp className="text-gray-500 flex-shrink-0" size={20} />
                    ) : (
                      <FiChevronDown className="text-gray-500 flex-shrink-0" size={20} />
                    )}
                  </button>
                  
                  {openFAQ === faq.id && (
                    <div className="p-4 pt-2 border-t border-gray-100 bg-gray-50">
                      <p className="text-gray-600 text-sm leading-relaxed">{faq.answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Additional Help */}
            <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Need More Help?</h3>
              <p className="text-blue-700 text-sm">
                If your question isn't answered here or by the assistant, you can:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-blue-700">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  <span>Contact the Federal Inland Revenue Service (FIRS) helpline</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  <span>Visit the Ministry of Finance website for official publications</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  <span>Consult with a qualified tax professional for specific advice</span>
                </li>
              </ul>
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-center text-xs text-gray-500">
                For official inquiries: info@finance.gov.ng • FIRS Contact Center: 0901 000 0400
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQsModal;
