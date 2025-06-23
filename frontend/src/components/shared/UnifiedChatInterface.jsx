import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

const UnifiedChatInterface = ({ 
  context = {}, 
  dashboardType = 'general', 
  userId = 'anonymous',
  height = '400px',
  title = 'Chat with Sophia AI' 
}) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I'm Sophia, your AI assistant. I have access to all your business data and can help with analysis, insights, and actions across ${dashboardType === 'ceo' ? 'executive metrics' : dashboardType === 'knowledge' ? 'knowledge management' : dashboardType === 'project' ? 'project management' : 'your business operations'}. What would you like to know?`,
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    setLoading(true);
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch('/api/v1/chat/unified', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          context: {
            ...context,
            dashboardType,
            userId,
            conversationHistory: messages.slice(-10) // Last 10 messages for context
          },
          routing: {
            preferredProvider: 'openrouter',
            taskType: detectTaskType(input),
            urgency: 'normal'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        metadata: {
          model: data.model_used,
          latency: data.latency_ms,
          cost: data.cost_usd,
          sources: data.sources || []
        }
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Trigger any suggested actions
      if (data.suggested_actions && data.suggested_actions.length > 0) {
        setSuggestedActions(data.suggested_actions);
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        role: 'assistant', 
        content: `I apologize, but I encountered an error: ${error.message}. Please try again or contact support if the issue persists.`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const detectTaskType = (message) => {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('code') || lowerMessage.includes('script') || lowerMessage.includes('function')) return 'code_generation';
    if (lowerMessage.includes('analyze') || lowerMessage.includes('compare') || lowerMessage.includes('reason')) return 'complex_reasoning';
    if (lowerMessage.includes('summarize') || lowerMessage.includes('summary')) return 'summarization';
    return 'general';
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const [suggestedActions, setSuggestedActions] = useState([]);

  const executeSuggestedAction = async (action) => {
    try {
      const response = await fetch('/api/v1/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action.id,
          parameters: action.parameters,
          context: { dashboardType, userId }
        })
      });
      
      const result = await response.json();
      
      const actionMessage = {
        role: 'assistant',
        content: `✅ ${action.description}: ${result.message}`,
        timestamp: new Date().toISOString(),
        isAction: true
      };
      
      setMessages(prev => [...prev, actionMessage]);
      setSuggestedActions(prev => prev.filter(a => a.id !== action.id));
      
    } catch (error) {
      console.error('Failed to execute action:', error);
    }
  };

  return (
    <Card className="flex flex-col" style={{ height }}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">{title}</CardTitle>
        <p className="text-xs text-muted-foreground">
          Powered by OpenRouter • Context: {dashboardType}
        </p>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : message.isError 
                    ? 'bg-red-50 text-red-800 border border-red-200'
                    : message.isAction
                      ? 'bg-green-50 text-green-800 border border-green-200'
                      : 'bg-gray-50 text-gray-800'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.metadata && (
                  <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                    Model: {message.metadata.model} • {message.metadata.latency}ms • ${message.metadata.cost?.toFixed(4)}
                    {message.metadata.sources && message.metadata.sources.length > 0 && (
                      <div className="mt-1">
                        Sources: {message.metadata.sources.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Actions */}
        {suggestedActions.length > 0 && (
          <div className="mb-4 space-y-2">
            <p className="text-sm font-medium text-gray-600">Suggested Actions:</p>
            {suggestedActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                size="sm"
                onClick={() => executeSuggestedAction(action)}
                className="mr-2 mb-2"
              >
                {action.description}
              </Button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask Sophia about ${dashboardType} data...`}
            disabled={loading}
            className="flex-1"
          />
          <Button onClick={sendMessage} disabled={loading || !input.trim()}>
            {loading ? '⏳' : '📤'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default UnifiedChatInterface; 