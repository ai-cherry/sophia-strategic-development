import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Send, Loader2, MessageCircle, RefreshCw, BrainCircuit, AlertTriangle } from 'lucide-react';
import apiClient from '../../services/apiClient';

const EnhancedUnifiedChat = ({ initialContext = 'business_intelligence' }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchContext, setSearchContext] = useState(initialContext);
    const [userId, setUserId] = useState('ceo-user-123');
    const ws = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    useEffect(() => {
        connectWebSocket();
        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, []);

    const connectWebSocket = () => {
        const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'message') {
                setMessages(prev => [...prev, data.message]);
            }
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
            setError('Connection error. Please refresh the page.');
        };

        ws.current.onclose = () => {
            console.log('WebSocket disconnected');
            setTimeout(connectWebSocket, 5000);
        };
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = {
            type: 'user',
            content: input,
            timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await apiClient.post('/api/v3/chat/unified', {
                message: input,
                searchContext,
                userId,
                sessionId: Date.now().toString(),
            });

            const aiMessage = {
                type: 'assistant',
                content: response.data.response,
                citations: response.data.citations,
                timestamp: new Date().toISOString(),
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
            console.error('Chat error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const renderMessageContent = (msg) => {
        if (msg.type === 'user') {
            return <div className="text-white">{msg.content}</div>;
        }

        return (
            <div className="space-y-2">
                <div className="text-gray-50">{msg.content}</div>
                {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 border-t border-gray-700">
                        <p className="text-xs text-gray-400 mb-1">Sources:</p>
                        {msg.citations.map((citation, idx) => (
                            <Badge
                                key={idx}
                                variant="outline"
                                className="text-xs mr-1 mb-1 bg-gray-800 border-gray-700 text-gray-300"
                            >
                                {citation.source}
                            </Badge>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <Card className="h-[80vh] flex flex-col bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between bg-gray-800 border-b border-gray-700">
                <div className="flex items-center space-x-2">
                    <BrainCircuit className="h-5 w-5 text-purple-500" />
                    <CardTitle className="text-gray-50">Unified AI Chat</CardTitle>
                </div>
                <Select value={searchContext} onValueChange={setSearchContext}>
                    <SelectTrigger className="w-[200px] bg-gray-900 border-gray-700 text-gray-50">
                        <SelectValue placeholder="Select context..." />
                    </SelectTrigger>
                    <SelectContent className="bg-gray-900 border-gray-700">
                        <SelectItem value="business_intelligence">Business Intelligence</SelectItem>
                        <SelectItem value="ceo_deep_research">Unified Deep Research</SelectItem>
                        <SelectItem value="internal_only">Internal Knowledge</SelectItem>
                        <SelectItem value="blended_intelligence">Blended Intelligence</SelectItem>
                    </SelectContent>
                </Select>
            </CardHeader>

            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex items-end gap-2 ${msg.type === 'user' ? 'justify-end' : ''}`}
                    >
                        <div className={`p-3 rounded-lg max-w-[80%] ${
                            msg.type === 'user'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-800 border border-gray-700'
                        }`}>
                            {renderMessageContent(msg)}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex items-center gap-2 text-gray-400">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm">AI is thinking...</span>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </CardContent>

            {error && (
                <Alert variant="destructive" className="m-4 bg-red-900/20 border-red-800">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <div className="p-4 border-t border-gray-800 bg-gray-800">
                <div className="flex gap-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
                        placeholder="Ask anything about your business..."
                        disabled={isLoading}
                        className="flex-1 bg-gray-900 border-gray-700 text-gray-50 placeholder-gray-400"
                    />
                    <Button
                        onClick={sendMessage}
                        disabled={isLoading || !input.trim()}
                        className="bg-purple-600 hover:bg-purple-700 text-white"
                    >
                        {isLoading ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                            <Send className="h-4 w-4" />
                        )}
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default EnhancedUnifiedChat;
