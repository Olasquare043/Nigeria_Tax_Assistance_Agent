import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiMail, FiLock, FiUser, FiArrowLeft, FiAlertCircle, FiCheck, FiBook } from 'react-icons/fi';

const Signup = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: ''
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (name === 'password') {
      checkPasswordStrength(value);
    }
  };

  const checkPasswordStrength = (password) => {
    if (password.length === 0) {
      setPasswordStrength('');
      return;
    }
    if (password.length < 6) {
      setPasswordStrength('weak');
    } else if (password.length < 10) {
      setPasswordStrength('medium');
    } else {
      setPasswordStrength('strong');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.username || !formData.password) {
      setError('Please fill in all required fields');
      return;
    }
    if (formData.password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (!formData.username.match(/^[a-zA-Z0-9]+$/)) {
      setError('Username must contain only letters and numbers');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const result = await register(formData);
      if (result.success) {
        navigate('/dashboard', { replace: true });
      } else {
        setError(result.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const passwordStrengthColor = {
    weak: 'bg-red-500',
    medium: 'bg-yellow-500',
    strong: 'bg-green-600'
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <nav className="bg-white border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="w-8 h-8 bg-[#005c39] rounded-lg flex items-center justify-center text-white group-hover:bg-[#004a2e] transition-colors">
              <FiArrowLeft size={18} />
            </div>
            <span className="text-gray-700 font-semibold uppercase tracking-wider text-xs">Back to Portal</span>
          </Link>
          <div className="flex items-center gap-2">
            <FiBook className="text-[#005c39]" />
            <span className="font-bold text-gray-800">TaxAble AI</span>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center py-12 px-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
            <div className="text-center mb-10">
              <div className="w-16 h-16 bg-[#005c39]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <FiUser className="text-[#005c39]" size={28} />
              </div>
              <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
              <p className="text-gray-500 mt-2 text-sm">Join millions of Nigerians getting tax clarity</p>
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
                  Email Address *
                </label>
                <div className="relative">
                  <FiMail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="you@email.com"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">
                  Choose Username *
                </label>
                <div className="relative">
                  <FiUser className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="e.g. Chidi2024"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">
                  Password *
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="Min. 6 characters"
                    required
                    disabled={loading}
                  />
                </div>
                {passwordStrength && (
                  <div className="mt-3 bg-gray-50 p-2 rounded-lg border border-gray-100">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${passwordStrengthColor[passwordStrength]} transition-all duration-500`}
                          style={{ width: passwordStrength === 'weak' ? '33%' : passwordStrength === 'medium' ? '66%' : '100%' }}
                        ></div>
                      </div>
                      <span className="text-[10px] font-bold uppercase text-gray-500">{passwordStrength}</span>
                    </div>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-widest text-gray-500 mb-2">
                  Confirm Password *
                </label>
                <div className="relative">
                  <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#005c39] focus:border-transparent outline-none transition-all"
                    placeholder="Re-type password"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              {/* UPDATED SECTION BELOW */}
              <div className="flex items-start gap-3 p-2">
                <input
                  type="checkbox"
                  id="terms"
                  required
                  className="mt-1 accent-[#005c39]"
                />
                <label htmlFor="terms" className="text-[11px] text-gray-500 leading-tight">
                  I agree to the <Link to="/terms" className="text-[#005c39] font-bold underline">Terms</Link> and <Link to="/privacy" className="text-[#005c39] font-bold underline">Privacy Policy</Link>. 
                  I understand this is a portal based on official NRS data.
                </label>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#005c39] text-white py-4 rounded-xl font-bold hover:bg-[#004a2e] transition-all transform active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-green-900/10"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  'Create My Account'
                )}
              </button>
            </form>
          </div>

          <p className="mt-8 text-center text-gray-500 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-[#005c39] font-bold hover:underline">
              Sign in here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;