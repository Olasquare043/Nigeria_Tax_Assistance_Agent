
import React from 'react';
import { FiX, FiAlertTriangle, FiShield } from 'react-icons/fi';

const LegalDisclaimerModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

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
          <div className="bg-amber-500 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FiAlertTriangle size={24} />
                <div>
                  <h2 className="text-xl font-bold">Legal Disclaimer</h2>
                  <p className="text-amber-100 text-sm mt-1">
                    Important Information Notice
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-amber-100 p-1 rounded-full hover:bg-white/10 transition-colors"
              >
                <FiX size={24} />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <div className="space-y-4">
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <FiAlertTriangle className="text-amber-600 mt-1 flex-shrink-0" size={20} />
                  <div>
                    <p className="text-amber-800 font-medium">Important Notice</p>
                    <p className="text-amber-700 text-sm mt-1">
                      This assistant provides informational guidance only and does not constitute legal, financial, or professional tax advice.
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="font-semibold text-gray-900 text-lg">Terms of Use</h3>
                
                <div className="space-y-4">
                  <div className="border-l-4 border-amber-500 pl-4 py-2">
                    <h4 className="font-medium text-gray-900">1. Informational Purpose Only</h4>
                    <p className="text-gray-600 text-sm mt-1">
                      The Nigeria Tax Reform Bills 2024 Q&A Assistant is designed to provide general information about proposed tax reforms. It should not be relied upon as a substitute for professional advice from qualified tax practitioners, legal counsel, or the Federal Inland Revenue Service (FIRS).
                    </p>
                  </div>

                  <div className="border-l-4 border-amber-500 pl-4 py-2">
                    <h4 className="font-medium text-gray-900">2. No Liability</h4>
                    <p className="text-gray-600 text-sm mt-1">
                      The developers, operators, and associated government agencies shall not be liable for any decisions made or actions taken based on information provided by this assistant. Users assume full responsibility for verifying information with official sources.
                    </p>
                  </div>

                  <div className="border-l-4 border-amber-500 pl-4 py-2">
                    <h4 className="font-medium text-gray-900">3. Official Documents Prevail</h4>
                    <p className="text-gray-600 text-sm mt-1">
                      In case of any discrepancy between information provided by this assistant and official government publications, the official documents shall prevail. Always refer to the original legislation and official gazettes for authoritative information.
                    </p>
                  </div>

                  <div className="border-l-4 border-amber-500 pl-4 py-2">
                    <h4 className="font-medium text-gray-900">4. No Attorney-Client Relationship</h4>
                    <p className="text-gray-600 text-sm mt-1">
                      Use of this assistant does not create an attorney-client, accountant-client, or any other professional relationship between the user and any government agency or service provider.
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="font-semibold text-gray-900 mb-3">Recommended Actions</h3>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5"></div>
                    <span>Consult with a qualified tax professional for personalized advice</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5"></div>
                    <span>Verify information with the Federal Inland Revenue Service (FIRS)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5"></div>
                    <span>Review official government publications and gazettes</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5"></div>
                    <span>Monitor updates from the National Assembly and Ministry of Finance</span>
                  </li>
                </ul>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
                <FiShield className="text-amber-500" size={16} />
                <span>Official Government Information Source</span>
                <FiShield className="text-amber-500" size={16} />
              </div>
              <p className="text-center text-xs text-gray-500 mt-2">
                Federal Republic of Nigeria • Ministry of Finance • FIRS
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LegalDisclaimerModal;
