import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiArrowRight, FiBook, FiCheckCircle, FiMessageSquare, FiShield, FiUsers } from 'react-icons/fi';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <FiBook className="text-white" size={18} />
              </div>
              <span className="text-xl font-bold text-gray-800">Tax Reform Assistant</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link 
                to="/login" 
                className="text-gray-600 hover:text-primary font-medium transition-colors"
              >
                Login
              </Link>
              <Link 
                to="/signup" 
                className="bg-primary text-white px-5 py-2 rounded-lg font-medium hover:bg-primary-dark transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Understand Nigerian Tax Reform 
              <span className="text-primary block">Made Simple</span>
            </h1>
            <p className="text-lg md:text-xl text-gray-600 mb-10 max-w-3xl mx-auto">
              Get clear, accurate answers about the 2024 Tax Reform Bills from official documents. 
              No legal jargon, no confusion—just straight answers you can trust.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/signup')}
                className="bg-primary text-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-primary-dark transition-colors flex items-center justify-center gap-2"
              >
                Start Asking Questions <FiArrowRight />
              </button>
              <button
                onClick={() => navigate('/login')}
                className="bg-white text-primary border-2 border-primary px-8 py-4 rounded-xl text-lg font-semibold hover:bg-primary hover:text-white transition-colors"
              >
                Sign In
              </button>
            </div>
            <p className="text-gray-500 text-sm mt-4">
              No credit card required • Start chatting immediately
            </p>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            The Problem We're Solving
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <div className="bg-red-50 p-8 rounded-2xl border border-red-100">
              <div className="text-red-500 mb-4">
                <FiUsers size={32} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Confusion Everywhere</h3>
              <p className="text-gray-600">
                Over <strong>200 million Nigerians</strong> are affected by the tax reforms, but few understand 
                what the changes mean for them. Misinformation spreads faster than facts.
              </p>
              <ul className="mt-4 space-y-2">
                <li className="flex items-start">
                  <FiCheckCircle className="text-red-500 mt-1 mr-2 flex-shrink-0" />
                  <span>500+ pages of complex legal language</span>
                </li>
                <li className="flex items-start">
                  <FiCheckCircle className="text-red-500 mt-1 mr-2 flex-shrink-0" />
                  <span>Conflicting information on social media</span>
                </li>
                <li className="flex items-start">
                  <FiCheckCircle className="text-red-500 mt-1 mr-2 flex-shrink-0" />
                  <span>No simple way to get accurate answers</span>
                </li>
              </ul>
            </div>
            
            <div className="bg-blue-50 p-8 rounded-2xl border border-blue-100">
              <div className="text-blue-500 mb-4">
                <FiMessageSquare size={32} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Real Questions, Real People</h3>
              <p className="text-gray-600">
                Everyday Nigerians are searching for answers to life-changing questions about taxes, 
                but struggle to find reliable information.
              </p>
              <div className="mt-6 space-y-4">
                <div className="bg-white p-4 rounded-lg border">
                  <p className="text-gray-800 italic">"Will I pay more tax under the new law?"</p>
                  <p className="text-sm text-gray-500 mt-1">— Aunty Ngozi, small business owner</p>
                </div>
                <div className="bg-white p-4 rounded-lg border">
                  <p className="text-gray-800 italic">"How does VAT derivation affect my state's revenue?"</p>
                  <p className="text-sm text-gray-500 mt-1">— Governor Yahaya, state governor</p>
                </div>
                <div className="bg-white p-4 rounded-lg border">
                  <p className="text-gray-800 italic">"What documents do I need for the new tax filing?"</p>
                  <p className="text-sm text-gray-500 mt-1">— Chidi, software developer</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How Our AI Assistant Helps
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <FiBook className="text-primary" size={24} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Official Sources Only</h3>
              <p className="text-gray-600">
                Answers are sourced directly from the 4 Tax Reform Bills, official government documents, 
                and verified memoranda.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <FiShield className="text-primary" size={24} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Citation & Verification</h3>
              <p className="text-gray-600">
                Every answer includes citations showing exactly which document and page the information 
                comes from.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <FiMessageSquare className="text-primary" size={24} />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Simple Conversation</h3>
              <p className="text-gray-600">
                Ask questions in plain English. Our AI understands context and provides follow-up 
                explanations when needed.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Understand Your Taxes?</h2>
          <p className="text-xl mb-10 max-w-2xl mx-auto opacity-90">
            Join thousands of Nigerians who are getting clear answers about the tax reforms.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/signup')}
              className="bg-white text-primary px-8 py-4 rounded-xl text-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Start Free Today
            </button>
            <button
              onClick={() => navigate('/login')}
              className="bg-transparent border-2 border-white px-8 py-4 rounded-xl text-lg font-semibold hover:bg-white/10 transition-colors"
            >
              Sign In to Continue
            </button>
          </div>
          <p className="mt-6 text-white/80">
            No installation needed • Works on any device • Private and secure
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <FiBook size={18} />
                </div>
                <span className="text-xl font-bold">Tax Reform Assistant</span>
              </div>
              <p className="text-gray-400">
                Making Nigerian tax reform understandable for everyone.
              </p>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/" className="hover:text-white transition-colors">Home</Link></li>
                <li><Link to="/login" className="hover:text-white transition-colors">Login</Link></li>
                <li><Link to="/signup" className="hover:text-white transition-colors">Sign Up</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Documents</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Finance Bill 2024</li>
                <li>Tax Reform Act</li>
                <li>VAT Amendment</li>
                <li>Official Memoranda</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-bold mb-4">Disclaimer</h4>
              <p className="text-gray-400 text-sm">
                This tool provides information based on official documents but does not constitute 
                legal or financial advice. Always consult a qualified professional for personal tax matters.
              </p>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>© {new Date().getFullYear()} Nigeria Tax Reform Q&A Assistant. Capstone Project.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;