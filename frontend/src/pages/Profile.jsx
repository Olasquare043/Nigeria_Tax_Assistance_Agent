import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  FiUser, FiMail, FiEdit2, FiSave, FiX, FiLock, 
  FiArrowLeft, FiAlertCircle, FiCheckCircle,
  FiCalendar, FiShield
} from 'react-icons/fi';

const Profile = () => {
  const { user, updateProfile, changePassword, logout } = useAuth();
  const navigate = useNavigate();
  
  const [editMode, setEditMode] = useState(false);
  const [changePasswordMode, setChangePasswordMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [profileData, setProfileData] = useState({
    full_name: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  useEffect(() => {
    if (user) {
      setProfileData({
        full_name: user.full_name || ''
      });
    }
  }, [user]);

  if (!user) {
    navigate('/login');
    return null;
  }

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    
    if (!profileData.full_name.trim()) {
      setError('Full name cannot be empty');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await updateProfile(profileData);
      
      if (result.success) {
        setSuccess('Profile updated successfully!');
        setEditMode(false);
      } else {
        setError(result.error || 'Failed to update profile.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (!passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password) {
      setError('Please fill in all password fields');
      return;
    }
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }
    
    if (passwordData.new_password.length < 6) {
      setError('New password must be at least 6 characters');
      return;
    }

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const result = await changePassword(
        passwordData.current_password,
        passwordData.new_password
      );
      
      if (result.success) {
        setSuccess('Password changed successfully!');
        setChangePasswordMode(false);
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      } else {
        setError(result.error || 'Failed to change password.');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <FiArrowLeft className="text-white" size={18} />
              </div>
              <span className="text-gray-700 font-medium">Back to Dashboard</span>
            </Link>
            <button
              onClick={handleLogout}
              className="text-red-600 hover:text-red-800 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {/* Left Column - Profile Info */}
            <div className="md:col-span-2">
              <div className="bg-white rounded-2xl shadow-lg p-8">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
                    <p className="text-gray-600 mt-1">Manage your account information</p>
                  </div>
                  {!editMode && !changePasswordMode && (
                    <button
                      onClick={() => setEditMode(true)}
                      className="flex items-center gap-2 text-primary hover:text-primary-dark font-medium"
                    >
                      <FiEdit2 /> Edit Profile
                    </button>
                  )}
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

                {/* Profile Form */}
                {editMode ? (
                  <form onSubmit={handleProfileUpdate} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Email Address
                        </label>
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
                          <FiMail className="text-gray-400" />
                          <span className="text-gray-700">{user.email}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Username
                        </label>
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border">
                          <FiUser className="text-gray-400" />
                          <span className="text-gray-700">{user.username}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Username cannot be changed</p>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={profileData.full_name}
                        onChange={(e) => setProfileData({...profileData, full_name: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                        placeholder="Enter your full name"
                        disabled={loading}
                      />
                    </div>

                    <div className="flex gap-4 pt-4">
                      <button
                        type="button"
                        onClick={() => setEditMode(false)}
                        className="flex-1 border-2 border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
                        disabled={loading}
                      >
                        <FiX /> Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 bg-primary text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {loading ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Saving...
                          </>
                        ) : (
                          <>
                            <FiSave /> Save Changes
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                ) : changePasswordMode ? (
                  <form onSubmit={handlePasswordChange} className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Current Password
                      </label>
                      <div className="relative">
                        <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="password"
                          value={passwordData.current_password}
                          onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                          placeholder="Enter current password"
                          required
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        New Password
                      </label>
                      <div className="relative">
                        <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="password"
                          value={passwordData.new_password}
                          onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                          placeholder="At least 6 characters"
                          required
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confirm New Password
                      </label>
                      <div className="relative">
                        <FiLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="password"
                          value={passwordData.confirm_password}
                          onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-colors"
                          placeholder="Confirm new password"
                          required
                          disabled={loading}
                        />
                      </div>
                    </div>

                    <div className="flex gap-4 pt-4">
                      <button
                        type="button"
                        onClick={() => setChangePasswordMode(false)}
                        className="flex-1 border-2 border-gray-300 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
                        disabled={loading}
                      >
                        <FiX /> Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 bg-primary text-white py-3 px-4 rounded-lg font-medium hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                      >
                        {loading ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Changing...
                          </>
                        ) : (
                          'Change Password'
                        )}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-8">
                    {/* Profile Info Display */}
                    <div className="grid md:grid-cols-2 gap-6">
                      <div className="bg-gray-50 p-6 rounded-xl">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                            <FiUser className="text-primary" size={20} />
                          </div>
                          <div>
                            <h3 className="font-bold text-gray-900">{user.full_name || 'Not set'}</h3>
                            <p className="text-sm text-gray-600">{user.username}</p>
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">
                          Your display name for the Tax Reform Assistant
                        </p>
                      </div>

                      <div className="bg-gray-50 p-6 rounded-xl">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                            <FiMail className="text-green-600" size={20} />
                          </div>
                          <div>
                            <h3 className="font-bold text-gray-900">Email</h3>
                            <p className="text-sm text-gray-600 break-all">{user.email}</p>
                          </div>
                        </div>
                        <p className="text-sm text-gray-500">
                          Used for login and notifications
                        </p>
                      </div>
                    </div>

                    {/* Account Details */}
                    <div className="border-t pt-8">
                      <h3 className="text-lg font-bold text-gray-900 mb-4">Account Details</h3>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                          <FiCalendar className="text-gray-400" />
                          <div>
                            <p className="text-sm text-gray-500">Member since</p>
                            <p className="font-medium text-gray-900">
                              {formatDate(user.created_at)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg">
                          <FiShield className="text-gray-400" />
                          <div>
                            <p className="text-sm text-gray-500">Account Status</p>
                            <p className="font-medium text-gray-900">
                              {user.is_verified ? 'Verified ✓' : 'Pending verification'}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right Column - Actions & Security */}
            <div className="space-y-6">
              {/* Security Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Security</h3>
                <div className="space-y-4">
                  <button
                    onClick={() => {
                      setEditMode(false);
                      setChangePasswordMode(true);
                    }}
                    className="w-full flex items-center justify-between p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-100 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <FiLock className="text-blue-600" />
                      <span className="font-medium text-gray-900">Change Password</span>
                    </div>
                    <FiArrowLeft className="text-gray-400 transform rotate-180" />
                  </button>
                  
                  <Link
                    to="/forgot-password"
                    className="block w-full text-center p-3 bg-gray-50 hover:bg-gray-100 rounded-lg border transition-colors text-gray-700 font-medium"
                  >
                    Reset Password
                  </Link>
                </div>
              </div>

              {/* Account Actions Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Account Actions</h3>
                <div className="space-y-3">
                  <Link
                    to="/dashboard"
                    className="block w-full text-center p-3 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg font-medium transition-colors"
                  >
                    Go to Chat Dashboard
                  </Link>
                  
                  <button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to logout?')) {
                        handleLogout();
                      }
                    }}
                    className="w-full p-3 bg-red-50 text-red-600 hover:bg-red-100 rounded-lg font-medium transition-colors"
                  >
                    Logout Account
                  </button>
                </div>
              </div>

              {/* Quick Stats Card */}
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Account Type</span>
                    <span className="font-medium text-gray-900">Standard</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Data Usage</span>
                    <span className="font-medium text-gray-900">Unlimited</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-600">Support</span>
                    <span className="font-medium text-gray-900">Available</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;