import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge, Alert, AlertDescription, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';
import { Send, Loader2, MessageCircle, RefreshCw, BrainCircuit } from 'lucide-react';
import apiClient from '../../services/apiClient';

const EnhancedUnifiedChat = ({ initialContext = 'business_intelligence' }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [searchContext, setSearchContext] = useState(initialContext);
    const [userId, setUserId] = useState('ceo-user-123'); // Example user ID
    const ws = useRef(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    useEffect(() => {
        const connect = () => {
            // Use a dynamic URL with the user ID
            const wsUrl = apiClient.defaults.baseURL.replace(/^http/, 'ws') + `/api/v1/chat/ws/${userId}`;
            ws.current = new WebSocket(wsUrl);

            ws.current.onopen = () => console.log("WebSocket Connected");
            ws.current.onclose = () => setTimeout(connect, 5000); // Reconnect after 5s
            ws.current.onerror = (err) => console.error("WebSocket Error:", err);

            ws.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setIsLoading(false);

                if (data.type === 'response') {
                    setMessages(prev => [...prev, { type: 'assistant', ...data.data }]);
                } else if (data.type === 'error') {
                     setError(data.message);
                }
            };
        };

        connect();

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [userId]);

    const handleSendMessage = () => {
        if (!input.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) return;

        const userMessage = { type: 'user', message: input, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        ws.current.send(JSON.stringify({
            message: input,
            search_context: searchContext,
            // Future-proofing: send access level if available
            // access_level: "ceo"
        }));
        setInput('');
    };

    const renderMessageContent = (msg) => {
        return (
            <div>
                <p className="whitespace-pre-wrap">{msg.response || msg.message}</p>
                {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2">
                        <h4 className="text-xs font-semibold">Sources:</h4>
                        <div className="flex flex-wrap gap-2 mt-1">
                            {msg.sources.map((source, i) => (
                                <Badge key={i} variant="secondary">{source.title}</Badge>
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
            </div>
        );
    };

    return (
        <Card className="h-[80vh] flex flex-col">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-2">
                    <BrainCircuit className="h-5 w-5" />
                    <CardTitle>Unified AI Chat</CardTitle>
                </div>
                <Select value={searchContext} onValueChange={setSearchContext}>
                    <SelectTrigger className="w-[200px]">
                        <SelectValue placeholder="Select context..." />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="business_intelligence">Business Intelligence</SelectItem>
                        <SelectItem value="ceo_deep_research">Unified Deep Research</SelectItem>
                        <SelectItem value="internal_only">Internal Knowledge</SelectItem>
                        <SelectItem value="blended_intelligence">Blended Intelligence</SelectItem>
                    </SelectContent>
                </Select>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex items-end gap-2 ${msg.type === 'user' ? 'justify-end' : ''}`}>
                        <div className={`p-3 rounded-lg max-w-[80%] ${msg.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}>
                            {renderMessageContent(msg)}
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </CardContent>
            {error && <Alert variant="destructive" className="m-4"><AlertTriangle className="h-4 w-4" /><AlertDescription>{error}</AlertDescription></Alert>}
            <div className="p-4 border-t">
                <div className="flex items-center space-x-2">
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask anything..."
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        disabled={isLoading}
                    />
                    <Button onClick={handleSendMessage} disabled={isLoading || !input.trim()}>
                        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default EnhancedUnifiedChat;
