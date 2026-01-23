import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  FiArrowRight, 
  FiBook, 
  FiCheckCircle, 
  FiMessageSquare, 
  FiShield, 
  FiUsers, 
  FiGlobe, 
  FiAlertTriangle, 
  FiFileText,
  FiSearch
} from 'react-icons/fi';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* TOP UTILITY BAR - Original Green */}
      <div className="bg-[#005c39] text-white py-2 text-[10px] md:text-xs">
        <div className="container mx-auto px-6 flex justify-between items-center opacity-90 tracking-widest uppercase">
          <div className="flex gap-6">
            <span>Official Reform Portal</span>
          </div>
          <div className="flex items-center gap-2">
            <FiGlobe /> FEDERAL REPUBLIC OF NIGERIA
          </div>
        </div>
      </div>

      {/* NAVIGATION - Logo placed here */}
      <nav className="bg-white py-4 border-b sticky top-0 z-50">
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-[#005c39] rounded-lg flex items-center justify-center text-white">
                <FiBook size={18} />
              </div>
              <span className="text-xl font-bold text-gray-800 tracking-tight">TaxAble AI</span>
            </div>
            
            {/* NRS Logo Integration - UPDATED */}
            <div className="h-6 w-px bg-gray-200 hidden md:block"></div>
            <div className="hidden md:flex items-center gap-2">
              <img 
                src="/nrs-logo.png" 
                alt="NRS Logo" 
                className="w-10 h-10 object-contain" 
              />
              <span className="text-[10px] leading-tight font-bold text-gray-500 uppercase tracking-tighter">
                Nigeria <br/> Revenue Service
              </span>
            </div>
          </div>
          
          <div className="hidden md:flex items-center space-x-6 text-sm font-semibold uppercase tracking-wider">
            <Link to="/login" className="text-gray-600 hover:text-[#005c39]">Login</Link>
            <button 
              onClick={() => navigate('/signup')}
              className="bg-[#005c39] text-white px-5 py-2 rounded-md hover:bg-opacity-90 transition-all flex items-center gap-2 shadow-sm"
            >
              Get Started <FiArrowRight size={14} />
            </button>
          </div>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section className="bg-[#005c39] text-white py-16 lg:py-24 relative overflow-hidden">
        <div className="container mx-auto px-6 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2">
              <h1 className="text-5xl lg:text-7xl font-serif font-medium leading-tight mb-6">
                Understand Nigerian <br />
                <span className="text-accent text-yellow-400">Tax Bills</span> Made Simple.
              </h1>
              <p className="text-gray-100 text-lg max-w-lg mb-10 leading-relaxed opacity-90">
                Get accurate, easy to understand answers about the Tax Reform Bills based strictly on official documents from the NRS and Federal Government.
              </p>
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={() => navigate('/signup')}
                  className="bg-white text-[#005c39] px-8 py-4 rounded-xl text-lg font-bold hover:bg-gray-100 transition-all flex items-center gap-2 shadow-xl"
                >
                  Start Asking Questions <FiArrowRight />
                </button>
              </div>
            </div>

            {/* UPDATED CARD: Replacing highlights with common questions */}
            <div className="lg:w-1/2 w-full max-w-xl">
              <div className="bg-white text-gray-900 p-8 lg:p-12 rounded-2xl shadow-2xl border-t-4 border-[#005c39]">
                <h2 className="text-2xl font-bold uppercase tracking-widest mb-8 text-[#005c39] border-b pb-4">
                  Common Questions
                </h2>
                <div className="space-y-4">
                  {[
                    "Will my personal income tax increase?",
                    "Do small businesses still pay Company Tax?",
                    "How does the new VAT affect food items?",
                    "What happens to my state's revenue?"
                  ].map((question, index) => (
                    <button 
                      key={index}
                      onClick={() => navigate('/signup')}
                      className="w-full text-left p-4 rounded-xl border border-gray-100 hover:border-[#005c39] hover:bg-green-50 transition-all group flex justify-between items-center"
                    >
                      <span className="text-sm font-medium text-gray-700 group-hover:text-[#005c39]">{question}</span>
                      <FiArrowRight className="text-gray-300 group-hover:text-[#005c39]" size={16} />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PROBLEM SECTION */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <h2 className="text-4xl font-serif font-bold text-center text-gray-900 mb-16">
            The Problem We're Solving
          </h2>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <div className="bg-red-50 p-10 rounded-2xl border border-red-100">
              <FiUsers className="text-red-500 mb-6" size={40} />
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Information Vacuum</h3>
              <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                Over 200 million Nigerians are affected, but misinformation spreads faster than official facts.
              </p>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-center gap-2"><FiCheckCircle className="text-red-500" /> 500+ pages of legal jargon</li>
                <li className="flex items-center gap-2"><FiCheckCircle className="text-red-500" /> Conflicting social media info</li>
              </ul>
            </div>

            <div className="bg-orange-50 p-10 rounded-2xl border border-orange-100">
              <FiAlertTriangle className="text-orange-500 mb-6" size={40} />
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Multiple Taxation</h3>
              <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                Small businesses face 60+ taxes. The new NRS system unifies these, but many don't know how it works.
              </p>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-center gap-2"><FiCheckCircle className="text-orange-500" /> Overlapping tax jurisdictions</li>
                <li className="flex items-center gap-2"><FiCheckCircle className="text-orange-500" /> Confusing state vs federal rules</li>
              </ul>
            </div>

            <div className="bg-purple-50 p-10 rounded-2xl border border-purple-100">
              <FiFileText className="text-purple-500 mb-6" size={40} />
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Compliance Gap</h3>
              <p className="text-gray-600 mb-6 leading-relaxed text-sm">
                Many qualify for 0% tax rates but miss out because of the high cost of legal consultants.
              </p>
              <ul className="space-y-3 text-sm text-gray-600">
                <li className="flex items-center gap-2"><FiCheckCircle className="text-purple-500" /> Unknown tax exemptions</li>
                <li className="flex items-center gap-2"><FiCheckCircle className="text-purple-500" /> Complex filing procedures</li>
              </ul>
            </div>

            <div className="bg-blue-50 p-10 rounded-2xl border border-blue-100">
              <FiMessageSquare className="text-blue-500 mb-6" size={40} />
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Real Questions</h3>
              <div className="space-y-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100 italic text-sm text-gray-700">
                  "How does the VAT derivation affect my state's revenue?" 
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100 italic text-sm text-gray-400">
                  — Public Official
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section className="py-24 bg-gray-50 border-t">
        <div className="container mx-auto px-6">
          <h3 className="text-4xl font-serif font-bold text-gray-900 text-center mb-16">Built for Accuracy</h3>
          <div className="grid md:grid-cols-3 gap-12 max-w-6xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-white text-[#005c39] rounded-full flex items-center justify-center mb-6 mx-auto shadow-sm">
                <FiShield size={32} />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Verified Citations</h4>
              <p className="text-gray-600 text-sm leading-relaxed">Every answer includes the specific Bill, Section, and Page number.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-white text-[#005c39] rounded-full flex items-center justify-center mb-6 mx-auto shadow-sm">
                <FiSearch size={32} />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">4-Bill Context</h4>
              <p className="text-gray-600 text-sm leading-relaxed">Analyzed across all four New Reform Bills simultaneously for 100% accuracy.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-white text-[#005c39] rounded-full flex items-center justify-center mb-6 mx-auto shadow-sm">
                <FiBook size={32} />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">Citizen Friendly</h4>
              <p className="text-gray-600 text-sm leading-relaxed">Translating complex legal language into simple English and actionable advice.</p>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-[#005c39] text-white py-16 border-t border-white/10">
        <div className="container mx-auto px-6">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center space-x-2 mb-6">
              <FiBook className="text-white" size={24} />
              <span className="text-2xl font-bold">TaxAble AI</span>
            </div>
            <p className="text-gray-100 text-sm max-w-md mb-10 opacity-80 leading-relaxed">
              Empowering Nigerians with clarity on the New Tax Reform Bills. 
              Bridging the gap between legislation and understanding.
            </p>
            <div className="flex gap-8 mb-10 text-sm font-semibold uppercase tracking-widest opacity-70">
              <Link to="/login" className="hover:text-yellow-400">Portal Login</Link>
              <Link to="/signup" className="hover:text-yellow-400">Join Now</Link>
            </div>
            <div className="w-full border-t border-white/10 pt-8 text-[10px] md:text-xs text-gray-300 uppercase tracking-widest">
              © {new Date().getFullYear()} TaxAble AI • Supported by NRS Official Data
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;