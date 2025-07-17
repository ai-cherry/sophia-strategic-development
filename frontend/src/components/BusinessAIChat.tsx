import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, TrendingUp, Users, Target, BarChart3 } from 'lucide-react';
import { BusinessQuery, BusinessResponse } from './types/BusinessTypes';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  insights?: string[];
  recommendations?: string[];
  confidence?: number;
  processingTime?: number;
}

const BusinessAIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string>('auto');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const agentTypes = [
    { id: 'auto', name: 'Auto-Route', icon: Bot, description: 'Automatically routes to best agent' },
    { id: 'revenue', name: 'Revenue', icon: TrendingUp, description: 'Revenue analysis and forecasting' },
    { id: 'team', name: 'Team', icon: Users, description: 'Team performance and productivity' },
    { id: 'customer', name: 'Customer', icon: Target, description: 'Customer intelligence and satisfaction' },
    { id: 'market', name: 'Market', icon: BarChart3, description: 'Market analysis and competitive intelligence' }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call business AI orchestrator through existing Sophia backend
      const query: BusinessQuery = {
        query: inputValue,
        user_id: 'current_user', // Get from auth context
        department: undefined,
        priority: 'normal',
        context: { selectedAgent }
      };

      const response = await fetch('/api/business-ai/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(query)
      });

      const businessResponse: BusinessResponse = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: businessResponse.response,
        timestamp: new Date(),
        insights: businessResponse.insights,
        recommendations: businessResponse.recommendations,
        confidence: businessResponse.confidence,
        processingTime: businessResponse.processing_time_ms
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error calling business AI:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatConfidence = (confidence?: number) => {
    if (!confidence) return '';
    return `${(confidence * 100).toFixed(0)}% confidence`;
  };

  const formatProcessingTime = (ms?: number) => {
    if (!ms) return '';
    return `${ms}ms`;
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Agent Selection Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Business AI Assistant
          </h2>
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600 dark:text-gray-400">Agent:</label>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="px-3 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {agentTypes.map(agent => (
                <option key={agent.id} value={agent.id}>
                  {agent.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Agent Descriptions */}
        <div className="mt-2 grid grid-cols-2 md:grid-cols-5 gap-2">
          {agentTypes.map(agent => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.id}
                className={`p-2 rounded-lg border cursor-pointer transition-colors ${
                  selectedAgent === agent.id
                    ? 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-700'
                    : 'bg-gray-50 border-gray-200 dark:bg-gray-700 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600'
                }`}
                onClick={() => setSelectedAgent(agent.id)}
              >
                <div className="flex items-center space-x-2">
                  <Icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="text-xs font-medium text-gray-900 dark:text-white">
                    {agent.name}
                  </span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  {agent.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Business Intelligence at Your Fingertips
            </h3>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
              Ask me about revenue, team performance, customer insights, or market analysis. 
              I'll route your question to the best AI agent and provide actionable intelligence.
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <button
                onClick={() => setInputValue("How is our revenue performing this quarter?")}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
              >
                Revenue Performance
              </button>
              <button
                onClick={() => setInputValue("What's our team productivity looking like?")}
                className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200 transition-colors"
              >
                Team Productivity
              </button>
              <button
                onClick={() => setInputValue("How satisfied are our customers?")}
                className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200 transition-colors"
              >
                Customer Satisfaction
              </button>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-start space-x-3">
                {message.type === 'ai' && (
                  <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400 mt-1 flex-shrink-0" />
                )}
                {message.type === 'user' && (
                  <User className="w-6 h-6 text-white mt-1 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <div
                    className={`prose max-w-none ${
                      message.type === 'user' ? 'text-white' : 'text-gray-900 dark:text-white'
                    }`}
                    dangerouslySetInnerHTML={{
                      __html: message.content.replace(/\n/g, '<br />')
                    }}
                  />

                  {/* AI Response Metadata */}
                  {message.type === 'ai' && (
                    <div className="mt-4 space-y-3">
                      {/* Insights */}
                      {message.insights && message.insights.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Key Insights:
                          </h4>
                          <ul className="space-y-1">
                            {message.insights.map((insight, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                {insight}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Recommendations */}
                      {message.recommendations && message.recommendations.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Recommendations:
                          </h4>
                          <ul className="space-y-1">
                            {message.recommendations.map((rec, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start">
                                <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Processing Info */}
                      <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{formatConfidence(message.confidence)}</span>
                        <span>{formatProcessingTime(message.processingTime)}</span>
                        <span>{message.timestamp.toLocaleTimeString()}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask about business performance, metrics, or insights..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default BusinessAIChat; 