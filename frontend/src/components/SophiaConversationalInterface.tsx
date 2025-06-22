import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  MessageCircle,
  Sparkles,
  Brain,
  Send,
  Download,
  FileText,
  BarChart3,
  Lightbulb,
  Heart
} from 'lucide-react';

// Enhanced message interface with Sophia personality
interface SophiaMessage {
  id: string;
  type: 'user' | 'sophia' | 'system';
  content: string;
  timestamp: number;
  confidence?: number;
  personality_markers?: {
    warmth: number;
    intelligence: number;
    helpfulness: number;
  };
  suggested_actions?: Array<{
    label: string;
    action: string;
    icon?: string;
  }>;
  export_options?: Array<{
    format: 'csv' | 'excel' | 'pdf' | 'txt';
    label: string;
  }>;
}

// Sophia personality configuration
const SOPHIA_PERSONALITY = {
  greeting_messages: [
    "Hi there! I'm Sophia, your AI business intelligence partner. How can I help you unlock insights today?",
    "Hello! Sophia here, ready to dive into your data and find the answers you need. What's on your mind?",
    "Welcome back! I'm excited to help you discover new insights. What would you like to explore together?"
  ],
  conversation_starters: [
    "📊 Show me our latest sales performance",
    "🎯 Analyze recent Gong call insights", 
    "📈 Generate a revenue report for this quarter",
    "🔍 Help me understand customer sentiment trends",
    "💡 What opportunities should we focus on?"
  ],
  response_patterns: {
    enthusiasm: ["That's a great question!", "I love diving into this data!", "Excellent insight!"],
    empathy: ["I understand that's important to you", "Let me help you with that", "I can see why you'd want to know that"],
    intelligence: ["Based on the data patterns I'm seeing", "The analytics suggest", "Here's what the numbers tell us"]
  }
};

const SophiaConversationalInterface: React.FC = () => {
  const [messages, setMessages] = useState<SophiaMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionMemory, setSessionMemory] = useState<Record<string, any>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize with Sophia's greeting
  useEffect(() => {
    const greetingIndex = Math.floor(Math.random() * SOPHIA_PERSONALITY.greeting_messages.length);
    const greeting: SophiaMessage = {
      id: 'sophia-greeting',
      type: 'sophia',
      content: SOPHIA_PERSONALITY.greeting_messages[greetingIndex],
      timestamp: Date.now(),
      personality_markers: {
        warmth: 0.9,
        intelligence: 0.8,
        helpfulness: 0.95
      },
      suggested_actions: SOPHIA_PERSONALITY.conversation_starters.map(starter => ({
        label: starter,
        action: 'suggest_query',
        icon: starter.charAt(0)
      }))
    };
    setMessages([greeting]);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    // Add user message
    const userMessage: SophiaMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Update session memory
    setSessionMemory(prev => ({
      ...prev,
      last_query: message,
      query_count: (prev.query_count || 0) + 1,
      conversation_context: [...(prev.conversation_context || []), message]
    }));

    try {
      // Call Sophia AI backend
      const response = await fetch('/api/v1/sophia/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_memory: sessionMemory,
          personality_config: SOPHIA_PERSONALITY
        })
      });

      const data = await response.json();

      // Add Sophia's response with personality
      const sophiaResponse: SophiaMessage = {
        id: `sophia-${Date.now()}`,
        type: 'sophia',
        content: data.response,
        timestamp: Date.now(),
        confidence: data.confidence,
        personality_markers: data.personality_markers,
        suggested_actions: data.suggested_actions,
        export_options: data.export_options
      };

      setMessages(prev => [...prev, sophiaResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Fallback response
      const errorResponse: SophiaMessage = {
        id: `sophia-error-${Date.now()}`,
        type: 'sophia',
        content: "I apologize, but I'm having trouble processing that right now. Could you try rephrasing your question?",
        timestamp: Date.now(),
        personality_markers: {
          warmth: 0.8,
          intelligence: 0.6,
          helpfulness: 0.9
        }
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestedAction = (action: string, label: string) => {
    if (action === 'suggest_query') {
      // Remove emoji and use the text as query
      const query = label.replace(/^[^\w\s]+\s*/, '');
      handleSendMessage(query);
    }
  };

  const handleExport = async (messageId: string, format: string) => {
    try {
      const response = await fetch(`/api/v1/sophia/export/${messageId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sophia-export-${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const SophiaMessageBubble: React.FC<{ message: SophiaMessage }> = ({ message }) => {
    const isUser = message.type === 'user';
    const isSophia = message.type === 'sophia';

    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
        <div className={`max-w-[80%] ${
          isUser 
            ? 'bg-blue-500 text-white rounded-lg p-4' 
            : isSophia
              ? 'bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4'
              : 'bg-gray-100 border rounded-lg p-4'
        }`}>
          {/* Sophia Avatar and Name */}
          {isSophia && (
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                <Sparkles className="w-3 h-3 text-white" />
              </div>
              <span className="text-sm font-medium text-purple-700">Sophia</span>
              {message.personality_markers && (
                <div className="flex gap-1 ml-auto">
                  <Heart className="w-3 h-3 text-pink-500" fill="currentColor" style={{ opacity: message.personality_markers.warmth }} />
                  <Brain className="w-3 h-3 text-blue-500" fill="currentColor" style={{ opacity: message.personality_markers.intelligence }} />
                  <Lightbulb className="w-3 h-3 text-yellow-500" fill="currentColor" style={{ opacity: message.personality_markers.helpfulness }} />
                </div>
              )}
            </div>
          )}

          {/* Message Content */}
          <div className={`text-sm ${isSophia ? 'text-gray-800' : isUser ? 'text-white' : 'text-gray-800'}`}>
            {message.content}
          </div>

          {/* Confidence Score */}
          {message.confidence && (
            <div className="text-xs mt-2 opacity-70">
              Confidence: {(message.confidence * 100).toFixed(1)}%
            </div>
          )}

          {/* Export Options */}
          {message.export_options && message.export_options.length > 0 && (
            <div className="mt-3 flex gap-2">
              <span className="text-xs text-gray-600">Export as:</span>
              {message.export_options.map((option) => (
                <Button
                  key={option.format}
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport(message.id, option.format)}
                  className="text-xs h-6"
                >
                  <Download className="w-3 h-3 mr-1" />
                  {option.label}
                </Button>
              ))}
            </div>
          )}

          {/* Suggested Actions */}
          {message.suggested_actions && message.suggested_actions.length > 0 && (
            <div className="mt-3 space-y-1">
              <div className="text-xs text-gray-600 mb-2">Try asking:</div>
              {message.suggested_actions.map((action, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  size="sm"
                  onClick={() => handleSuggestedAction(action.action, action.label)}
                  className="text-xs h-auto p-2 justify-start w-full text-left"
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}

          {/* Timestamp */}
          <div className="text-xs mt-2 opacity-50">
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">Sophia AI</h1>
              <p className="text-sm text-gray-600">Your intelligent business partner</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="flex items-center gap-1">
              <Brain className="w-3 h-3" />
              Business Intelligence
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <BarChart3 className="w-3 h-3" />
              Real-time Analytics
            </Badge>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-lg font-medium mb-2 text-gray-800">Welcome to Sophia AI</h3>
            <p className="text-gray-600">Your intelligent business intelligence partner is ready to help</p>
          </div>
        ) : (
          messages.map(message => (
            <SophiaMessageBubble key={message.id} message={message} />
          ))
        )}
        
        {isTyping && (
          <div className="flex justify-start mb-4">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-purple-700">Sophia</span>
                <div className="flex gap-1 ml-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t bg-white px-6 py-4">
        <div className="flex gap-3">
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask Sophia anything about your business..."
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
            className="flex-1"
          />
          <Button 
            onClick={() => handleSendMessage(inputValue)}
            disabled={!inputValue.trim() || isTyping}
            className="bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <div className="text-xs text-gray-500 mt-2 text-center">
          Sophia remembers our conversation context and can export data in multiple formats
        </div>
      </div>
    </div>
  );
};

export default SophiaConversationalInterface; 