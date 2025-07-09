/**
 * 🎯 SOPHIA AI - UNIFIED CHAT DASHBOARD
 * Executive-grade business intelligence interface for Pay Ready CEO
 * 
 * 🚨 FILE TYPE: PERMANENT
 * 🏗️ ARCHITECTURE: React + TypeScript + WebSocket integration
 * 🔐 API INTEGRATION: Unified Chat Backend (port 8001)
 * 
 * Business Context:
 * - Executive dashboard for Pay Ready CEO (80 employees, $50M revenue)
 * - Real-time chat interface with MCP server orchestration
 * - Comprehensive business intelligence across all systems
 * 
 * Features:
 * - Real-time chat with intelligent query routing
 * - MCP server status monitoring
 * - Executive KPI visualization
 * - Multi-source data integration
 */

import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Types for our data structures
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  sources?: string[];
  insights?: string[];
  recommendations?: string[];
  metadata?: {
    intent: string;
    urgency: string;
    response_time: number;
  };
}

interface MCPServer {
  name: string;
  description: string;
  url: string;
  healthy: boolean;
  response_time: number;
}

interface SystemStatus {
  timestamp: string;
  overall_status: 'healthy' | 'degraded' | 'critical';
  servers: Record<string, MCPServer>;
  metrics: {
    total_servers: number;
    healthy_servers: number;
    avg_response_time: number;
    active_connections: number;
  };
}

const CHAT_API_BASE = 'http://localhost:8001';

const UnifiedChatDashboard: React.FC = () => {
  // State management
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message and system status
  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          role: 'system',
          content: '🚀 Welcome to Sophia AI - Your Executive Intelligence Assistant. I can help you with project management, team insights, sales analysis, and data analytics across all your business systems.',
          timestamp: new Date().toISOString()
        };
        setMessages([welcomeMessage]);

        // Check system status
        await checkSystemStatus();
        setIsConnected(true);
      } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        const errorMessage: ChatMessage = {
          role: 'system',
          content: '❌ Failed to connect to Sophia AI backend. Please check system status.',
          timestamp: new Date().toISOString()
        };
        setMessages([errorMessage]);
      }
    };

    initializeDashboard();
  }, []);

  // Check system status
  const checkSystemStatus = async () => {
    try {
      const response = await axios.get(`${CHAT_API_BASE}/api/v3/system/status`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Failed to get system status:', error);
    }
  };

  // Send chat message
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
      const response = await axios.post(`${CHAT_API_BASE}/api/v3/chat`, {
        message: inputMessage
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        sources: response.data.data_sources,
        insights: response.data.insights,
        recommendations: response.data.recommendations,
        metadata: response.data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        role: 'system',
        content: '❌ Failed to process your request. Please try again.',
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

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white shadow-sm border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sophia AI</h1>
              <p className="text-sm text-gray-600">Executive Intelligence Assistant</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-green-600' : 'bg-red-600'}`}></div>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
              <button
                onClick={checkSystemStatus}
                className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                Refresh Status
              </button>
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
                className={`max-w-3xl p-4 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.role === 'system'
                    ? 'bg-gray-200 text-gray-800'
                    : 'bg-white border shadow-sm'
                }`}
              >
                <div className="mb-2">
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>

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

                {/* Sources and Metadata */}
                <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center space-x-4">
                    {message.sources && message.sources.length > 0 && (
                      <span>📊 Sources: {message.sources.join(', ')}</span>
                    )}
                    {message.metadata && (
                      <span>⚡ {message.metadata.response_time.toFixed(3)}s</span>
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
                  <span className="text-gray-600">Sophia is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t p-4">
          <div className="flex space-x-4">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your projects, tasks, team insights, sales data, or any business intelligence query..."
              className="flex-1 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            💡 Try: "What are my current tasks?" | "Show me project status" | "Team communication insights" | "Sales pipeline analysis"
          </div>
        </div>
      </div>

      {/* System Status Sidebar */}
      <div className="w-80 bg-white border-l p-4 overflow-y-auto">
        <h3 className="text-lg font-semibold mb-4">System Status</h3>

        {systemStatus && (
          <>
            {/* Overall Status */}
            <div className="mb-4 p-3 bg-gray-50 rounded">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">Overall Status</span>
                <span className={`font-bold ${getStatusColor(systemStatus.overall_status)}`}>
                  {systemStatus.overall_status.toUpperCase()}
                </span>
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Servers: {systemStatus.metrics.healthy_servers}/{systemStatus.metrics.total_servers}</div>
                <div>Avg Response: {systemStatus.metrics.avg_response_time.toFixed(3)}s</div>
                <div>Connections: {systemStatus.metrics.active_connections}</div>
              </div>
            </div>

            {/* MCP Servers */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700">MCP Servers</h4>
              {Object.entries(systemStatus.servers).map(([name, server]) => (
                <div key={name} className="p-2 border rounded text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium capitalize">{name}</span>
                    <div className={`w-2 h-2 rounded-full ${server.healthy ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  </div>
                  <div className="text-xs text-gray-600 mb-1">{server.description}</div>
                  {server.healthy && (
                    <div className="text-xs text-green-600">⚡ {server.response_time.toFixed(3)}s</div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        {/* Quick Actions */}
        <div className="mt-6">
          <h4 className="font-medium text-gray-700 mb-2">Quick Actions</h4>
          <div className="space-y-2 text-sm">
            <button
              onClick={() => setInputMessage("What are my current tasks and deadlines?")}
              className="w-full text-left p-2 bg-blue-50 hover:bg-blue-100 rounded"
            >
              📋 View Tasks & Deadlines
            </button>
            <button
              onClick={() => setInputMessage("Show me project health status")}
              className="w-full text-left p-2 bg-green-50 hover:bg-green-100 rounded"
            >
              📊 Project Health Status
            </button>
            <button
              onClick={() => setInputMessage("Team communication insights")}
              className="w-full text-left p-2 bg-purple-50 hover:bg-purple-100 rounded"
            >
              👥 Team Insights
            </button>
            <button
              onClick={() => setInputMessage("Sales pipeline analysis")}
              className="w-full text-left p-2 bg-orange-50 hover:bg-orange-100 rounded"
            >
              💰 Sales Pipeline
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedChatDashboard; 