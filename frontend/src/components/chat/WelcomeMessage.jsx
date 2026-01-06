
import React from 'react';
import { FiFileText, FiTrendingUp, FiBriefcase, FiCalendar, FiMapPin } from 'react-icons/fi';

const WelcomeMessage = ({ onQuickTopicSelect }) => {
  const quickTopics = [
    {
      id: 'vat',
      title: 'VAT Changes',
      icon: FiTrendingUp,
      question: 'What are the new VAT rates?',
      description: 'Value Added Tax adjustments and implications'
    },
    {
      id: 'small-business',
      title: 'Small Businesses',
      icon: FiBriefcase,
      question: 'How will small businesses be affected?',
      description: 'SME exemptions and simplified procedures'
    },
    {
      id: 'timeline',
      title: 'Implementation Timeline',
      icon: FiCalendar,
      question: 'When do the new tax changes start?',
      description: 'Schedule and transition periods'
    },
    {
      id: 'states',
      title: 'State Revenue Sharing',
      icon: FiMapPin,
      question: 'Which states benefit the most?',
      description: 'Revenue allocation and state benefits'
    }
  ];

  const handleTopicClick = (question) => {
    if (onQuickTopicSelect) {
      onQuickTopicSelect(question);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8">
      {/* Official Header */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-md bg-primary/10 text-primary mb-4">
          <FiFileText size={32} />
        </div>
        <h2 className="text-2xl font-bold text-text mb-3">
          Nigeria Tax Reform Bills 
        </h2>
        <p className="text-text-light max-w-2xl mx-auto">
          Official Q&A Assistant for the 2024 Tax Reform Legislation
        </p>
        <div className="mt-3 h-px w-24 bg-border mx-auto"></div>
      </div>

      {/* Quick topics with official styling */}
      <div className="professional-card p-6 mb-8">
        <h3 className="font-semibold text-text mb-4 text-lg">Common Inquiries</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {quickTopics.map((topic) => {
            const Icon = topic.icon;
            return (
              <button
                key={topic.id}
                onClick={() => handleTopicClick(topic.question)}
                className="group text-left p-4 border border-border hover:border-primary rounded-md transition-all duration-200 hover:shadow-sm"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                    <Icon size={18} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-text mb-1">{topic.title}</h4>
                    <p className="text-sm text-text-light mb-2">{topic.description}</p>
                    <div className="text-primary text-sm font-medium flex items-center gap-1">
                      Ask about this
                      <span className="group-hover:translate-x-1 transition-transform">→</span>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Example questions with document styling */}
      <div className="professional-card p-6">
        <h3 className="font-semibold text-text mb-4">Example Questions You Can Ask:</h3>
        <div className="space-y-3">
          {quickTopics.map((topic) => (
            <button
              key={`example-${topic.id}`}
              onClick={() => handleTopicClick(topic.question)}
              className="block w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 border border-transparent hover:border-primary rounded-md transition-all text-sm"
            >
              <span className="text-text">{topic.question}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Official Disclaimer */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <div className="flex items-start gap-3">
          <div className="text-blue-500 mt-0.5">:information_source:</div>
          <div className="flex-1">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">Disclaimer:</span> This assistant provides informational answers based on available tax reform documents. The information here is for general guidance only and should not be considered as legal or tax advice. For specific tax matters, please consult a qualified tax professional or the Federal Inland Revenue Service (FIRS).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeMessage;
