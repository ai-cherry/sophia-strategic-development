import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { FileUpload, MessageSquare, Search, Database, Settings } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    latency?: number;
    cost?: number;
    sources?: Array<{title: string; category: string; relevance: number}>;
    contextUsed?: number;
    contextTokens?: number;
    searchResults?: number;
  };
  isError?: boolean;
  isAction?: boolean;
}

interface IngestionJob {
  jobId: string;
  filename: string;
  status: 'pending' | 'processing' | 'chunking' | 'storing' | 'completed' | 'failed';
  progress: number;
  chunksProcessed: number;
  totalChunks: number;
  entriesCreated: number;
  errorMessage?: string;
}

interface EnhancedChatProps {
  context?: Record<string, any>;
  dashboardType?: string;
  userId?: string;
  height?: string;
  title?: string;
  enableFileUpload?: boolean;
  enableAdvancedSearch?: boolean;
  maxContextTokens?: number;
}

const EnhancedUniversalChatInterface: React.FC<EnhancedChatProps> = ({
  context = {},
  dashboardType = 'general',
  userId = 'ceo_user',
  height = '600px',
  title = 'Sophia AI - Enhanced Intelligence Platform',
  enableFileUpload = true,
  enableAdvancedSearch = true,
  maxContextTokens = 32000
}) => {
  // State management
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Hello! I'm Sophia, your enhanced AI assistant with enterprise-grade capabilities.

🧠 **Enhanced Features Available:**
• **Large Context Windows**: Up to ${maxContextTokens.toLocaleString()} tokens for comprehensive analysis
• **Multi-Format File Processing**: Upload PDFs, Word docs, Excel files, PowerPoint, and more
• **Intelligent Search**: Semantic, keyword, and cross-document search capabilities
• **Real-time Analytics**: Performance monitoring and usage insights

I have access to all your business data and can provide detailed analysis across ${dashboardType === 'ceo' ? 'executive metrics and strategic insights' : dashboardType === 'knowledge' ? 'your complete knowledge base' : dashboardType === 'project' ? 'project management and team analytics' : 'all business operations'}.

**What would you like to explore today?**`,
      timestamp: new Date().toISOString(),
      metadata: {
        contextTokens: 0,
        contextUsed: 0
      }
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [ingestionJobs, setIngestionJobs] = useState<IngestionJob[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [contextStats, setContextStats] = useState<any>({});

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Utility functions
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const estimateTokens = (text: string): number => {
    return Math.ceil(text.length / 4); // Rough estimation
  };

  // Enhanced message sending with context management
  const sendMessage = async () => {
    if (!input.trim()) return;

    setLoading(true);
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      // Get enhanced context before sending
      const contextResponse = await fetch('/api/v1/chat/enhanced-context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input,
          userId,
          maxContextTokens,
          sessionId: generateSessionId(),
          includeConversationHistory: true,
          includeCrossDocumentContext: true
        })
      });

      const enhancedContext = await contextResponse.json();
      setContextStats(enhancedContext.stats || {});

      // Send message with enhanced context
      const response = await fetch('/api/v1/chat/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          context: {
            ...context,
            dashboardType,
            userId,
            enhancedContext,
            conversationHistory: messages.slice(-20) // More history for context
          },
          routing: {
            preferredProvider: 'openrouter',
            taskType: detectTaskType(input),
            urgency: 'normal',
            useEnhancedContext: true
          },
          searchOptions: {
            searchType: 'hybrid', // semantic + keyword + cross-document
            limit: 10,
            includeMetadata: true
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        metadata: {
          model: data.model_used,
          latency: data.latency_ms,
          cost: data.cost_usd,
          sources: data.sources || [],
          contextUsed: enhancedContext.context_items?.length || 0,
          contextTokens: enhancedContext.total_tokens || 0,
          searchResults: data.search_results_count || 0
        }
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
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

  // Enhanced file upload with job tracking
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    for (const file of Array.from(files)) {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('metadata', JSON.stringify({
        uploadedBy: userId,
        dashboardType,
        timestamp: new Date().toISOString()
      }));

      try {
        const response = await fetch('/api/v1/knowledge/upload-enhanced', {
          method: 'POST',
          body: formData
        });

        const result = await response.json();

        if (response.ok) {
          const newJob: IngestionJob = {
            jobId: result.job_id,
            filename: file.name,
            status: result.status,
            progress: 0,
            chunksProcessed: 0,
            totalChunks: 0,
            entriesCreated: 0
          };

          setIngestionJobs(prev => [...prev, newJob]);

          // Start polling for job status
          pollJobStatus(result.job_id);

          // Add confirmation message
          const uploadMessage: Message = {
            role: 'system',
            content: `📄 **File Upload Started**: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)

The file is being processed with intelligent chunking and context preservation. You'll see progress updates below.`,
            timestamp: new Date().toISOString(),
            metadata: {
              contextTokens: 0
            }
          };

          setMessages(prev => [...prev, uploadMessage]);

        } else {
          throw new Error(result.detail || 'Upload failed');
        }

      } catch (error) {
        console.error('File upload failed:', error);
        const errorMessage: Message = {
          role: 'assistant',
          content: `❌ Failed to upload ${file.name}: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Job status polling
  const pollJobStatus = async (jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/knowledge/job-status/${jobId}`);
        const jobStatus = await response.json();

        setIngestionJobs(prev => 
          prev.map(job => 
            job.jobId === jobId 
              ? { ...job, ...jobStatus }
              : job
          )
        );

        if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
          clearInterval(pollInterval);

          const completionMessage: Message = {
            role: 'system',
            content: jobStatus.status === 'completed' 
              ? `✅ **Processing Complete**: ${jobStatus.filename}

📊 **Results:**
• ${jobStatus.totalChunks} intelligent chunks created
• ${jobStatus.entriesCreated} knowledge entries added
• Ready for enhanced search and analysis

The document is now fully integrated into your knowledge base with context preservation and semantic search capabilities.`
              : `❌ **Processing Failed**: ${jobStatus.filename}

Error: ${jobStatus.errorMessage}`,
            timestamp: new Date().toISOString(),
            isError: jobStatus.status === 'failed'
          };

          setMessages(prev => [...prev, completionMessage]);
        }

      } catch (error) {
        console.error('Failed to poll job status:', error);
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  // Advanced search functionality
  const performAdvancedSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await fetch('/api/v1/knowledge/search-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          searchType: 'hybrid',
          limit: 20,
          userId,
          includeMetadata: true,
          includeHighlights: true
        })
      });

      const results = await response.json();
      setSearchResults(results.results || []);

    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  // Utility functions
  const detectTaskType = (message: string): string => {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('code') || lowerMessage.includes('script')) return 'code_generation';
    if (lowerMessage.includes('analyze') || lowerMessage.includes('compare')) return 'complex_reasoning';
    if (lowerMessage.includes('summarize') || lowerMessage.includes('summary')) return 'summarization';
    if (lowerMessage.includes('upload') || lowerMessage.includes('file')) return 'file_processing';
    return 'general';
  };

  const generateSessionId = (): string => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'processing': 
      case 'chunking': 
      case 'storing': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card className="flex flex-col" style={{ height }}>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center justify-between">
          {title}
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-xs">
              Context: {maxContextTokens.toLocaleString()} tokens
            </Badge>
            <Badge variant="outline" className="text-xs">
              {dashboardType}
            </Badge>
          </div>
        </CardTitle>
        <p className="text-xs text-muted-foreground">
          Enterprise AI Platform • Large Context Windows • Multi-Format Processing
        </p>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="chat" className="flex items-center space-x-1">
              <MessageSquare className="w-4 h-4" />
              <span>Chat</span>
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center space-x-1">
              <FileUpload className="w-4 h-4" />
              <span>Upload</span>
            </TabsTrigger>
            <TabsTrigger value="search" className="flex items-center space-x-1">
              <Search className="w-4 h-4" />
              <span>Search</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-1">
              <Database className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-3 mb-4">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-3 rounded-lg ${
                    message.role === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : message.isError 
                        ? 'bg-red-50 text-red-800 border border-red-200'
                        : message.role === 'system'
                          ? 'bg-yellow-50 text-yellow-800 border border-yellow-200'
                          : 'bg-gray-50 text-gray-800'
                  }`}>
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    
                    {message.metadata && (
                      <div className="mt-3 pt-2 border-t border-gray-200 text-xs">
                        <div className="grid grid-cols-2 gap-2">
                          {message.metadata.model && (
                            <div>Model: <span className="font-mono">{message.metadata.model}</span></div>
                          )}
                          {message.metadata.latency && (
                            <div>Latency: <span className="font-mono">{message.metadata.latency}ms</span></div>
                          )}
                          {message.metadata.contextTokens !== undefined && (
                            <div>Context: <span className="font-mono">{message.metadata.contextTokens.toLocaleString()} tokens</span></div>
                          )}
                          {message.metadata.contextUsed !== undefined && (
                            <div>Sources: <span className="font-mono">{message.metadata.contextUsed} items</span></div>
                          )}
                        </div>
                        
                        {message.metadata.sources && message.metadata.sources.length > 0 && (
                          <div className="mt-2">
                            <div className="font-medium mb-1">Sources:</div>
                            <div className="space-y-1">
                              {message.metadata.sources.slice(0, 3).map((source, i) => (
                                <div key={i} className="flex items-center justify-between">
                                  <span className="truncate">{source.title}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {Math.round(source.relevance * 100)}%
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <Input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask Sophia about ${dashboardType} data with enhanced context...`}
                disabled={loading}
                className="flex-1"
              />
              <Button onClick={sendMessage} disabled={loading || !input.trim()}>
                {loading ? '⏳' : '📤'}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="upload" className="flex-1 flex flex-col">
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  accept=".pdf,.docx,.doc,.txt,.csv,.json,.xlsx,.xls,.pptx,.ppt,.md,.rtf"
                />
                <Button onClick={() => fileInputRef.current?.click()} className="mb-2">
                  <FileUpload className="w-4 h-4 mr-2" />
                  Upload Documents
                </Button>
                <p className="text-sm text-gray-600">
                  Support for PDF, Word, Excel, PowerPoint, CSV, JSON, Text files
                  <br />
                  Maximum file size: 100MB • Intelligent chunking with context preservation
                </p>
              </div>

              {/* Processing Jobs */}
              {ingestionJobs.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-medium">Processing Jobs</h3>
                  {ingestionJobs.map((job) => (
                    <div key={job.jobId} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-sm">{job.filename}</span>
                        <Badge className={`${getStatusColor(job.status)} text-white`}>
                          {job.status}
                        </Badge>
                      </div>
                      
                      {job.status !== 'completed' && job.status !== 'failed' && (
                        <Progress value={job.progress} className="mb-2" />
                      )}
                      
                      <div className="text-xs text-gray-600 grid grid-cols-2 gap-2">
                        <div>Progress: {job.progress.toFixed(1)}%</div>
                        <div>Chunks: {job.chunksProcessed}/{job.totalChunks}</div>
                        <div>Entries: {job.entriesCreated}</div>
                        <div>Status: {job.status}</div>
                      </div>
                      
                      {job.errorMessage && (
                        <div className="mt-2 text-xs text-red-600">
                          Error: {job.errorMessage}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="search" className="flex-1 flex flex-col">
            <div className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search across all documents with semantic understanding..."
                  className="flex-1"
                />
                <Button onClick={performAdvancedSearch} disabled={!searchQuery.trim()}>
                  <Search className="w-4 h-4" />
                </Button>
              </div>

              {searchResults.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-medium">Search Results ({searchResults.length})</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {searchResults.map((result, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm">{result.title}</h4>
                          <Badge variant="outline">
                            {Math.round(result.similarity_score * 100)}% match
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {result.content?.substring(0, 200)}...
                        </p>
                        <div className="text-xs text-gray-500">
                          Category: {result.category_name}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="flex-1 flex flex-col">
            <div className="space-y-4">
              <h3 className="font-medium">Context & Performance Analytics</h3>
              
              {contextStats && Object.keys(contextStats).length > 0 && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="border rounded-lg p-3">
                    <div className="text-sm font-medium">Context Usage</div>
                    <div className="text-2xl font-bold">{contextStats.total_items || 0}</div>
                    <div className="text-xs text-gray-600">Items in context</div>
                  </div>
                  
                  <div className="border rounded-lg p-3">
                    <div className="text-sm font-medium">Token Usage</div>
                    <div className="text-2xl font-bold">
                      {contextStats.total_tokens ? contextStats.total_tokens.toLocaleString() : 0}
                    </div>
                    <div className="text-xs text-gray-600">Tokens processed</div>
                  </div>
                  
                  {contextStats.types && (
                    <div className="col-span-2 border rounded-lg p-3">
                      <div className="text-sm font-medium mb-2">Context Breakdown</div>
                      <div className="space-y-1">
                        {Object.entries(contextStats.types).map(([type, count]) => (
                          <div key={type} className="flex justify-between text-sm">
                            <span className="capitalize">{type}:</span>
                            <span>{count as number}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              <div className="text-sm text-gray-600">
                This analytics view shows real-time context usage, token consumption, and processing performance to help optimize your AI interactions.
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default EnhancedUniversalChatInterface; 