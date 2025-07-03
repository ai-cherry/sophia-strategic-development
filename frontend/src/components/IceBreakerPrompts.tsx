import React from 'react';
import { 
  ChartBarIcon, 
  CodeBracketIcon, 
  CurrencyDollarIcon,
  UserGroupIcon,
  LightBulbIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface IceBreakerPrompt {
  id: string;
  category: string;
  prompt: string;
  icon: React.ComponentType<any>;
  focusMode?: 'business' | 'code' | 'data';
}

interface IceBreakerPromptsProps {
  onPromptSelect: (prompt: string, focusMode?: string) => void;
}

export const IceBreakerPrompts: React.FC<IceBreakerPromptsProps> = ({ onPromptSelect }) => {
  const prompts: IceBreakerPrompt[] = [
    {
      id: 'revenue-analysis',
      category: 'Business Intelligence',
      prompt: 'What were our top revenue drivers last quarter?',
      icon: CurrencyDollarIcon,
      focusMode: 'business'
    },
    {
      id: 'customer-health',
      category: 'Customer Insights',
      prompt: 'Show me customers at risk of churning',
      icon: UserGroupIcon,
      focusMode: 'data'
    },
    {
      id: 'sales-performance',
      category: 'Sales Analytics',
      prompt: 'How is my sales team performing this month?',
      icon: ChartBarIcon,
      focusMode: 'business'
    },
    {
      id: 'code-refactor',
      category: 'Code Assistance',
      prompt: 'Help me refactor this function to be more efficient',
      icon: CodeBracketIcon,
      focusMode: 'code'
    },
    {
      id: 'strategic-planning',
      category: 'Strategic Insights',
      prompt: 'What market trends should we be aware of?',
      icon: LightBulbIcon,
      focusMode: 'business'
    },
    {
      id: 'time-sensitive',
      category: 'Urgent Matters',
      prompt: 'What needs my immediate attention today?',
      icon: ClockIcon,
      focusMode: 'business'
    }
  ];

  const groupedPrompts = prompts.reduce((acc, prompt) => {
    if (!acc[prompt.category]) {
      acc[prompt.category] = [];
    }
    acc[prompt.category].push(prompt);
    return acc;
  }, {} as Record<string, IceBreakerPrompt[]>);

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">
          How can I help you today?
        </h2>
        <p className="text-gray-600">
          Choose a prompt to get started or type your own question
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(groupedPrompts).map(([category, categoryPrompts]) => (
          <div key={category} className="space-y-3">
            <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
              {category}
            </h3>
            {categoryPrompts.map((prompt) => (
              <button
                key={prompt.id}
                onClick={() => onPromptSelect(prompt.prompt, prompt.focusMode)}
                className="w-full text-left p-4 bg-white rounded-lg border border-gray-200 
                         hover:border-blue-400 hover:shadow-md transition-all duration-200
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <div className="flex items-start space-x-3">
                  <prompt.icon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700 leading-relaxed">
                    {prompt.prompt}
                  </span>
                </div>
              </button>
            ))}
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          Or start typing your question in the chat below
        </p>
      </div>
    </div>
  );
};

// Dynamic prompts based on time of day and context
export const useDynamicPrompts = (userContext?: any) => {
  const getTimeBasedPrompts = (): IceBreakerPrompt[] => {
    const hour = new Date().getHours();
    const dayOfWeek = new Date().getDay();
    
    const prompts: IceBreakerPrompt[] = [];
    
    // Morning prompts (6 AM - 12 PM)
    if (hour >= 6 && hour < 12) {
      prompts.push({
        id: 'morning-brief',
        category: 'Daily Brief',
        prompt: 'Give me my morning business briefing',
        icon: ClockIcon,
        focusMode: 'business'
      });
    }
    
    // Monday prompts
    if (dayOfWeek === 1) {
      prompts.push({
        id: 'weekly-planning',
        category: 'Weekly Planning',
        prompt: 'What are the key priorities for this week?',
        icon: LightBulbIcon,
        focusMode: 'business'
      });
    }
    
    // Friday prompts
    if (dayOfWeek === 5) {
      prompts.push({
        id: 'weekly-review',
        category: 'Weekly Review',
        prompt: 'Summarize this week\'s key achievements and issues',
        icon: ChartBarIcon,
        focusMode: 'business'
      });
    }
    
    return prompts;
  };
  
  return { getTimeBasedPrompts };
}; 