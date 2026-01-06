import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md', 
  disabled = false,
  className = '',
  type = 'button',
  icon: Icon,
  ...props 
}) => {
  const baseStyles = 'font-medium rounded-md transition-colors duration-200 flex items-center justify-center gap-2 tracking-normal normal-case';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-light active:bg-primary/90 disabled:bg-gray-300',
    secondary: 'bg-secondary text-white hover:bg-blue-900 active:bg-blue-950',
    outline: 'border border-primary text-primary hover:bg-primary/5',
    ghost: 'text-primary hover:bg-primary/5',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseStyles}
        ${variants[variant]}
        ${sizes[size]}
        ${disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}
        ${className}
      `}
      {...props}
    >
      {Icon && <Icon />}
      {children}
    </button>
  );
};

export default Button;