"""
Enhanced Retool Visual Workflow Designer
Provides Lucidchart-like visual workflow creation with real-time collaboration
"""

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Workflow,
  Plus,
  Save,
  Play,
  Pause,
  RotateCcw,
  Share2,
  Users,
  Settings,
  Database,
  MessageSquare,
  Brain,
  Zap,
  GitBranch,
  Timer,
  CheckCircle,
  AlertCircle,
  Eye,
  Edit3
} from 'lucide-react';

// Types
interface WorkflowNode {
  id: string;
  type: 'trigger' | 'action' | 'condition' | 'data' | 'ai' | 'human';
  position: { x: number; y: number };
  data: {
    label: string;
    description?: string;
    config: Record<string, any>;
    status?: 'idle' | 'running' | 'success' | 'error';
  };
  inputs: string[];
  outputs: string[];
}

interface WorkflowConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  animated?: boolean;
  style?: Record<string, any>;
}

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  thumbnail?: string;
}

interface CollaborationCursor {
  userId: string;
  userName: string;
  position: { x: number; y: number };
  color: string;
  timestamp: number;
}

// Component Library
const NodeTypes = {
  trigger: {
    icon: Play,
    color: 'bg-green-500',
    label: 'Trigger',
    description: 'Starts the workflow'
  },
  action: {
    icon: Zap,
    color: 'bg-blue-500',
    label: 'Action',
    description: 'Performs an operation'
  },
  condition: {
    icon: GitBranch,
    color: 'bg-yellow-500',
    label: 'Condition',
    description: 'Makes a decision'
  },
  data: {
    icon: Database,
    color: 'bg-purple-500',
    label: 'Data',
    description: 'Processes data'
  },
  ai: {
    icon: Brain,
    color: 'bg-pink-500',
    label: 'AI Agent',
    description: 'AI-powered processing'
  },
  human: {
    icon: Users,
    color: 'bg-orange-500',
    label: 'Human Task',
    description: 'Requires human input'
  }
};

// Workflow Templates
const WorkflowTemplates: WorkflowTemplate[] = [
  {
    id: 'apartment-lead-processing',
    name: 'Apartment Lead Processing',
    description: 'Automatically process and qualify apartment leads',
    category: 'Sales',
    nodes: [
      {
        id: 'trigger-1',
        type: 'trigger',
        position: { x: 100, y: 100 },
        data: {
          label: 'New Lead',
          config: { source: 'website_form' }
        },
        inputs: [],
        outputs: ['lead-data']
      },
      {
        id: 'ai-1',
        type: 'ai',
        position: { x: 300, y: 100 },
        data: {
          label: 'Lead Qualification',
          config: { agent: 'sophia-lead-qualifier' }
        },
        inputs: ['lead-data'],
        outputs: ['qualified-lead', 'rejected-lead']
      },
      {
        id: 'action-1',
        type: 'action',
        position: { x: 500, y: 50 },
        data: {
          label: 'Send to CRM',
          config: { system: 'hubspot' }
        },
        inputs: ['qualified-lead'],
        outputs: []
      },
      {
        id: 'action-2',
        type: 'action',
        position: { x: 500, y: 150 },
        data: {
          label: 'Send Rejection Email',
          config: { template: 'polite-rejection' }
        },
        inputs: ['rejected-lead'],
        outputs: []
      }
    ],
    connections: [
      { id: 'c1', source: 'trigger-1', target: 'ai-1' },
      { id: 'c2', source: 'ai-1', target: 'action-1', sourceHandle: 'qualified-lead' },
      { id: 'c3', source: 'ai-1', target: 'action-2', sourceHandle: 'rejected-lead' }
    ]
  },
  {
    id: 'maintenance-request',
    name: 'Maintenance Request Processing',
    description: 'Automate maintenance request handling and scheduling',
    category: 'Operations',
    nodes: [
      {
        id: 'trigger-1',
        type: 'trigger',
        position: { x: 100, y: 100 },
        data: {
          label: 'Maintenance Request',
          config: { source: 'tenant_portal' }
        },
        inputs: [],
        outputs: ['request-data']
      },
      {
        id: 'ai-1',
        type: 'ai',
        position: { x: 300, y: 100 },
        data: {
          label: 'Categorize & Prioritize',
          config: { agent: 'sophia-maintenance-classifier' }
        },
        inputs: ['request-data'],
        outputs: ['urgent', 'normal', 'low-priority']
      },
      {
        id: 'human-1',
        type: 'human',
        position: { x: 500, y: 50 },
        data: {
          label: 'Emergency Response',
          config: { assignee: 'maintenance-manager' }
        },
        inputs: ['urgent'],
        outputs: []
      },
      {
        id: 'action-1',
        type: 'action',
        position: { x: 500, y: 100 },
        data: {
          label: 'Schedule Maintenance',
          config: { system: 'maintenance-calendar' }
        },
        inputs: ['normal'],
        outputs: []
      },
      {
        id: 'action-2',
        type: 'action',
        position: { x: 500, y: 150 },
        data: {
          label: 'Add to Backlog',
          config: { system: 'task-queue' }
        },
        inputs: ['low-priority'],
        outputs: []
      }
    ],
    connections: [
      { id: 'c1', source: 'trigger-1', target: 'ai-1' },
      { id: 'c2', source: 'ai-1', target: 'human-1', sourceHandle: 'urgent' },
      { id: 'c3', source: 'ai-1', target: 'action-1', sourceHandle: 'normal' },
      { id: 'c4', source: 'ai-1', target: 'action-2', sourceHandle: 'low-priority' }
    ]
  }
];

// Custom Hooks
const useWorkflowDesigner = () => {
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [connections, setConnections] = useState<WorkflowConnection[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);

  const addNode = useCallback((type: keyof typeof NodeTypes, position: { x: number; y: number }) => {
    const newNode: WorkflowNode = {
      id: `${type}-${Date.now()}`,
      type,
      position,
      data: {
        label: NodeTypes[type].label,
        config: {}
      },
      inputs: type === 'trigger' ? [] : ['input'],
      outputs: ['output']
    };
    setNodes(prev => [...prev, newNode]);
  }, []);

  const updateNode = useCallback((nodeId: string, updates: Partial<WorkflowNode>) => {
    setNodes(prev => prev.map(node =>
      node.id === nodeId ? { ...node, ...updates } : node
    ));
  }, []);

  const deleteNode = useCallback((nodeId: string) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setConnections(prev => prev.filter(conn =>
      conn.source !== nodeId && conn.target !== nodeId
    ));
  }, []);

  const addConnection = useCallback((source: string, target: string) => {
    const newConnection: WorkflowConnection = {
      id: `${source}-${target}`,
      source,
      target,
      animated: false
    };
    setConnections(prev => [...prev, newConnection]);
  }, []);

  const executeWorkflow = useCallback(async () => {
    setIsExecuting(true);
    try {
      const response = await fetch('/api/v1/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, connections })
      });
      const result = await response.json();
      setExecutionHistory(prev => [result, ...prev]);
    } catch (error) {
      console.error('Workflow execution failed:', error);
    } finally {
      setIsExecuting(false);
    }
  }, [nodes, connections]);

  const loadTemplate = useCallback((template: WorkflowTemplate) => {
    setNodes(template.nodes);
    setConnections(template.connections);
  }, []);

  return {
    nodes,
    connections,
    selectedNode,
    isExecuting,
    executionHistory,
    addNode,
    updateNode,
    deleteNode,
    addConnection,
    executeWorkflow,
    loadTemplate,
    setSelectedNode
  };
};

const useCollaboration = (workflowId: string) => {
  const [collaborators, setCollaborators] = useState<CollaborationCursor[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // WebSocket connection for real-time collaboration
    const ws = new WebSocket(`ws://localhost:8000/api/v1/workflows/${workflowId}/collaborate`);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'cursor_update') {
        setCollaborators(prev => {
          const filtered = prev.filter(c => c.userId !== data.userId);
          return [...filtered, data.cursor];
        });
      }
    };

    return () => ws.close();
  }, [workflowId]);

  const updateCursor = useCallback((position: { x: number; y: number }) => {
    // Send cursor position to other collaborators
    // Implementation would send via WebSocket
  }, []);

  return { collaborators, isConnected, updateCursor };
};

// Components
const NodeComponent: React.FC<{
  node: WorkflowNode;
  isSelected: boolean;
  onSelect: () => void;
  onUpdate: (updates: Partial<WorkflowNode>) => void;
}> = ({ node, isSelected, onSelect, onUpdate }) => {
  const nodeType = NodeTypes[node.type];
  const Icon = nodeType.icon;

  return (
    <div
      className={`absolute cursor-pointer transition-all duration-200 ${
        isSelected ? 'ring-2 ring-blue-500 scale-105' : ''
      }`}
      style={{ left: node.position.x, top: node.position.y }}
      onClick={onSelect}
    >
      <Card className="w-48 shadow-lg hover:shadow-xl">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <div className={`w-6 h-6 rounded-full ${nodeType.color} flex items-center justify-center`}>
              <Icon className="w-3 h-3 text-white" />
            </div>
            {node.data.label}
            {node.data.status && (
              <Badge variant={node.data.status === 'success' ? 'default' : 'destructive'} className="ml-auto">
                {node.data.status}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-xs text-gray-600">{nodeType.description}</p>
          {node.data.description && (
            <p className="text-xs text-gray-500 mt-1">{node.data.description}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

const TemplateLibrary: React.FC<{
  onSelectTemplate: (template: WorkflowTemplate) => void;
}> = ({ onSelectTemplate }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const categories = ['All', ...Array.from(new Set(WorkflowTemplates.map(t => t.category)))];
  const filteredTemplates = selectedCategory === 'All'
    ? WorkflowTemplates
    : WorkflowTemplates.filter(t => t.category === selectedCategory);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {categories.map(category => (
          <Button
            key={category}
            variant={selectedCategory === category ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory(category)}
          >
            {category}
          </Button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredTemplates.map(template => (
          <Card key={template.id} className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="text-sm">{template.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-gray-600 mb-3">{template.description}</p>
              <div className="flex justify-between items-center">
                <Badge variant="outline">{template.category}</Badge>
                <Button size="sm" onClick={() => onSelectTemplate(template)}>
                  Use Template
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

const NodePalette: React.FC<{
  onAddNode: (type: keyof typeof NodeTypes) => void;
}> = ({ onAddNode }) => {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">Components</h3>
      {Object.entries(NodeTypes).map(([type, config]) => {
        const Icon = config.icon;
        return (
          <Button
            key={type}
            variant="outline"
            size="sm"
            className="w-full justify-start"
            onClick={() => onAddNode(type as keyof typeof NodeTypes)}
          >
            <div className={`w-4 h-4 rounded-full ${config.color} flex items-center justify-center mr-2`}>
              <Icon className="w-2 h-2 text-white" />
            </div>
            {config.label}
          </Button>
        );
      })}
    </div>
  );
};

const CollaborationPanel: React.FC<{
  collaborators: CollaborationCursor[];
  isConnected: boolean;
}> = ({ collaborators, isConnected }) => {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <h3 className="text-sm font-semibold">Collaboration</h3>
        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>

      {collaborators.length === 0 ? (
        <p className="text-xs text-gray-500">No other users online</p>
      ) : (
        <div className="space-y-1">
          {collaborators.map(collaborator => (
            <div key={collaborator.userId} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: collaborator.color }}
              />
              <span className="text-xs">{collaborator.userName}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main Component
const EnhancedRetoolWorkflowDesigner: React.FC = () => {
  const workflowId = 'demo-workflow';
  const {
    nodes,
    connections,
    selectedNode,
    isExecuting,
    executionHistory,
    addNode,
    updateNode,
    deleteNode,
    addConnection,
    executeWorkflow,
    loadTemplate,
    setSelectedNode
  } = useWorkflowDesigner();

  const { collaborators, isConnected, updateCursor } = useCollaboration(workflowId);

  const [activeTab, setActiveTab] = useState('designer');
  const [showTemplates, setShowTemplates] = useState(false);

  const canvasRef = useRef<HTMLDivElement>(null);

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      setSelectedNode(null);
    }
  }, [setSelectedNode]);

  const handleAddNodeToCanvas = useCallback((type: keyof typeof NodeTypes) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
      addNode(type, {
        x: Math.random() * (rect.width - 200),
        y: Math.random() * (rect.height - 100)
      });
    }
  }, [addNode]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold flex items-center gap-2">
              <Workflow className="w-6 h-6 text-blue-500" />
              Visual Workflow Designer
            </h1>
            <Badge variant="outline" className="flex items-center gap-1">
              <Users className="w-3 h-3" />
              {collaborators.length + 1} online
            </Badge>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowTemplates(true)}>
              <Plus className="w-4 h-4 mr-1" />
              Templates
            </Button>
            <Button variant="outline" size="sm">
              <Save className="w-4 h-4 mr-1" />
              Save
            </Button>
            <Button
              size="sm"
              onClick={executeWorkflow}
              disabled={isExecuting || nodes.length === 0}
            >
              {isExecuting ? (
                <Timer className="w-4 h-4 mr-1 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-1" />
              )}
              {isExecuting ? 'Running...' : 'Execute'}
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Sidebar */}
        <div className="w-64 bg-white border-r p-4 space-y-6">
          <NodePalette onAddNode={handleAddNodeToCanvas} />
          <CollaborationPanel collaborators={collaborators} isConnected={isConnected} />

          {selectedNode && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold">Properties</h3>
              <div className="space-y-2">
                <Input
                  placeholder="Node label"
                  value={nodes.find(n => n.id === selectedNode)?.data.label || ''}
                  onChange={(e) => {
                    const node = nodes.find(n => n.id === selectedNode);
                    if (node) {
                      updateNode(selectedNode, {
                        data: { ...node.data, label: e.target.value }
                      });
                    }
                  }}
                />
                <Button
                  variant="destructive"
                  size="sm"
                  className="w-full"
                  onClick={() => {
                    deleteNode(selectedNode);
                    setSelectedNode(null);
                  }}
                >
                  Delete Node
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Canvas Area */}
        <div className="flex-1 flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="mx-6 mt-4 w-fit">
              <TabsTrigger value="designer">Designer</TabsTrigger>
              <TabsTrigger value="execution">Execution</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            <TabsContent value="designer" className="flex-1 mt-4">
              <div
                ref={canvasRef}
                className="relative h-full bg-gray-100 mx-6 mb-6 rounded-lg border-2 border-dashed border-gray-300 overflow-hidden"
                onClick={handleCanvasClick}
              >
                {/* Grid Background */}
                <div
                  className="absolute inset-0 opacity-20"
                  style={{
                    backgroundImage: `
                      linear-gradient(to right, #e5e7eb 1px, transparent 1px),
                      linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)
                    `,
                    backgroundSize: '20px 20px'
                  }}
                />

                {/* Nodes */}
                {nodes.map(node => (
                  <NodeComponent
                    key={node.id}
                    node={node}
                    isSelected={selectedNode === node.id}
                    onSelect={() => setSelectedNode(node.id)}
                    onUpdate={(updates) => updateNode(node.id, updates)}
                  />
                ))}

                {/* Collaboration Cursors */}
                {collaborators.map(collaborator => (
                  <div
                    key={collaborator.userId}
                    className="absolute pointer-events-none z-50"
                    style={{
                      left: collaborator.position.x,
                      top: collaborator.position.y,
                      color: collaborator.color
                    }}
                  >
                    <div className="flex items-center gap-1">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: collaborator.color }}
                      />
                      <span className="text-xs bg-white px-1 rounded shadow">
                        {collaborator.userName}
                      </span>
                    </div>
                  </div>
                ))}

                {/* Empty State */}
                {nodes.length === 0 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Workflow className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-600 mb-2">
                        Start Building Your Workflow
                      </h3>
                      <p className="text-gray-500 mb-4">
                        Drag components from the sidebar or choose a template
                      </p>
                      <Button onClick={() => setShowTemplates(true)}>
                        Browse Templates
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="execution" className="flex-1 mt-4 mx-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Workflow Execution</CardTitle>
                </CardHeader>
                <CardContent>
                  {isExecuting ? (
                    <div className="text-center py-8">
                      <Timer className="w-8 h-8 animate-spin mx-auto mb-4" />
                      <p>Executing workflow...</p>
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Play className="w-8 h-8 mx-auto mb-4" />
                      <p>Click Execute to run your workflow</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="flex-1 mt-4 mx-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Execution History</CardTitle>
                </CardHeader>
                <CardContent>
                  {executionHistory.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Eye className="w-8 h-8 mx-auto mb-4" />
                      <p>No executions yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {executionHistory.map((execution, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium">
                              Execution #{executionHistory.length - index}
                            </span>
                            <Badge variant={execution.success ? 'default' : 'destructive'}>
                              {execution.success ? 'Success' : 'Failed'}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-600">
                            {new Date(execution.timestamp).toLocaleString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Template Modal */}
      {showTemplates && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Workflow Templates</h2>
              <Button variant="outline" onClick={() => setShowTemplates(false)}>
                Close
              </Button>
            </div>
            <TemplateLibrary
              onSelectTemplate={(template) => {
                loadTemplate(template);
                setShowTemplates(false);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedRetoolWorkflowDesigner;
