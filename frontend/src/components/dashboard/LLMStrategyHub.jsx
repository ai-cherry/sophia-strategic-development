import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';

const LLMStrategyHub = () => {
  const [llmMetrics, setLlmMetrics] = useState({
    totalRequests: 0,
    totalCost: 0,
    averageLatency: 0,
    modelDistribution: {}
  });
  const [activeModels, setActiveModels] = useState([]);
  const [routingConfig, setRoutingConfig] = useState({});

  useEffect(() => {
    fetchLLMMetrics();
    fetchActiveModels();
    fetchRoutingConfig();
  }, []);

  const fetchLLMMetrics = async () => {
    try {
      const response = await fetch('/api/v1/llm/metrics');
      const data = await response.json();
      setLlmMetrics(data);
    } catch (error) {
      console.error('Failed to fetch LLM metrics:', error);
    }
  };

  const fetchActiveModels = async () => {
    try {
      const response = await fetch('/api/v1/llm/models');
      const data = await response.json();
      setActiveModels(data);
    } catch (error) {
      console.error('Failed to fetch active models:', error);
    }
  };

  const fetchRoutingConfig = async () => {
    try {
      const response = await fetch('/api/v1/llm/routing-config');
      const data = await response.json();
      setRoutingConfig(data);
    } catch (error) {
      console.error('Failed to fetch routing config:', error);
    }
  };

  const updateModelPriority = async (modelId, priority) => {
    try {
      await fetch('/api/v1/llm/models/priority', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modelId, priority })
      });
      fetchActiveModels();
    } catch (error) {
      console.error('Failed to update model priority:', error);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🧠 Sophia LLM Strategy Hub</CardTitle>
          <p className="text-sm text-muted-foreground">
            Centralized management for all AI model routing, cost optimization, and performance monitoring
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800">Total Requests</h3>
              <p className="text-2xl font-bold text-blue-600">{llmMetrics.totalRequests.toLocaleString()}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-green-800">Total Cost</h3>
              <p className="text-2xl font-bold text-green-600">${llmMetrics.totalCost.toFixed(2)}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="text-lg font-semibold text-purple-800">Avg Latency</h3>
              <p className="text-2xl font-bold text-purple-600">{llmMetrics.averageLatency}ms</p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Active OpenRouter Models</h3>
            {activeModels.map((model) => (
              <div key={model.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">{model.name}</p>
                  <p className="text-sm text-muted-foreground">
                    Usage: {model.usage}% | Cost/1K: ${model.costPer1k} | Latency: {model.avgLatency}ms
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <select
                    value={model.priority}
                    onChange={(e) => updateModelPriority(model.id, e.target.value)}
                    className="border rounded px-2 py-1"
                  >
                    <option value="high">High Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="low">Low Priority</option>
                    <option value="disabled">Disabled</option>
                  </select>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-4 border-t">
            <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
            <div className="flex space-x-2">
              <Button onClick={() => window.open('/admin/llm-config', '_blank')}>
                🔧 Advanced Config
              </Button>
              <Button variant="outline" onClick={fetchLLMMetrics}>
                🔄 Refresh Metrics
              </Button>
              <Button variant="outline" onClick={() => window.open('/admin/llm-logs', '_blank')}>
                📊 View Logs
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LLMStrategyHub; 