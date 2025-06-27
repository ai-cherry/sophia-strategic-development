/**
 * Universal Chat Interface for Sophia AI
 * 
 * Primary interface for conversational business intelligence with:
 * - Real-time OKR tracking header
 * - Glassmorphism design with premium UI
 * - Voice input support and conversation memory
 * - Role-based data access and premium model routing
 * - Proactive insights sidebar with live business intelligence
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  MessageCircle, 
  Mic, 
  MicOff, 
  Send, 
  TrendingUp, 
  Target, 
  DollarSign,
  Brain,
  Users,
  Building,
  AlertCircle,
  CheckCircle,
  Clock,
  Zap,
  BarChart3,
  Settings
} from 'lucide-react';

// Types
interface OKRMetric {
  name: string;
  current_value: number;
  target_value: number;
  unit: string;
  trend_7d: number;
  trend_30d: number;
  status: 'on_track' | 'at_risk' | 'behind' | 'exceeded';
  confidence: number;
}

interface OKRData {
  overall_score: {
    score: number;
    grade: string;
    trend: string;
  };
  okrs: {
    ai_first_company: OKRMetric;
    revenue_per_employee: OKRMetric;
    revenue_per_unit: OKRMetric;
  };
  critical_actions: Array<{
    okr: string;
    action: string;
    urgency: string;
    impact: number;
  }>;
}

interface ChatMessage {
  message: string;
  context?: Record<string, any>;
  user_role?: string;
  conversation_id?: string;
}

interface ChatResponse {
  response: string;
  confidence: number;
  sources: string[];
  insights: Array<{
    type: string;
    data: any;
  }>;
  recommended_actions: string[];
  conversation_id: string;
  timestamp: string;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  confidence?: number;
  sources?: string[];
  insights?: any[];
  actions?: string[];
}

const UniversalChatInterface: React.FC = () => {
  // State management
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [okrData, setOkrData] = useState<OKRData | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string>('employee');
  const [showInsights, setShowInsights] = useState(true);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
      };

      recognitionRef.current.onerror = () => {
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Fetch OKR data
  const fetchOKRData = useCallback(async () => {
    try {
      const response = await fetch('/api/chat/okrs');
      if (response.ok) {
        const data = await response.json();
        setOkrData(data);
      }
    } catch (error) {
      console.error('Error fetching OKR data:', error);
    }
  }, []);

  // Load OKR data on mount and set up refresh interval
  useEffect(() => {
    fetchOKRData();
    const interval = setInterval(fetchOKRData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [fetchOKRData]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle voice input
  const handleVoiceInput = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      recognitionRef.current.start();
    } else if (isListening) {
      setIsListening(false);
      recognitionRef.current?.stop();
    }
  };

  // Send message
  const sendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const chatMessage: ChatMessage = {
        message: inputText,
        context: {},
        user_role: userRole,
        conversation_id: conversationId || undefined
      };

      const response = await fetch('/api/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatMessage)
      });

      if (response.ok) {
        const chatResponse: ChatResponse = await response.json();
        
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: chatResponse.response,
          isUser: false,
          timestamp: new Date(),
          confidence: chatResponse.confidence,
          sources: chatResponse.sources,
          insights: chatResponse.insights,
          actions: chatResponse.recommended_actions
        };

        setMessages(prev => [...prev, aiMessage]);
        setConversationId(chatResponse.conversation_id);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm experiencing technical difficulties. Please try again.",
        isUser: false,
        timestamp: new Date(),
        confidence: 0.1
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

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'exceeded': return 'text-green-400';
      case 'on_track': return 'text-blue-400';
      case 'at_risk': return 'text-yellow-400';
      case 'behind': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  // Get status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'exceeded': return <CheckCircle className="w-4 h-4" />;
      case 'on_track': return <TrendingUp className="w-4 h-4" />;
      case 'at_risk': return <Clock className="w-4 h-4" />;
      case 'behind': return <AlertCircle className="w-4 h-4" />;
      default: return <BarChart3 className="w-4 h-4" />;
    }
  };

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  // Quick actions
  const quickActions = [
    "What's our OKR progress this month?",
    "Show me top customer expansion opportunities",
    "Analyze churn risk across accounts",
    "Generate revenue forecast",
    "Review AI automation status",
    "What are the critical actions this week?"
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* OKR Header */}
        {okrData && (
          <div className="bg-black/20 backdrop-blur-xl border-b border-white/10 p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-purple-400" />
                  <span className="text-white font-semibold">Sophia AI</span>
                  <div className={`text-sm ${okrData.overall_score.grade === 'A+' ? 'text-green-400' : 
                    okrData.overall_score.grade.startsWith('A') ? 'text-blue-400' : 
                    okrData.overall_score.grade.startsWith('B') ? 'text-yellow-400' : 'text-red-400'}`}>
                    {okrData.overall_score.score.toFixed(1)}% ({okrData.overall_score.grade})
                  </div>
                </div>
                
                {/* OKR Metrics */}
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <Target className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-gray-300">AI-First:</span>
                    <span className={`text-sm font-medium ${getStatusColor(okrData.okrs.ai_first_company.status)}`}>
                      {(okrData.okrs.ai_first_company.current_value * 100).toFixed(1)}%
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-gray-300">Rev/Employee:</span>
                    <span className={`text-sm font-medium ${getStatusColor(okrData.okrs.revenue_per_employee.status)}`}>
                      {formatCurrency(okrData.okrs.revenue_per_employee.current_value)}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Building className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-gray-300">Rev/Unit:</span>
                    <span className={`text-sm font-medium ${getStatusColor(okrData.okrs.revenue_per_unit.status)}`}>
                      {formatCurrency(okrData.okrs.revenue_per_unit.current_value)}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowInsights(!showInsights)}
                  className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                >
                  <BarChart3 className="w-4 h-4 text-white" />
                </button>
                <button className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors">
                  <Settings className="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-8 border border-white/10 max-w-2xl mx-auto">
                <Brain className="w-12 h-12 text-purple-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-white mb-2">Welcome to Sophia AI</h2>
                <p className="text-gray-300 mb-6">
                  Your conversational business intelligence assistant. Ask me about OKRs, customers, revenue, or any business insights.
                </p>
                
                {/* Quick Actions */}
                <div className="grid grid-cols-2 gap-3">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => setInputText(action)}
                      className="p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 
                               text-sm text-white transition-colors text-left"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl p-4 rounded-2xl ${
                  message.isUser
                    ? 'bg-purple-600 text-white'
                    : 'bg-white/10 backdrop-blur-xl border border-white/10 text-white'
                }`}
              >
                <div className="mb-2">{message.text}</div>
                
                {!message.isUser && (
                  <div className="text-xs text-gray-300 space-y-2">
                    {message.confidence && (
                      <div className="flex items-center space-x-2">
                        <span>Confidence:</span>
                        <div className="flex-1 bg-white/10 rounded-full h-1">
                          <div
                            className="bg-gradient-to-r from-purple-400 to-blue-400 h-1 rounded-full"
                            style={{ width: `${message.confidence * 100}%` }}
                          />
                        </div>
                        <span>{(message.confidence * 100).toFixed(0)}%</span>
                      </div>
                    )}
                    
                    {message.sources && message.sources.length > 0 && (
                      <div>
                        <span className="font-medium">Sources:</span> {message.sources.join(', ')}
                      </div>
                    )}
                    
                    {message.actions && message.actions.length > 0 && (
                      <div className="mt-2">
                        <div className="text-xs font-medium mb-1">Recommended Actions:</div>
                        <div className="space-y-1">
                          {message.actions.map((action, index) => (
                            <div key={index} className="flex items-start space-x-2">
                              <Zap className="w-3 h-3 text-yellow-400 mt-0.5 flex-shrink-0" />
                              <span className="text-xs">{action}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                <div className="text-xs text-gray-400 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-400"></div>
                  <span className="text-white text-sm">Sophia is thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-black/20 backdrop-blur-xl border-t border-white/10">
          <div className="flex items-center space-x-3">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask Sophia about your business..."
                className="w-full p-4 bg-white/10 backdrop-blur-xl border border-white/10 rounded-2xl 
                         text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 
                         focus:border-transparent pr-12"
                disabled={isLoading}
              />
              <button
                onClick={handleVoiceInput}
                className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-1.5 rounded-lg 
                          transition-colors ${
                  isListening 
                    ? 'bg-red-500 text-white' 
                    : 'bg-white/10 hover:bg-white/20 text-gray-400'
                }`}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>
            </div>
            
            <button
              onClick={sendMessage}
              disabled={!inputText.trim() || isLoading}
              className="p-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 
                       hover:to-blue-700 text-white rounded-2xl transition-colors disabled:opacity-50 
                       disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Insights Sidebar */}
      {showInsights && (
        <div className="w-80 bg-black/20 backdrop-blur-xl border-l border-white/10 p-4 overflow-y-auto">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            <span>Live Insights</span>
          </h3>
          
          {okrData && (
            <div className="space-y-4">
              {/* Critical Actions */}
              {okrData.critical_actions.length > 0 && (
                <div className="bg-white/5 backdrop-blur-xl rounded-lg p-4 border border-white/10">
                  <h4 className="font-semibold text-white mb-3 flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <span>Critical Actions</span>
                  </h4>
                  <div className="space-y-2">
                    {okrData.critical_actions.map((action, index) => (
                      <div key={index} className="text-sm">
                        <div className="text-white font-medium">{action.okr}</div>
                        <div className="text-gray-300">{action.action}</div>
                        <div className={`text-xs ${
                          action.urgency === 'critical' ? 'text-red-400' :
                          action.urgency === 'high' ? 'text-yellow-400' : 'text-green-400'
                        }`}>
                          {action.urgency.toUpperCase()} • Impact: {(action.impact * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* OKR Details */}
              <div className="bg-white/5 backdrop-blur-xl rounded-lg p-4 border border-white/10">
                <h4 className="font-semibold text-white mb-3">OKR Details</h4>
                <div className="space-y-3">
                  {Object.entries(okrData.okrs).map(([key, okr]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(okr.status)}
                        <span className="text-sm text-gray-300">{okr.name.split(' ')[0]}</span>
                      </div>
                      <div className={`text-sm font-medium ${getStatusColor(okr.status)}`}>
                        {okr.unit.includes('usd') 
                          ? formatCurrency(okr.current_value)
                          : `${(okr.current_value * 100).toFixed(1)}%`
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="bg-white/5 backdrop-blur-xl rounded-lg p-4 border border-white/10">
                <h4 className="font-semibold text-white mb-3">Quick Actions</h4>
                <div className="space-y-2">
                  <button
                    onClick={() => setInputText("Show detailed OKR analysis")}
                    className="w-full text-left p-2 bg-white/5 hover:bg-white/10 rounded-lg 
                             text-sm text-white transition-colors"
                  >
                    📊 Detailed OKR Analysis
                  </button>
                  <button
                    onClick={() => setInputText("What customers need attention?")}
                    className="w-full text-left p-2 bg-white/5 hover:bg-white/10 rounded-lg 
                             text-sm text-white transition-colors"
                  >
                    👥 Customer Health Check
                  </button>
                  <button
                    onClick={() => setInputText("Generate weekly executive summary")}
                    className="w-full text-left p-2 bg-white/5 hover:bg-white/10 rounded-lg 
                             text-sm text-white transition-colors"
                  >
                    📈 Executive Summary
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UniversalChatInterface; 