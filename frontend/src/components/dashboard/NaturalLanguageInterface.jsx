import React, { useState, useRef } from 'react';

const NaturalLanguageInterface = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setLoading(true);
    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          context: messages.slice(-5),
        }),
      });
      if (!response.ok) throw new Error('Failed to get response');
      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'ai', content: data.message }]);
      // Optionally handle agent action triggers here
      if (data.action_summary) {
        setMessages((prev) => [...prev, { role: 'system', content: data.action_summary }]);
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'system', content: `[Error: ${e.message}]` }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg p-4">
      <div className="h-48 overflow-y-auto mb-2 bg-slate-900 rounded p-2">
        {messages.map((msg, i) => (
          <div key={i} className={`mb-1 ${msg.role === 'user' ? 'text-blue-300' : msg.role === 'ai' ? 'text-green-300' : 'text-yellow-300'}`}>{msg.content}</div>
        ))}
        {loading && <div className="text-gray-400">AI is thinking...</div>}
      </div>
      <div className="flex gap-2">
        <input
          ref={inputRef}
          className="flex-1 bg-slate-700 text-white rounded px-3 py-2"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
          placeholder="Ask anything or issue a command..."
          disabled={loading}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={sendMessage}
          disabled={loading}
        >Send</button>
      </div>
    </div>
  );
};

export default NaturalLanguageInterface; 