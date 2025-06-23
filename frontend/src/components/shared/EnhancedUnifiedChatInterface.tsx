import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2, Send, AlertCircle, CheckCircle, Info, Bot, User } from 'lucide-react';

// Dashboard context types
export type DashboardType = 'ceo' | 'knowledge' | 'project' | 'general';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    latency?: number;
    cost?: number;
    sources?: string[];
    actions?: SuggestedAction[];
  };
  error?: boolean;
  actionResult?: boolean;
}

interface SuggestedAction {
  id: string;
  type: string;
  description: string;
  parameters: Record<string, any>;
  requiresConfirmation?: boolean;
}

interface ChatContext {
  dashboardType: DashboardType;
  userId: string;
  tenantId?: string;
  activeFilters?: Record<string, any>;
  selectedEntities?: string[];
}

interface EnhancedUnifiedChatInterfaceProps {
  context: ChatContext;
  height?: string;
  title?: string;
  placeholder?: string;
  onActionExecuted?: (action: SuggestedAction, result: any) => void;
  onContextChange?: (newContext: Partial<ChatContext>) => void;
}

const DASHBOARD_PROMPTS: Record<DashboardType, string> = {
  ceo: "I'm here to help with executive insights, strategic analysis, and business metrics. What would you like to know?",
  knowledge: "I can help you search, analyze, and manage your knowledge base. What information are you looking for?",
  project: "I'm ready to assist with project management, task tracking, and team coordination. How can I help?",
  general: "I'm Sophia, your AI assistant. I have access to all your business data and can help with various tasks. What would you like to do?"
};

const DASHBOARD_PLACEHOLDERS: Record<DashboardType, string> = {
  ceo: "Ask about revenue, competitors, or strategic initiatives...",
  knowledge: "Search documents, request summaries, or manage knowledge...",
  project: "Check project status, create tasks, or view team metrics...",
  general: "Ask me anything about your business..."
};

export const EnhancedUnifiedChatInterface: React.FC<EnhancedUnifiedChatInterfaceProps> = ({
  context,
  height = '500px',
  title = 'Chat with Sophia AI',
  placeholder,
  onActionExecuted,
  onContextChange
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: DASHBOARD_PROMPTS[context.dashboardType],
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedActions, setSuggestedActions] = useState<SuggestedAction[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/chat/ws`);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        ws.send(JSON.stringify({ type: 'init', context }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'suggestion') {
          setSuggestedActions(prev => [...prev, data.action]);
        }
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      return ws;
    };

    const ws = connectWebSocket();
    return () => ws.close();
  }, [context]);

  const detectTaskType = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    // Dashboard-specific task detection
    if (context.dashboardType === 'ceo') {
      if (lowerMessage.includes('revenue') || lowerMessage.includes('sales')) return 'financial_analysis';
      if (lowerMessage.includes('competitor') || lowerMessage.includes('market')) return 'competitive_intelligence';
      if (lowerMessage.includes('team') || lowerMessage.includes('staff')) return 'team_analytics';
    } else if (context.dashboardType === 'knowledge') {
      if (lowerMessage.includes('search') || lowerMessage.includes('find')) return 'knowledge_search';
      if (lowerMessage.includes('summarize') || lowerMessage.includes('summary')) return 'summarization';
      if (lowerMessage.includes('upload') || lowerMessage.includes('ingest')) return 'knowledge_ingestion';
    } else if (context.dashboardType === 'project') {
      if (lowerMessage.includes('status') || lowerMessage.includes('progress')) return 'project_status';
      if (lowerMessage.includes('create') || lowerMessage.includes('new')) return 'task_creation';
      if (lowerMessage.includes('assign') || lowerMessage.includes('delegate')) return 'task_assignment';
    }
    
    // General task types
    if (lowerMessage.includes('code') || lowerMessage.includes('script')) return 'code_generation';
    if (lowerMessage.includes('analyze') || lowerMessage.includes('compare')) return 'complex_reasoning';
    
    return 'general';
  };

  const sendMessage = useCallback(async () => {
    if (!input.trim() || loading) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    
    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/v1/chat/unified', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          message: input,
          context: {
            ...context,
            conversationHistory: messages.slice(-10).map((m: any) => ({
              role: m.role,
              content: m.content
            }))
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
      
      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        metadata: {
          model: data.model_used,
          latency: data.latency_ms,
          cost: data.cost_usd,
          sources: data.sources || [],
          actions: data.suggested_actions || []
        }
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Handle suggested actions
      if (data.suggested_actions && data.suggested_actions.length > 0) {
        setSuggestedActions(data.suggested_actions);
      }

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Request was cancelled');
      } else {
        console.error('Failed to send message:', error);
        const errorMessage: ChatMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `I apologize, but I encountered an error: ${error.message}. Please try again or contact support if the issue persists.`,
          timestamp: new Date().toISOString(),
          error: true
        };
        setMessages(prev => [...prev, errorMessage]);
        setError(error.message);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, [input, loading, messages, context]);

  const cancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setLoading(false);
    }
  };

  const executeSuggestedAction = async (action: SuggestedAction) => {
    if (action.requiresConfirmation) {
      const confirmed = window.confirm(`Are you sure you want to: ${action.description}?`);
      if (!confirmed) return;
    }

    try {
      const response = await fetch('/api/v1/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: action.id,
          type: action.type,
          parameters: action.parameters,
          context
        })
      });
      
      const result = await response.json();
      
      const actionMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `✅ ${action.description}: ${result.message}`,
        timestamp: new Date().toISOString(),
        actionResult: true
      };
      
      setMessages(prev => [...prev, actionMessage]);
      setSuggestedActions(prev => prev.filter((a: any) => a.id !== action.id));
      
      // Notify parent component
      if (onActionExecuted) {
        onActionExecuted(action, result);
      }
      
    } catch (error: any) {
      console.error('Failed to execute action:', error);
      setError(`Failed to execute action: ${error.message}`);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getMessageIcon = (message: ChatMessage) => {
    if (message.role === 'user') return <User className="h-4 w-4" />;
    if (message.error) return <AlertCircle className="h-4 w-4" />;
    if (message.actionResult) return <CheckCircle className="h-4 w-4" />;
    return <Bot className="h-4 w-4" />;
  };

  const getMessageClassName = (message: ChatMessage) => {
    const baseClasses = "flex gap-3 p-4 rounded-lg";
    if (message.role === 'user') return `${baseClasses} bg-blue-50 ml-8`;
    if (message.error) return `${baseClasses} bg-red-50 mr-8`;
    if (message.actionResult) return `${baseClasses} bg-green-50 mr-8`;
    return `${baseClasses} bg-gray-50 mr-8`;
  };

  return (
    <Card className="flex flex-col shadow-lg" style={{ height }}>
      <CardHeader className="pb-3 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Bot className="h-5 w-5" />
            {title}
          </CardTitle>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className={`flex items-center gap-1 ${
              connectionStatus === 'connected' ? 'text-green-600' : 
              connectionStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'
            }`}>
              <div className={`h-2 w-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-600' : 
                connectionStatus === 'connecting' ? 'bg-yellow-600 animate-pulse' : 'bg-red-600'
              }`} />
              {connectionStatus}
            </div>
            <span>•</span>
            <span>Context: {context.dashboardType}</span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="m-4 mb-0">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((message) => (
            <div key={message.id} className={getMessageClassName(message)}>
              <div className="flex-shrink-0 mt-1">
                {getMessageIcon(message)}
              </div>
              <div className="flex-1">
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.metadata && (
                  <div className="mt-2 text-xs text-gray-500 space-y-1">
                    {message.metadata.model && (
                      <div>Model: {message.metadata.model} • {message.metadata.latency}ms • ${message.metadata.cost?.toFixed(4)}</div>
                    )}
                    {message.metadata.sources && message.metadata.sources.length > 0 && (
                      <div>Sources: {message.metadata.sources.join(', ')}</div>
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
          <div className="p-4 pt-0 space-y-2">
            <p className="text-sm font-medium text-gray-600 flex items-center gap-1">
              <Info className="h-4 w-4" />
              Suggested Actions:
            </p>
            <div className="flex flex-wrap gap-2">
              {suggestedActions.map((action) => (
                <Button
                  key={action.id}
                  variant="outline"
                  size="sm"
                  onClick={() => executeSuggestedAction(action)}
                  className="text-xs"
                >
                  {action.description}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder || DASHBOARD_PLACEHOLDERS[context.dashboardType]}
              disabled={loading}
              className="flex-1"
            />
            {loading ? (
              <Button className="" variant="default" size="default" onClick={cancelRequest} variant="outline" size="icon">
                <Loader2 className="h-4 w-4 animate-spin" />
              </Button>
            ) : (
              <Button className="" variant="default" size="default" onClick={sendMessage} disabled={!input.trim()} size="icon">
                <Send className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedUnifiedChatInterface;
