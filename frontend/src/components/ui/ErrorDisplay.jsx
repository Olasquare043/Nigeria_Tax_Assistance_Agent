import React from 'react';
import { FiAlertCircle } from 'react-icons/fi';

const ErrorDisplay = ({ error, onDismiss, className = '' }) => {
  if (!error) return null;

  return (
    <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3">
        <FiAlertCircle className="text-red-500 mt-0.5 flex-shrink-0" size={20} />
        <div className="flex-1">
          <p className="text-red-800 text-sm font-medium">{error}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-500 hover:text-red-700 text-sm font-medium"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;