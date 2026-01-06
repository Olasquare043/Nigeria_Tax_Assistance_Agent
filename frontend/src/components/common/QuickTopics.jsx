
import React from 'react';
import { FiTrendingUp, FiBookOpen, FiCalendar, FiMapPin } from 'react-icons/fi';

const QuickTopics = ({ onSelectTopic }) => {
  const topics = [
    {
      id: 'vat',
      label: 'VAT Changes',
      icon: FiTrendingUp,
      question: 'What are the new VAT rates?'
    },
    {
      id: 'small-business',
      label: 'Small Businesses',
      icon: FiBookOpen,
      question: 'How will small businesses be affected?'
    },
    {
      id: 'timeline',
      label: 'Implementation Timeline',
      icon: FiCalendar,
      question: 'When do the new tax changes start?'
    },
    {
      id: 'states',
      label: 'State Benefits',
      icon: FiMapPin,
      question: 'Which states benefit the most?'
    }
  ];

  const handleClick = (question) => {
    if (onSelectTopic) {
      onSelectTopic(question);
    }
  };

  return (
    <div>
      <h3 className="font-semibold text-text mb-3">Quick Topics</h3>
      <div className="space-y-2">
        {topics.map((topic) => {
          const Icon = topic.icon;
          return (
            <button
              key={topic.id}
              onClick={() => handleClick(topic.question)}
              className="flex items-center gap-3 w-full p-3 text-left bg-gray-50 hover:bg-primary/5 hover:border-primary border border-transparent rounded-lg transition-all group"
            >
              <div className="p-1.5 rounded-md bg-primary/10 text-primary group-hover:bg-primary group-hover:text-white">
                <Icon size={16} />
              </div>
              <span className="text-sm font-medium text-text">{topic.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default QuickTopics;
