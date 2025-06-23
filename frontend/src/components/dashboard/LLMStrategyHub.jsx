import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

const LLMStrategyHub = () => {
  const [llmMetrics, setLlmMetrics] = useState({
    totalRequests: 0,
    totalCost: 0,
    averageLatency: 0,
    modelDistribution: {},
    cacheHitRate: 0,
    costSavings: 0
  });
  const [activeModels, setActiveModels] = useState([]);
  const [routingConfig, setRoutingConfig] = useState({});
  const [portkeyStatus, setPortkeyStatus] = useState({ status: 'healthy', latency: 0 });
  const [strategicAssignments, setStrategicAssignments] = useState({});
  const [costControls, setCostControls] = useState({});

  useEffect(() => {
    fetchLLMMetrics();
    fetchActiveModels();
    fetchRoutingConfig();
    fetchPortkeyStatus();
    fetchStrategicAssignments();
    fetchCostControls();
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

  const fetchPortkeyStatus = async () => {
    try {
      const response = await fetch('/api/v1/llm/portkey/status');
      const data = await response.json();
      setPortkeyStatus(data);
    } catch (error) {
      console.error('Failed to fetch Portkey status:', error);
    }
  };

  const fetchStrategicAssignments = async () => {
    try {
      const response = await fetch('/api/v1/llm/strategic-assignments');
      const data = await response.json();
      setStrategicAssignments(data);
    } catch (error) {
      console.error('Failed to fetch strategic assignments:', error);
    }
  };

  const fetchCostControls = async () => {
    try {
      const response = await fetch('/api/v1/llm/cost-controls');
      const data = await response.json();
      setCostControls(data);
    } catch (error) {
      console.error('Failed to fetch cost controls:', error);
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

  const updateStrategicAssignment = async (useCase, modelId) => {
    try {
      await fetch('/api/v1/llm/strategic-assignments', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ useCase, modelId })
      });
      fetchStrategicAssignments();
    } catch (error) {
      console.error('Failed to update strategic assignment:', error);
    }
  };

  const updateCostControl = async (setting, value) => {
    try {
      await fetch('/api/v1/llm/cost-controls', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ setting, value })
      });
      fetchCostControls();
    } catch (error) {
      console.error('Failed to update cost control:', error);
    }
  };

  const getModelTierBadge = (model) => {
    const tier1Models = ['gpt-4o', 'claude-3-opus', 'gemini-1.5-pro'];
    const tier2Models = ['claude-3-haiku', 'gpt-4-turbo', 'deepseek-v3'];
    
    if (tier1Models.includes(model.id)) return <Badge variant="default">Tier 1</Badge>;
    if (tier2Models.includes(model.id)) return <Badge variant="secondary">Tier 2</Badge>;
    return <Badge variant="outline">Cost Optimized</Badge>;
  };

  const getStatusBadge = (status) => {
    const colors = {
      healthy: 'bg-green-100 text-green-800',
      degraded: 'bg-yellow-100 text-yellow-800',
      unhealthy: 'bg-red-100 text-red-800'
    };
    return <span className={`px-2 py-1 rounded-full text-xs ${colors[status] || colors.healthy}`}>{status}</span>;
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>🧠 Sophia LLM Strategy Hub</span>
            <div className="flex items-center space-x-2">
              <span className="text-sm">Portkey Gateway:</span>
              {getStatusBadge(portkeyStatus.status)}
              <span className="text-xs text-muted-foreground">{portkeyStatus.latency}ms</span>
            </div>
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Enterprise LLM orchestration with Portkey gateway, OpenRouter backend, and intelligent cost optimization
          </p>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="models">Model Management</TabsTrigger>
              <TabsTrigger value="strategic">Strategic Assignments</TabsTrigger>
              <TabsTrigger value="cost">Cost Controls</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800">Total Requests</h3>
                  <p className="text-2xl font-bold text-blue-600">{llmMetrics.totalRequests.toLocaleString()}</p>
                  <p className="text-xs text-blue-600">via Portkey Gateway</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800">Total Cost</h3>
                  <p className="text-2xl font-bold text-green-600">${llmMetrics.totalCost.toFixed(2)}</p>
                  <p className="text-xs text-green-600">Saved: ${llmMetrics.costSavings.toFixed(2)}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800">Avg Latency</h3>
                  <p className="text-2xl font-bold text-purple-600">{llmMetrics.averageLatency}ms</p>
                  <p className="text-xs text-purple-600">Gateway + Model</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-orange-800">Cache Hit Rate</h3>
                  <p className="text-2xl font-bold text-orange-600">{(llmMetrics.cacheHitRate * 100).toFixed(1)}%</p>
                  <p className="text-xs text-orange-600">Semantic Caching</p>
                </div>
              </div>

              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-4">Model Distribution (Last 7 Days)</h3>
                <div className="space-y-2">
                  {Object.entries(llmMetrics.modelDistribution || {}).map(([model, percentage]) => (
                    <div key={model} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{model}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-muted-foreground">{percentage}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="models" className="space-y-4">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Active Models via Portkey + OpenRouter</h3>
                {activeModels.map((model) => (
                  <div key={model.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <p className="font-medium">{model.name}</p>
                          {getModelTierBadge(model)}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Usage: {model.usage}% | Cost/1K: ${model.costPer1k} | Latency: {model.avgLatency}ms
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Cache Hit: {model.cacheHitRate || 0}% | Quality Score: {model.qualityScore || 'N/A'}
                        </p>
                      </div>
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
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.open(`/admin/model-details/${model.id}`, '_blank')}
                      >
                        Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="strategic" className="space-y-4">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Strategic Model Assignments for Executive Use Cases</h3>
                <p className="text-sm text-muted-foreground">
                  Configure which models handle specific executive intelligence tasks
                </p>
                
                {[
                  { key: 'executive_insights', label: 'Executive Insights & Summaries', description: 'CEO dashboard insights and strategic analysis' },
                  { key: 'competitive_intelligence', label: 'Competitive Intelligence', description: 'Market analysis and competitor monitoring' },
                  { key: 'financial_analysis', label: 'Financial Analysis', description: 'Revenue metrics and financial reporting' },
                  { key: 'market_analysis', label: 'Market Analysis', description: 'Industry trends and market positioning' },
                  { key: 'operational_efficiency', label: 'Operational Efficiency', description: 'Process optimization and productivity analysis' }
                ].map((useCase) => (
                  <div key={useCase.key} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{useCase.label}</p>
                      <p className="text-sm text-muted-foreground">{useCase.description}</p>
                    </div>
                    <select
                      value={strategicAssignments[useCase.key] || 'gpt-4o'}
                      onChange={(e) => updateStrategicAssignment(useCase.key, e.target.value)}
                      className="border rounded px-3 py-2 min-w-[150px]"
                    >
                      <option value="gpt-4o">GPT-4o</option>
                      <option value="claude-3-opus">Claude 3 Opus</option>
                      <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                      <option value="claude-3-haiku">Claude 3 Haiku</option>
                      <option value="deepseek-v3">DeepSeek V3</option>
                    </select>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="cost" className="space-y-4">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Cost Management & Optimization</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Monthly Budget Control</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Budget Limit:</span>
                        <input 
                          type="number" 
                          value={costControls.monthlyBudget || 2000}
                          onChange={(e) => updateCostControl('monthlyBudget', e.target.value)}
                          className="border rounded px-2 py-1 w-20 text-sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Alert at:</span>
                        <input 
                          type="number" 
                          value={costControls.alertThreshold || 75}
                          onChange={(e) => updateCostControl('alertThreshold', e.target.value)}
                          className="border rounded px-2 py-1 w-16 text-sm"
                        />
                        <span className="text-sm">%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Auto-downgrade at:</span>
                        <input 
                          type="number" 
                          value={costControls.autoDowngradeThreshold || 90}
                          onChange={(e) => updateCostControl('autoDowngradeThreshold', e.target.value)}
                          className="border rounded px-2 py-1 w-16 text-sm"
                        />
                        <span className="text-sm">%</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Caching Configuration</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Similarity Threshold:</span>
                        <input 
                          type="number" 
                          step="0.01"
                          min="0.8"
                          max="0.99"
                          value={costControls.cacheThreshold || 0.92}
                          onChange={(e) => updateCostControl('cacheThreshold', e.target.value)}
                          className="border rounded px-2 py-1 w-16 text-sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Cache TTL (hours):</span>
                        <input 
                          type="number" 
                          value={costControls.cacheTTL || 24}
                          onChange={(e) => updateCostControl('cacheTTL', e.target.value)}
                          className="border rounded px-2 py-1 w-16 text-sm"
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Max Cache Size (GB):</span>
                        <input 
                          type="number" 
                          value={costControls.maxCacheSize || 50}
                          onChange={(e) => updateCostControl('maxCacheSize', e.target.value)}
                          className="border rounded px-2 py-1 w-16 text-sm"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <h4 className="font-medium mb-2">Emergency Fallback Settings</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Emergency Model:</span>
                    <select
                      value={costControls.emergencyModel || 'llama-3-70b'}
                      onChange={(e) => updateCostControl('emergencyModel', e.target.value)}
                      className="border rounded px-2 py-1"
                    >
                      <option value="llama-3-70b">Llama 3 70B (Cost Effective)</option>
                      <option value="qwen2-72b">Qwen2 72B</option>
                      <option value="mixtral-8x22b">Mixtral 8x22B</option>
                    </select>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-6 pt-4 border-t">
            <h3 className="text-lg font-semibold mb-2">Quick Actions</h3>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => window.open('/admin/portkey-dashboard', '_blank')}>
                🚀 Portkey Dashboard
              </Button>
              <Button variant="outline" onClick={() => window.open('/admin/openrouter-console', '_blank')}>
                🔗 OpenRouter Console
              </Button>
              <Button variant="outline" onClick={fetchLLMMetrics}>
                🔄 Refresh All Metrics
              </Button>
              <Button variant="outline" onClick={() => window.open('/admin/llm-logs', '_blank')}>
                📊 View Detailed Logs
              </Button>
              <Button variant="outline" onClick={() => window.open('/admin/cost-analysis', '_blank')}>
                💰 Cost Analysis
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default LLMStrategyHub; 