import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  Users, 
  DollarSign,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Sparkles,
  MessageSquare,
  BarChart3,
  Zap,
  Target,
  ChevronLeft
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { SophiaUniversalChatInterface } from '../shared/SophiaUniversalChatInterface';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { SophiaLiveChatInterface } from '../shared/SophiaLiveChatInterface';

const ContextualSidebar = ({ 
  activeView, 
  onViewChange, 
  className = '',
  userId = 'ceo' 
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');

  // Define sidebar tabs with icons
  const sidebarTabs = [
    { 
      id: 'chat', 
      label: 'AI Assistant', 
      icon: MessageSquare,
      description: 'Chat with Sophia AI'
    },
    { 
      id: 'insights', 
      label: 'AI Insights', 
      icon: BarChart3,
      description: 'AI-generated insights'
    },
    { 
      id: 'documents', 
      label: 'Knowledge Base', 
      icon: FileText,
      description: 'Company documents'
    },
    { 
      id: 'team', 
      label: 'Team Activity', 
      icon: Users,
      description: 'Team collaboration'
    }
  ];

  // Mock data for other tabs (replace with real data from API)
  const mockInsights = [
    {
      id: 1,
      title: "Sales Performance",
      description: "Q4 sales are 15% above target",
      priority: "high",
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      title: "Customer Engagement",
      description: "Customer satisfaction up 8% this month",
      priority: "medium", 
      timestamp: new Date().toISOString()
    }
  ];

  const mockDocuments = [
    { id: 1, name: "Q4 Business Plan.pdf", uploadedAt: "2024-01-15", size: "2.3 MB" },
    { id: 2, name: "Customer Analysis.docx", uploadedAt: "2024-01-14", size: "1.8 MB" },
    { id: 3, name: "Market Research.pdf", uploadedAt: "2024-01-13", size: "4.1 MB" }
  ];

  const mockTeamActivity = [
    { id: 1, user: "Alice Johnson", action: "Updated sales forecast", time: "2 hours ago" },
    { id: 2, user: "Bob Smith", action: "Completed project review", time: "4 hours ago" },
    { id: 3, user: "Carol Davis", action: "Added new client notes", time: "6 hours ago" }
  ];

  // Render tab content
  const renderTabContent = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <SophiaLiveChatInterface
            userId={userId}
            dashboardType={activeView}
            className="border-0 bg-transparent"
            height="h-full"
            showFileUpload={true}
          />
        );

      case 'insights':
        return (
          <div className="space-y-4">
            <div className="text-sm text-text-secondary mb-4">
              AI-generated insights based on your data
            </div>
            {mockInsights.map((insight) => (
              <Card key={insight.id} className="border-border-interactive">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-text-primary text-sm">
                      {insight.title}
                    </h4>
                    <Badge 
                      variant={insight.priority === 'high' ? 'destructive' : 'secondary'}
                      className="text-xs"
                    >
                      {insight.priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-text-secondary">
                    {insight.description}
                  </p>
                  <div className="text-xs text-text-tertiary mt-2">
                    {new Date(insight.timestamp).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      case 'documents':
        return (
          <div className="space-y-4">
            <div className="text-sm text-text-secondary mb-4">
              Recently uploaded documents
            </div>
            {mockDocuments.map((doc) => (
              <Card key={doc.id} className="border-border-interactive hover:bg-surface-elevated cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-4 h-4 text-pr-primary-blue" />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-text-primary text-sm truncate">
                        {doc.name}
                      </h4>
                      <div className="flex items-center justify-between text-xs text-text-tertiary">
                        <span>{doc.uploadedAt}</span>
                        <span>{doc.size}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      case 'team':
        return (
          <div className="space-y-4">
            <div className="text-sm text-text-secondary mb-4">
              Recent team activity
            </div>
            {mockTeamActivity.map((activity) => (
              <Card key={activity.id} className="border-border-interactive">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-pr-primary-blue text-white flex items-center justify-center text-xs font-medium">
                      {activity.user.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-text-primary text-sm">
                        {activity.user}
                      </h4>
                      <p className="text-xs text-text-secondary">
                        {activity.action}
                      </p>
                      <div className="text-xs text-text-tertiary mt-1">
                        {activity.time}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        );

      default:
        return null;
    }
  };

  if (isCollapsed) {
    return (
      <div className={`bg-surface transition-all duration-300 border-l border-border-interactive ${className} w-16 flex flex-col`}>
        <div className="p-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(false)}
            className="w-full p-2"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex-1 flex flex-col space-y-2 px-2">
          {sidebarTabs.map((tab) => {
            const TabIcon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant={activeTab === tab.id ? "default" : "ghost"}
                size="sm"
                onClick={() => {
                  setActiveTab(tab.id);
                  setIsCollapsed(false);
                }}
                className="w-full p-2 justify-center"
                title={tab.label}
              >
                <TabIcon className="w-4 h-4" />
              </Button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-surface transition-all duration-300 border-l border-border-interactive ${className} w-96 flex flex-col`}>
      {/* Header */}
      <div className="border-b border-border-interactive p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary">
            Contextual Assistant
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(true)}
            className="p-2"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        {/* Tab Navigation */}
        <div className="grid grid-cols-2 gap-2">
          {sidebarTabs.map((tab) => {
            const TabIcon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant={activeTab === tab.id ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTab(tab.id)}
                className="justify-start p-2 h-auto"
              >
                <TabIcon className="w-4 h-4 mr-2" />
                <div className="text-left">
                  <div className="text-xs font-medium">{tab.label}</div>
                  <div className="text-xs opacity-70">{tab.description}</div>
                </div>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'chat' ? (
          // Chat takes full height
          renderTabContent()
        ) : (
          // Other tabs have padding and scroll
          <div className="h-full overflow-y-auto p-4">
            {renderTabContent()}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContextualSidebar; 