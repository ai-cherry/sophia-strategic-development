/**
 * 🔄 WORKFLOW AUTOMATION PANEL
 * Extracted from SophiaExecutiveDashboard.tsx as part of Phase 1 Frontend Refactoring
 * 
 * Features:
 * - Real-time workflow status monitoring
 * - n8n automation management
 * - Performance metrics and analytics
 * - Quick action controls
 * - Activity feed
 * 
 * Business Context:
 * - Monitors Pay Ready's business process automation
 * - Tracks time savings and efficiency gains
 * - Manages integrations (Gong → HubSpot, Slack notifications, etc.)
 */

import React from 'react';
import { 
  Zap, 
  Activity, 
  Clock, 
  CheckCircle, 
  BarChart3
} from 'lucide-react';
import { 
  WorkflowAutomationProps, 
  WorkflowStatus, 
  WorkflowMetrics, 
  WorkflowActivity 
} from '../../types/dashboard';

const WorkflowAutomationPanel: React.FC<WorkflowAutomationProps> = ({
  workflows = [],
  metrics = {
    activeWorkflows: 12,
    executionsToday: 247,
    timeSavedHours: 18.5,
    successRate: 98.2
  },
  activities = [],
  onCreateWorkflow = () => {},
  onViewDashboard = () => {},
  onViewAnalytics = () => {},
  className = ""
}) => {
  // Default mock data for workflows if not provided
  const defaultWorkflows: WorkflowStatus[] = [
    { name: 'Gong Call → HubSpot Lead Scoring', status: 'active', executions: 34, lastRun: '2 minutes ago' },
    { name: 'HubSpot Deal → Slack Notifications', status: 'active', executions: 18, lastRun: '5 minutes ago' },
    { name: 'Customer Health Score Updates', status: 'active', executions: 12, lastRun: '15 minutes ago' },
    { name: 'Weekly Revenue Report Generation', status: 'scheduled', executions: 1, lastRun: 'Yesterday' },
    { name: 'Competitor Price Monitoring', status: 'active', executions: 8, lastRun: '1 hour ago' }
  ];

  // Default mock data for activities if not provided
  const defaultActivities: WorkflowActivity[] = [
    { action: 'Lead scored in HubSpot', time: '2 min ago', status: 'success' },
    { action: 'Slack notification sent', time: '5 min ago', status: 'success' },
    { action: 'Revenue report generated', time: '1 hour ago', status: 'success' },
    { action: 'Customer health updated', time: '2 hours ago', status: 'success' },
    { action: 'Competitor data fetched', time: '3 hours ago', status: 'warning' }
  ];

  const displayWorkflows = workflows.length > 0 ? workflows : defaultWorkflows;
  const displayActivities = activities.length > 0 ? activities : defaultActivities;

  return (
    <div className={`p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-white mb-4">Workflow Automation</h2>
      
      {/* Workflow Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Active Workflows</h3>
            <Zap className="h-5 w-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.activeWorkflows}</div>
          <div className="text-xs text-gray-400">n8n automations</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Executions Today</h3>
            <Activity className="h-5 w-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.executionsToday}</div>
          <div className="text-xs text-gray-400">Successful runs</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Time Saved</h3>
            <Clock className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.timeSavedHours}h</div>
          <div className="text-xs text-gray-400">This week</div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-white">Success Rate</h3>
            <CheckCircle className="h-5 w-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.successRate}%</div>
          <div className="text-xs text-gray-400">Last 30 days</div>
        </div>
      </div>

      {/* Active Workflows */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
        <h3 className="text-lg font-semibold text-white mb-4">Active Automation Workflows</h3>
        <div className="space-y-3">
          {displayWorkflows.map((workflow, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded">
              <div className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  workflow.status === 'active' ? 'bg-green-400' : 
                  workflow.status === 'scheduled' ? 'bg-yellow-400' : 'bg-red-400'
                }`} />
                <span className="text-white font-medium">{workflow.name}</span>
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <span>{workflow.executions} runs today</span>
                <span>{workflow.lastRun}</span>
                <button className="text-blue-400 hover:text-blue-300 transition-colors">
                  Configure
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workflow Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button 
              onClick={onCreateWorkflow}
              className="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded text-white transition-colors flex items-center justify-center space-x-2"
            >
              <Zap className="h-4 w-4" />
              <span>Create New Workflow</span>
            </button>
            <button 
              onClick={onViewDashboard}
              className="w-full p-3 bg-green-600 hover:bg-green-700 rounded text-white transition-colors flex items-center justify-center space-x-2"
            >
              <Activity className="h-4 w-4" />
              <span>View n8n Dashboard</span>
            </button>
            <button 
              onClick={onViewAnalytics}
              className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded text-white transition-colors flex items-center justify-center space-x-2"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Automation Analytics</span>
            </button>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {displayActivities.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-700 rounded text-sm">
                <span className="text-white">{activity.action}</span>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-400">{activity.time}</span>
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-400' : 
                    activity.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowAutomationPanel; 