import React from 'react';

const LoadingSpinner = ({ size = 'md', text = '', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  // If there's text, wrap in a column layout
  if (text) {
    return (
      <div className={`flex flex-col items-center justify-center ${className}`}>
        <div className={`${sizes[size]} animate-spin rounded-full border-2 border-primary border-t-transparent`}></div>
        {text && (
          <p className="mt-3 text-gray-600 font-medium text-sm">{text}</p>
        )}
      </div>
    );
  }

  // Original layout for no text
  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div className={`${sizes[size]} animate-spin rounded-full border-2 border-primary border-t-transparent`}></div>
    </div>
  );
};

export default LoadingSpinner;