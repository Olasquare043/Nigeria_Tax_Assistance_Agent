import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiMail, FiArrowLeft, FiAlertCircle, FiCheckCircle, FiCopy } from 'react-icons/fi';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [step, setStep] = useState('request'); // 'request' or 'reset'
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoToken, setDemoToken] = useState('');
  
  const { forgotPassword, resetPassword } = useAuth();
  const navigate = useNavigate();

  const handleRequestReset = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await forgotPassword(email);
      
      if (result.success) {
        setSuccess('Password reset instructions have been sent to your email.');
        setDemoToken(result.demoToken); // For demo/testing only
        setStep('reset');
      } else {
        setError(result.error || 'Failed to send reset instructions.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (!resetToken || !newPassword || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await resetPassword(resetToken, newPassword);
      
      if (result.success) {
        setSuccess('Password reset successfully! You can now login with your new password.');
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setError(result.error || 'Failed to reset password.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(demoToken);
    setSuccess('Token copied to clipboard!');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/login" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <FiArrowLeft className="text-white" size={18} />
              </div>
              <span className="text-gray-700 font-medium">Back to Login</span>
            </Link>
            <Link 
              to="/" 
              className="text-primary font-medium hover:underline"
            >
              Home
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center py-12">
        <div className="max-w-md w-full mx-auto px-4">
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiMail className="text-primary" size={24} />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">
                {step === 'request' ? 'Reset Your Password' : 'Enter Reset Token'}
              </h1>
              <p className="text-gray-600 mt-2">
                {step === 'request' 
                  ? "Enter your email and we'll send you reset instructions"
                  : "Check your email and enter the reset token"}
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-lg flex items-start gap-3">
                <FiAlertCircle className="text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-100 rounded-lg flex items-start gap-3">
                <FiCheckCircle className="text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-green-700 text-sm">{success}</p>
              </div>
            )}

            {step === 'request' ? (
              <form onSubmit={handleRequestReset} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                      placeholder="you@example.com"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Sending reset link...
                    </>
                  ) : (
                    'Send Reset Instructions'
                  )}
                </button>

                {/* Demo Mode Note */}
                <div className="p-4 bg-yellow-50 border border-yellow-100 rounded-lg">
                  <p className="text-yellow-800 text-sm">
                    <strong>Demo Note:</strong> In production, this would send an email. 
                    For this demo, you'll receive a token on the next screen.
                  </p>
                </div>
              </form>
            ) : (
              <form onSubmit={handleResetPassword} className="space-y-6">
                {demoToken && (
                  <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-blue-800 text-sm font-medium">Demo Reset Token:</p>
                      <button
                        type="button"
                        onClick={copyToClipboard}
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <FiCopy size={14} />
                        Copy
                      </button>
                    </div>
                    <code className="block bg-white p-2 rounded border text-sm font-mono break-all">
                      {demoToken}
                    </code>
                    <p className="text-blue-600 text-xs mt-2">
                      Copy this token and paste it below. In production, this would be sent via email.
                    </p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Reset Token
                  </label>
                  <input
                    type="text"
                    value={resetToken}
                    onChange={(e) => setResetToken(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors font-mono"
                    placeholder="Paste the token from your email"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    placeholder="At least 6 characters"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                    placeholder="Confirm your new password"
                    required
                    disabled={loading}
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    type="button"
                    onClick={() => setStep('request')}
                    className="flex-1 border-2 border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                    disabled={loading}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-primary text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Resetting...
                      </>
                    ) : (
                      'Reset Password'
                    )}
                  </button>
                </div>
              </form>
            )}

            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Security Tips:</h3>
              <ul className="text-xs text-gray-600 space-y-1">
                <li className="flex items-start gap-1">
                  <FiCheckCircle className="text-green-500 mt-0.5 flex-shrink-0" size={12} />
                  Use a strong password with at least 6 characters
                </li>
                <li className="flex items-start gap-1">
                  <FiCheckCircle className="text-green-500 mt-0.5 flex-shrink-0" size={12} />
                  Reset tokens expire after 30 minutes
                </li>
                <li className="flex items-start gap-1">
                  <FiCheckCircle className="text-green-500 mt-0.5 flex-shrink-0" size={12} />
                  Never share your reset token with anyone
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600">
              Remember your password?{' '}
              <Link to="/login" className="text-primary font-medium hover:underline">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;