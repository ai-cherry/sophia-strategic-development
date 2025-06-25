import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { 
  Loader2, 
  Send, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  Bot, 
  User, 
  Zap,
  MessageSquare,
  Settings,
  RefreshCw,
  Copy,
  ExternalLink
} from 'lucide-react';

// Dashboard context types
export type DashboardType = 'ceo' | 'knowledge' | 'project' | 'general';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  actionResult?: ActionResult;
  error?: string;
  metadata?: Record<string, any>;
  suggestedActions?: SuggestedAction[];
}

interface ActionResult {
  success: boolean;
  message: string;
  data?: any;
  executionTime?: number;
}

interface SuggestedAction {
  id: string;
  label: string;
  description?: string;
  action: string;
  parameters?: Record<string, any>;
  icon?: string;
  category: 'data' | 'analysis' | 'action' | 'navigation';
}

interface ChatContext {
  dashboardType: DashboardType;
  userId: string;
  tenantId?: string;
  activeFilters?: Record<string, any>;
  selectedEntities?: string[];
  currentPage?: string;
  sessionData?: Record<string, any>;
}

interface EnhancedUnifiedChatInterfaceProps {
  context: ChatContext;
  height?: string;
  title?: string;
  placeholder?: string;
  onActionExecuted?: (action: SuggestedAction, result: ActionResult) => void;
  onContextChange?: (newContext: Partial<ChatContext>) => void;
  enableVoice?: boolean;
  enableFileUpload?: boolean;
  maxMessages?: number;
}

// Dashboard-specific prompts and placeholders
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
  onContextChange,
  enableVoice = false,
  enableFileUpload = false,
  maxMessages = 100
}) => {
  // State management
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
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connecting');
  const [typingIndicator, setTypingIndicator] = useState(false);
  
  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/chat/ws`;
    
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setError(null);
        
        // Send initialization message with context
        ws.send(JSON.stringify({
          type: 'init',
          context: context,
          timestamp: new Date().toISOString()
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setConnectionStatus('disconnected');
        
        // Attempt to reconnect after delay (with exponential backoff)
        if (!event.wasClean) {
          const delay = Math.min(1000 * Math.pow(2, Math.random()), 30000);
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, delay);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
        setError('Connection error. Retrying...');
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setConnectionStatus('disconnected');
      setError('Failed to connect. Please check your connection.');
    }
  }, [context]);

  // Handle incoming WebSocket messages
  const handleWebSocketMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'message':
        setMessages(prev => [...prev, {
          id: data.id || Date.now().toString(),
          role: data.role || 'assistant',
          content: data.content,
          timestamp: data.timestamp || new Date().toISOString(),
          actionResult: data.actionResult,
          suggestedActions: data.suggestedActions
        }]);
        setTypingIndicator(false);
        break;
        
      case 'suggestion':
        setSuggestedActions(prev => [...prev, data.action]);
        break;
        
      case 'typing':
        setTypingIndicator(data.isTyping);
        break;
        
      case 'error':
        setError(data.message);
        setLoading(false);
        setTypingIndicator(false);
        break;
        
      case 'action_result':
        if (onActionExecuted) {
          onActionExecuted(data.action, data.result);
        }
        break;
        
      case 'context_update':
        if (onContextChange) {
          onContextChange(data.context);
        }
        break;
        
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }, [onActionExecuted, onContextChange]);

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [connectWebSocket]);

  // Detect task type based on message content and dashboard context
  const detectTaskType = useCallback((message: string): string => {
    const lowerMessage = message.toLowerCase();
    
    // Dashboard-specific task detection
    if (context.dashboardType === 'ceo') {
      if (lowerMessage.includes('revenue') || lowerMessage.includes('sales')) return 'financial_analysis';
      if (lowerMessage.includes('competitor') || lowerMessage.includes('market')) return 'competitive_intelligence';
      if (lowerMessage.includes('team') || lowerMessage.includes('staff')) return 'team_analytics';
      if (lowerMessage.includes('forecast') || lowerMessage.includes('predict')) return 'forecasting';
    } else if (context.dashboardType === 'knowledge') {
      if (lowerMessage.includes('search') || lowerMessage.includes('find')) return 'knowledge_search';
      if (lowerMessage.includes('summarize') || lowerMessage.includes('summary')) return 'summarization';
      if (lowerMessage.includes('upload') || lowerMessage.includes('ingest')) return 'knowledge_ingestion';
      if (lowerMessage.includes('analyze') || lowerMessage.includes('insights')) return 'content_analysis';
    } else if (context.dashboardType === 'project') {
      if (lowerMessage.includes('status') || lowerMessage.includes('progress')) return 'project_status';
      if (lowerMessage.includes('create') || lowerMessage.includes('new')) return 'task_creation';
      if (lowerMessage.includes('assign') || lowerMessage.includes('delegate')) return 'task_assignment';
      if (lowerMessage.includes('timeline') || lowerMessage.includes('schedule')) return 'project_planning';
    }
    
    // General task types
    if (lowerMessage.includes('code') || lowerMessage.includes('script')) return 'code_generation';
    if (lowerMessage.includes('analyze') || lowerMessage.includes('compare')) return 'complex_reasoning';
    if (lowerMessage.includes('report') || lowerMessage.includes('dashboard')) return 'reporting';
    
    return 'general';
  }, [context.dashboardType]);

  // Send message via WebSocket or HTTP fallback
  const sendMessage = useCallback(async (messageContent: string) => {
    if (!messageContent.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: messageContent.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);
    setTypingIndicator(true);

    const taskType = detectTaskType(messageContent);

    try {
      // Try WebSocket first
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'chat_message',
          message: messageContent,
          context: context,
          taskType: taskType,
          timestamp: new Date().toISOString()
        }));
      } else {
        // Fallback to HTTP API
        const response = await fetch('/api/v1/chat/message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: messageContent,
            context: context,
            taskType: taskType,
            history: messages.slice(-10) // Send last 10 messages for context
          }),
          signal: abortControllerRef.current?.signal
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: data.id || (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.content,
          timestamp: data.timestamp || new Date().toISOString(),
          actionResult: data.actionResult,
          suggestedActions: data.suggestedActions
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        if (data.suggestedActions) {
          setSuggestedActions(prev => [...prev, ...data.suggestedActions]);
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Failed to send message:', err);
        setError('Failed to send message. Please try again.');
        
        // Add error message to chat
        const errorMessage: ChatMessage = {
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: 'I apologize, but I encountered an error processing your request. Please try again.',
          timestamp: new Date().toISOString(),
          error: err.message
        };
        
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setLoading(false);
      setTypingIndicator(false);
    }
  }, [messages, context, detectTaskType]);

  // Execute suggested action
  const executeSuggestedAction = useCallback(async (action: SuggestedAction) => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/v1/chat/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: action,
          context: context
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (onActionExecuted) {
        onActionExecuted(action, result);
      }

      // Add action result to chat
      const resultMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Action "${action.label}" completed successfully.`,
        timestamp: new Date().toISOString(),
        actionResult: result
      };

      setMessages(prev => [...prev, resultMessage]);
      
      // Remove executed action from suggestions
      setSuggestedActions(prev => prev.filter(a => a.id !== action.id));
      
    } catch (err: any) {
      console.error('Failed to execute action:', err);
      setError(`Failed to execute action: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, [context, onActionExecuted]);

  // Handle input submission
  const handleSubmit = useCallback((e?: React.FormEvent) => {
    e?.preventDefault();
    
    if (loading || !input.trim()) return;
    
    // Cancel any pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    sendMessage(input);
  }, [input, loading, sendMessage]);

  // Handle keyboard shortcuts
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  // Copy message to clipboard
  const copyMessage = useCallback(async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      // Could add a toast notification here
    } catch (err) {
      console.error('Failed to copy message:', err);
    }
  }, []);

  // Clear chat history
  const clearChat = useCallback(() => {
    setMessages([{
      id: '1',
      role: 'assistant',
      content: DASHBOARD_PROMPTS[context.dashboardType],
      timestamp: new Date().toISOString()
    }]);
    setSuggestedActions([]);
    setError(null);
  }, [context.dashboardType]);

  // Get message styling based on type
  const getMessageClassName = useCallback((message: ChatMessage) => {
    const baseClasses = "flex gap-3 p-4 rounded-lg transition-all duration-200";
    
    if (message.role === 'user') {
      return `${baseClasses} bg-blue-50 dark:bg-blue-900/20 ml-8 border-l-4 border-blue-500`;
    }
    
    if (message.error) {
      return `${baseClasses} bg-red-50 dark:bg-red-900/20 mr-8 border-l-4 border-red-500`;
    }
    
    if (message.actionResult) {
      return `${baseClasses} bg-green-50 dark:bg-green-900/20 mr-8 border-l-4 border-green-500`;
    }
    
    return `${baseClasses} bg-gray-50 dark:bg-slate-800/50 mr-8 border-l-4 border-purple-500`;
  }, []);

  // Connection status indicator
  const getConnectionStatusDisplay = () => {
    const statusConfig = {
      connected: { color: 'text-green-600', bg: 'bg-green-600', label: 'Connected' },
      connecting: { color: 'text-yellow-600', bg: 'bg-yellow-600', label: 'Connecting' },
      disconnected: { color: 'text-red-600', bg: 'bg-red-600', label: 'Disconnected' }
    };
    
    const config = statusConfig[connectionStatus];
    
    return (
      <div className={`flex items-center gap-1 ${config.color}`}>
        <div className={`h-2 w-2 rounded-full ${config.bg} ${connectionStatus === 'connecting' ? 'animate-pulse' : ''}`} />
        <span className="text-xs">{config.label}</span>
      </div>
    );
  };

  return (
    <Card className="flex flex-col shadow-lg border-slate-700/50" style={{ height }}>
      <CardHeader className="pb-3 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Bot className="h-5 w-5 text-purple-400" />
            {title}
          </CardTitle>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {getConnectionStatusDisplay()}
            <span>•</span>
            <Badge variant="outline" className="text-xs">
              {context.dashboardType}
            </Badge>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearChat}
              className="h-6 w-6 p-0"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="m-4 mb-0">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Messages Container */}
        <div className="h-full overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={getMessageClassName(message)}>
              <div className="flex-shrink-0">
                {message.role === 'user' ? (
                  <User className="h-6 w-6 text-blue-500" />
                ) : (
                  <Bot className="h-6 w-6 text-purple-400" />
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium">
                    {message.role === 'user' ? 'You' : 'Sophia'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  {message.content}
                </div>

                {/* Action Result Display */}
                {message.actionResult && (
                  <div className="mt-2 p-3 bg-green-100 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">Action Completed</span>
                      {message.actionResult.executionTime && (
                        <span className="text-xs text-gray-500">
                          ({message.actionResult.executionTime}ms)
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                      {message.actionResult.message}
                    </p>
                  </div>
                )}

                {/* Suggested Actions */}
                {message.suggestedActions && message.suggestedActions.length > 0 && (
                  <div className="mt-3 space-y-2">
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      Suggested Actions:
                    </span>
                    <div className="flex flex-wrap gap-2">
                      {message.suggestedActions.map((action) => (
                        <Button
                          key={action.id}
                          variant="outline"
                          size="sm"
                          onClick={() => executeSuggestedAction(action)}
                          className="text-xs"
                        >
                          <Zap className="h-3 w-3 mr-1" />
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Message Actions */}
                <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyMessage(message.content)}
                    className="h-6 w-6 p-0"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {typingIndicator && (
            <div className="flex gap-3 p-4 rounded-lg bg-gray-50 dark:bg-slate-800/50 mr-8">
              <Bot className="h-6 w-6 text-purple-400" />
              <div className="flex items-center gap-1">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
                <span className="text-sm text-gray-500 ml-2">Sophia is thinking...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Global Suggested Actions */}
        {suggestedActions.length > 0 && (
          <div className="border-t border-slate-700/50 p-4 bg-slate-900/50">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-purple-400" />
              <span className="text-sm font-medium">Quick Actions</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestedActions.slice(0, 6).map((action) => (
                <Button
                  key={action.id}
                  variant="outline"
                  size="sm"
                  onClick={() => executeSuggestedAction(action)}
                  className="text-xs"
                >
                  {action.label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-slate-700/50 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={placeholder || DASHBOARD_PLACEHOLDERS[context.dashboardType]}
              disabled={loading || connectionStatus === 'disconnected'}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={loading || !input.trim() || connectionStatus === 'disconnected'}
              size="sm"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  );
};

export default EnhancedUnifiedChatInterface;
