import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowLeft, FiShield } from 'react-icons/fi';

const Terms = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-6">
      <div className="max-w-3xl mx-auto bg-white rounded-3xl shadow-sm border p-8 md:p-12">
        <Link to="/signup" className="flex items-center gap-2 text-[#005c39] font-bold mb-8">
          <FiArrowLeft /> Back to Signup
        </Link>
        
        <h1 className="text-3xl font-bold mb-6 flex items-center gap-3">
          <FiShield className="text-[#005c39]" /> Terms of Service
        </h1>
        
        <div className="prose prose-green text-gray-600 space-y-6">
          <section>
            <h2 className="text-xl font-bold text-gray-800">1. Purpose</h2>
            <p>TaxAble AI is an educational tool designed to help Nigerians understand the Tax Reform Bills. It provides information based on official NRS documents.</p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-800">2. Not Legal Advice</h2>
            <p className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400 text-yellow-800">
              <strong>Warning:</strong> While our AI is trained on official laws, its responses should not be taken as professional legal or financial advice. Always consult a certified tax professional for official filings.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-bold text-gray-800">3. Data Accuracy</h2>
            <p>We use RAG (Retrieval-Augmented Generation) to ensure high accuracy. However, AI can occasionally hallucinate. Please check the "Source Citations" provided in the chat for confirmation.</p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Terms;