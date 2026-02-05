import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowLeft, FiLock, FiEyeOff, FiDatabase } from 'react-icons/fi';

const Privacy = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-6 font-sans">
      <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-sm border border-gray-100 p-8 md:p-12">
        <Link to="/signup" className="flex items-center gap-2 text-[#005c39] font-bold mb-8 hover:gap-3 transition-all">
          <FiArrowLeft /> Back to Signup
        </Link>
        
        <header className="mb-10">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FiLock className="text-[#005c39]" /> Privacy Policy
          </h1>
          <p className="text-gray-500 mt-2">Last updated: January 2026</p>
        </header>
        
        <div className="space-y-8 text-gray-600 leading-relaxed">
          <section>
            <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
              <FiDatabase className="text-[#005c39]" size={18} /> 1. Data Collection
            </h2>
            <p>
              We only collect the information necessary to provide you with tax insights. This includes your email and username. Your chat history is stored so you can refer back to previous tax queries.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
              <FiEyeOff className="text-[#005c39]" size={18} /> 2. Data Usage
            </h2>
            <p>
              Your data is never sold to third parties. We use your information strictly to:
            </p>
            <ul className="list-disc ml-6 mt-3 space-y-2">
              <li>Personalize your TaxAble AI experience.</li>
              <li>Improve our AI's understanding of Nigerian tax questions.</li>
              <li>Maintain the security of your account.</li>
            </ul>
          </section>

          <section className="bg-green-50 p-6 rounded-2xl border border-green-100">
            <h2 className="text-lg font-bold text-[#005c39] mb-2">Security Note</h2>
            <p className="text-sm text-green-800">
              We use industry-standard encryption to protect your account. However, please do not share sensitive personal financial documents (like bank statements or NIN) directly in the chat.
            </p>
          </section>

          <section className="pt-6 border-t border-gray-100">
            <p className="text-sm text-gray-400 italic">
              Note: This is an educational project built for the Capstone requirements. While we treat data with care, this is not a commercial government-certified database.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Privacy;