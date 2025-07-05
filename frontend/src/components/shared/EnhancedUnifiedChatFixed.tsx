import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge, Alert, AlertDescription, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';
import { Send, Loader2, MessageCircle, RefreshCw, BrainCircuit, AlertTriangle } from 'lucide-react';
import apiClient from '../../services/apiClient';

const EnhancedUnifiedChatFixed = ({ initialContext = 'business_intelligence' }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchContext, setSearchContext] = useState(initialContext);
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef(null);
    const messagesEndRef = useRef(null);
    const reconnectTimeout = useRef(null);

    // Get user ID from localStorage or generate one
    const userId = localStorage.getItem('userId') || 'user_' + Math.random().toString(36).substr(2, 9);
    if (!localStorage.getItem('userId')) {
        localStorage.setItem('userId', userId);
    }

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const connect = () => {
        // Use the correct WebSocket endpoint that exists: /api/v1/chat/ws/{user_id}
        const wsUrl = apiClient.defaults.baseURL.replace(/^http/, 'ws') + '/api/v1/chat/ws/' + userId;

        console.log('Connecting to WebSocket:', wsUrl);
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log("WebSocket Connected");
            setIsConnected(true);
            setError(null);

            // Clear any reconnect timeout
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
                reconnectTimeout.current = null;
            }
        };

        ws.current.onclose = () => {
            console.log("WebSocket Disconnected");
            setIsConnected(false);

            // Attempt to reconnect after 5 seconds
            reconnectTimeout.current = setTimeout(() => {
                console.log("Attempting to reconnect...");
                connect();
            }, 5000);
        };

        ws.current.onerror = (err) => {
            console.error("WebSocket Error:", err);
            setError("Connection error. Retrying...");
        };

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("Received message:", data);

                setIsLoading(false);

                if (data.type === 'chat_response' || data.type === 'integrated_response') {
                    const responseData = data.data || data;
                    setMessages(prev => [...prev, {
                        type: 'assistant',
                        message: responseData.content || responseData.response,
                        sources: responseData.sources,
                        suggestions: responseData.suggestions,
                        metadata: responseData.metadata,
                        timestamp: responseData.timestamp || new Date().toISOString()
                    }]);
                } else if (data.type === 'error') {
                    setError(data.message);
                } else if (data.type === 'typing') {
                    // Show typing indicator
                } else if (data.type === 'pong') {
                    // Heartbeat response
                }
            } catch (e) {
                console.error("Error parsing message:", e);
            }
        };
    };

    useEffect(() => {
        connect();

        // Cleanup on unmount
        return () => {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    // Send heartbeat every 30 seconds to keep connection alive
    useEffect(() => {
        const heartbeatInterval = setInterval(() => {
            if (ws.current && ws.current.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000);

        return () => clearInterval(heartbeatInterval);
    }, []);

    const handleSendMessage = () => {
        if (!input.trim()) return;

        if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
            setError("Not connected. Please wait...");
            return;
        }

        const userMessage = {
            type: 'user',
            message: input,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        // Send message with proper format for the WebSocket endpoint
        ws.current.send(JSON.stringify({
            type: 'chat_message',
            message: input,
            context: searchContext,
            metadata: {
                search_context: searchContext,
                user_id: userId
            }
        }));

        setInput('');
    };

    const renderMessageContent = (msg) => {
        return (
            <div>
                <p className="whitespace-pre-wrap">{msg.message}</p>
                {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2">
                        <h4 className="text-xs font-semibold">Sources:</h4>
                        <div className="flex flex-wrap gap-2 mt-1">
                            {msg.sources.map((source, i) => (
                                <Badge key={i} variant="secondary">{source.title || source}</Badge>
                            ))}
                        </div>
                    </div>
                )}
                {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="mt-3">
                        <h4 className="text-xs font-semibold mb-1">Suggested Questions:</h4>
                        <div className="flex flex-wrap gap-2">
                            {msg.suggestions.map((s, i) => (
                                <Button key={i} size="sm" variant="outline" onClick={() => setInput(s)}>{s}</Button>
                            ))}
                        </div>
                    </div>
                )}
                {msg.metadata && msg.metadata.confidence && (
                    <div className="mt-2 text-xs text-gray-500">
                        Confidence: {(msg.metadata.confidence * 100).toFixed(1)}%
                    </div>
                )}
            </div>
        );
    };

    return (
        <Card className="h-[80vh] flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-2">
                    <BrainCircuit className="h-5 w-5" />
                    <CardTitle>Unified AI Chat</CardTitle>
                    {isConnected && (
                        <Badge variant="success" className="ml-2">Connected</Badge>
                    )}
                    {!isConnected && (
                        <Badge variant="secondary" className="ml-2">Connecting...</Badge>
                    )}
                </div>
                <Select value={searchContext} onValueChange={setSearchContext}>
                    <SelectTrigger className="w-[200px]">
                        <SelectValue placeholder="Select context..." />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="business_intelligence">Business Intelligence</SelectItem>
                        <SelectItem value="ceo_deep_research">CEO Deep Research</SelectItem>
                        <SelectItem value="internal_only">Internal Knowledge</SelectItem>
                        <SelectItem value="blended_intelligence">Blended Intelligence</SelectItem>
                        <SelectItem value="unified_intelligence">Unified Intelligence</SelectItem>
                    </SelectContent>
                </Select>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-8">
                        <BrainCircuit className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                        <p>Start a conversation with Sophia AI</p>
                        <p className="text-sm mt-2">Ask about business metrics, projects, or any other topic</p>
                    </div>
                )}
                {messages.map((msg, index) => (
                    <div key={index} className={`flex items-end gap-2 ${msg.type === 'user' ? 'justify-end' : ''}`}>
                        <div className={`p-3 rounded-lg max-w-[80%] ${msg.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
                            {renderMessageContent(msg)}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-center gap-2">
                        <div className="p-3 rounded-lg bg-gray-100">
                            <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </CardContent>
            {error && (
                <Alert variant="destructive" className="m-4">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}
            <div className="p-4 border-t">
                <div className="flex items-center space-x-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder={isConnected ? "Ask anything..." : "Connecting..."}
                        onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                        disabled={isLoading || !isConnected}
                    />
                    <Button
                        onClick={handleSendMessage}
                        disabled={isLoading || !input.trim() || !isConnected}
                    >
                        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default EnhancedUnifiedChatFixed;
