import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: string[];
  insights?: string[];
  recommendations?: string[];
  metadata?: {
    provider: string;
    model_used: string;
    response_time: number;
    session_id: string;
    conversation_length: number;
  };
}

interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  services: {
    api: {
      status: string;
      uptime_seconds: number;
      total_requests: number;
      success_rate: number;
    };
    chat: {
      status: string;
      active_sessions: number;
      conversation_count: number;
    };
    database: {
      status: string;
      type: string;
      note: string;
    };
  };
}

// Use environment variable or default to localhost
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const ProductionChatDashboard: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [sessionId] = useState(`session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection and get health status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await axios.get(`${BACKEND_URL}/health`);
        setHealthStatus(response.data);
        if (response.data.status === 'healthy') {
          setIsConnected(true);
          const welcomeMessage: ChatMessage = {
            role: 'system',
            content: `🚀 **Sophia AI Production v${response.data.version}** - Connected and Ready!\n\nI'm your executive AI assistant with advanced business intelligence capabilities. I can help you with:\n\n• Revenue and sales analysis\n• Project management insights\n• Team performance metrics\n• Data analytics and reporting\n• Strategic recommendations\n\nWhat would you like to explore today?`,
            timestamp: new Date().toISOString()
          };
          setMessages([welcomeMessage]);
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setIsConnected(false);
        const errorMessage: ChatMessage = {
          role: 'system',
          content: '❌ Could not connect to Sophia AI backend. Please check that the production server is running.',
          timestamp: new Date().toISOString()
        };
        setMessages([errorMessage]);
      }
    };

    checkConnection();
    
    // Refresh health status every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Send message to production backend
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${BACKEND_URL}/chat`, {
        message: inputMessage,
        user_id: 'ceo_user',
        session_id: sessionId
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        sources: response.data.sources,
        insights: response.data.insights,
        recommendations: response.data.recommendations,
        metadata: response.data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'system',
        content: '❌ Failed to send message. Please try again or check your connection.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Quick action buttons
  const quickActions = [
    { label: "Revenue Analysis", message: "What is our current revenue status?" },
    { label: "Project Status", message: "Show me our project status and deadlines" },
    { label: "Team Performance", message: "How is our team performing this quarter?" },
    { label: "System Health", message: "What is the current system status?" }
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sophia AI Production</h1>
              <p className="text-sm text-gray-600">Executive Intelligence Assistant</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-600' : 'bg-red-600'}`}></div>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              {healthStatus && (
                <span className="text-sm text-gray-500">
                  v{healthStatus.version} | {healthStatus.environment}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-4xl p-4 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'system'
                    ? 'bg-gray-200 text-gray-800'
                    : 'bg-white border shadow-sm'
                }`}
              >
                <div className="mb-2">
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded border-l-4 border-gray-400">
                    <h4 className="font-semibold text-gray-800 mb-2">📊 Data Sources:</h4>
                    <div className="flex flex-wrap gap-2">
                      {message.sources.map((source, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded">
                          {source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Insights */}
                {message.insights && message.insights.length > 0 && (
                  <div className="mt-3 p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                    <h4 className="font-semibold text-blue-800 mb-2">💡 Key Insights:</h4>
                    <ul className="space-y-1">
                      {message.insights.map((insight, i) => (
                        <li key={i} className="text-blue-700 text-sm">• {insight}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {message.recommendations && message.recommendations.length > 0 && (
                  <div className="mt-3 p-3 bg-green-50 rounded border-l-4 border-green-400">
                    <h4 className="font-semibold text-green-800 mb-2">🎯 Recommendations:</h4>
                    <ul className="space-y-1">
                      {message.recommendations.map((rec, i) => (
                        <li key={i} className="text-green-700 text-sm">• {rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Metadata */}
                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    {message.metadata && (
                      <>
                        <span>🤖 {message.metadata.provider}</span>
                        <span>⚡ {message.metadata.response_time}s</span>
                        <span>🧠 {message.metadata.model_used}</span>
                        <span>💬 {message.metadata.conversation_length} msgs</span>
                      </>
                    )}
                  </div>
                  <span>{formatTime(message.timestamp)}</span>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border shadow-sm p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <span className="text-gray-600">Sophia is analyzing...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-100 px-6 py-2">
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => setInputMessage(action.message)}
                className="px-3 py-1 bg-white text-gray-700 text-sm rounded border hover:bg-gray-50"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about revenue, projects, team performance, or any business intelligence query..."
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            💡 Try asking about revenue analysis, project status, team performance, or system health
          </div>
        </div>
      </div>

      {/* System Status Sidebar */}
      <div className="w-80 bg-white border-l p-4 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>

        {healthStatus && (
          <>
            {/* Overall Status */}
            <div className="mb-4 p-3 bg-gray-50 rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Overall Status</span>
                <span className={`font-bold ${healthStatus.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                  {healthStatus.status.toUpperCase()}
                </span>
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Version: {healthStatus.version}</div>
                <div>Environment: {healthStatus.environment}</div>
                <div>Uptime: {Math.floor(healthStatus.services.api.uptime_seconds)}s</div>
                <div>Success Rate: {healthStatus.services.api.success_rate.toFixed(1)}%</div>
              </div>
            </div>

            {/* Services */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">Services</h4>
              
              <div className="p-2 border rounded text-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">API Service</span>
                  <div className={`w-2 h-2 rounded-full ${healthStatus.services.api.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                </div>
                <div className="text-xs text-gray-600">
                  Requests: {healthStatus.services.api.total_requests}
                </div>
              </div>

              <div className="p-2 border rounded text-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">Chat Service</span>
                  <div className={`w-2 h-2 rounded-full ${healthStatus.services.chat.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                </div>
                <div className="text-xs text-gray-600">
                  Sessions: {healthStatus.services.chat.active_sessions}
                </div>
              </div>

              <div className="p-2 border rounded text-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium">Database</span>
                  <div className={`w-2 h-2 rounded-full ${healthStatus.services.database.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                </div>
                <div className="text-xs text-gray-600">
                  Type: {healthStatus.services.database.type}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProductionChatDashboard; 