import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiMail, FiLock, FiArrowLeft, FiAlertCircle, FiShield } from 'react-icons/fi';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/dashboard';

  const handleContinueAsGuest = () => {
    setError('');
    navigate('/dashboard', { replace: true });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);
      if (result.success) {
        navigate(from, { replace: true });
      } else {
        setError(result.error || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-8 h-8 bg-[#005c39] rounded-lg flex items-center justify-center text-white group-hover:bg-[#004a2e] transition-colors">
              <FiArrowLeft size={18} />
            </div>
            <span className="text-gray-700 font-semibold uppercase tracking-wider text-xs">Back to Home</span>
          </Link>
          <div className="hidden sm:block">
            <span className="text-gray-500 text-sm">New here? </span>
            <Link to="/signup" className="text-[#005c39] font-bold text-sm hover:underline">Create Account</Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
            <div className="text-center mb-10">
              {/* Logo Representation */}
              <div className="w-16 h-16 bg-[#005c39]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiShield className="text-[#005c39]" size={28} />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
              <p className="text-gray-500 mt-2 text-sm">Secure access to TaxAble AI Portal</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3 animate-shake">
                <FiAlertCircle className="text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="name@email.com"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-xs font-black uppercase tracking-widest text-gray-500">
                    Password
                  </label>
                  <Link to="/forgot-password" size="xs" className="text-[10px] font-bold text-[#005c39] uppercase hover:underline">
                    Reset Password?
                  </Link>
                </div>
                <div className="relative">
                  <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="••••••••"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#005c39] text-white py-4 rounded-xl font-bold hover:bg-[#004a2e] transition-all transform active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-green-900/10"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  'Sign In to Dashboard'
                )}
              </button>

              <div className="relative my-8">
                <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-gray-100"></div></div>
                <div className="relative flex justify-center text-xs uppercase tracking-widest font-bold text-gray-400">
                  <span className="px-4 bg-white">OR</span>
                </div>
              </div>

              <button
                type="button"
                onClick={handleContinueAsGuest}
                className="w-full bg-white border-2 border-gray-100 text-gray-600 py-3 rounded-xl font-bold hover:bg-gray-50 transition-all flex items-center justify-center gap-2"
              >
                Continue as Guest
              </button>
            </form>

            <div className="mt-10 pt-6 border-t border-gray-50 text-center">
              <p className="text-[11px] text-gray-400 leading-tight px-6">
                By logging in, you agree to our <Link to="/terms" className="text-[#005c39] font-bold underline">Terms</Link> and <Link to="/privacy" className="text-[#005c39] font-bold underline">Privacy Policy</Link>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
