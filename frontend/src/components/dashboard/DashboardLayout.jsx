import React, { useState } from 'react';
import {
  DollarSign,
  Users,
  TrendingUp,
  Activity,
  BarChart3,
  Building2,
  Brain,
  Zap,
  Crown,
  Kanban,
  Database,
  Bell,
  Shield,
  Settings,
  ChevronLeft,
  ChevronRight,
  User,
  Menu,
  X
} from 'lucide-react';
import Header from '../design-system/navigation/Header';
import MetricCard from '../design-system/cards/MetricCard';
import GlassCard from '../design-system/cards/GlassCard';
import Button from '../design-system/buttons/Button';
import { cn } from '@/lib/utils';
import api from '../../services/api';
import useCompanyMetrics from '../../hooks/use-company-metrics';
import NaturalLanguageInterface from '../NaturalLanguageInterface';
import ContextualSidebar from './ContextualSidebar';

// Enhanced Navigation Items with Pay Ready Branding
const NAVIGATION_ITEMS = [
  { 
    id: 'overview', 
    label: 'Executive', 
    icon: Crown, 
    badge: 'Live',
    description: 'CEO Dashboard & Analytics'
  },
  { 
    id: 'strategy', 
    label: 'Knowledge', 
    icon: Brain, 
    badge: null,
    description: 'Knowledge Base & Search'
  },
  { 
    id: 'operations', 
    label: 'Projects', 
    icon: Kanban, 
    badge: null,
    description: 'Project Management'
  },
  { 
    id: 'insights', 
    label: 'Analytics', 
    icon: BarChart3, 
    badge: null,
    description: 'Business Intelligence'
  },
];

const DashboardLayout = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [contextualSidebarCollapsed, setContextualSidebarCollapsed] = useState(false);
  const { data: metrics, loading, error } = useCompanyMetrics();

  // Sidebar Navigation Component
  const SidebarNavigation = () => {
    const NavigationItem = ({ item, isActive, isCollapsed }) => {
      const Icon = item.icon;
      
      return (
        <button
          onClick={() => {
            setActiveTab(item.id);
            setMobileMenuOpen(false); // Close mobile menu on selection
          }}
          className={cn(
            // Base styles with Pay Ready branding
            "w-full flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg",
            "transition-all duration-200 text-left min-h-[44px]",
            "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900",
            
            // Active state with brand colors
            isActive 
              ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-600/25" 
              : "text-gray-300 hover:text-white hover:bg-slate-700/50",
            
            // Focus ring with brand color
            "focus:ring-blue-500",
            
            // Collapsed state
            isCollapsed && "justify-center px-2"
          )}
          aria-label={isCollapsed ? item.label : undefined}
          title={isCollapsed ? item.description : undefined}
        >
          <Icon 
            className={cn(
              "w-5 h-5 flex-shrink-0",
              isActive ? "text-white" : "text-gray-400"
            )} 
          />
          
          {!isCollapsed && (
            <>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">
                  {item.label}
                </div>
                <div className="text-xs text-gray-400 truncate mt-0.5">
                  {item.description}
                </div>
              </div>
              
              {item.badge && (
                <span className={cn(
                  "px-2 py-0.5 text-xs font-semibold rounded-full",
                  item.badge === 'Live' 
                    ? "bg-green-500 text-white animate-pulse"
                    : item.badge === 'New'
                    ? "bg-blue-500 text-white"
                    : "bg-gray-600 text-gray-300"
                )}>
                  {item.badge}
                </span>
              )}
            </>
          )}
        </button>
      );
    };

    return (
      <aside 
        className={cn(
          // Base sidebar styles with glass effect
          "flex flex-col h-full border-r border-slate-700/50 transition-all duration-300",
          "bg-slate-900/80 backdrop-blur-md",
          
          // Width management
          sidebarCollapsed ? "w-16" : "w-72",
          
          // Mobile responsive
          "lg:relative lg:translate-x-0",
          "fixed inset-y-0 left-0 z-50 transform",
          mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
        aria-label="Main navigation"
      >
        {/* Header */}
        <div className={cn(
          "flex items-center border-b border-slate-700/50 p-4",
          sidebarCollapsed ? "justify-center" : "justify-between"
        )}>
          {!sidebarCollapsed && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Crown className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-semibold text-white text-sm">Sophia AI</h1>
                <p className="text-xs text-gray-400">Pay Ready Platform</p>
              </div>
            </div>
          )}
          
          {/* Desktop collapse toggle */}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className={cn(
              "hidden lg:flex p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-slate-700/50",
              "transition-colors duration-200",
              "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900",
              sidebarCollapsed && "mx-auto"
            )}
            aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {sidebarCollapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>

          {/* Mobile close button */}
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="lg:hidden p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-slate-700/50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent">
          <div className="space-y-1">
            {NAVIGATION_ITEMS.map((item) => (
              <NavigationItem
                key={item.id}
                item={item}
                isActive={activeTab === item.id}
                isCollapsed={sidebarCollapsed}
              />
            ))}
          </div>
          
          {/* Divider */}
          <div className="my-4 mx-4 border-t border-slate-700/50" />
          
          {/* Additional Actions */}
          <div className="space-y-1">
            <NavigationItem
              item={{
                id: 'notifications',
                label: 'Notifications',
                icon: Bell,
                badge: '3',
                description: 'System Alerts & Updates'
              }}
              isActive={activeTab === 'notifications'}
              isCollapsed={sidebarCollapsed}
            />
            <NavigationItem
              item={{
                id: 'security',
                label: 'Security',
                icon: Shield,
                badge: null,
                description: 'Access Control & Audit'
              }}
              isActive={activeTab === 'security'}
              isCollapsed={sidebarCollapsed}
            />
          </div>
        </nav>

        {/* Footer */}
        <div className={cn(
          "border-t border-slate-700/50 p-4",
          sidebarCollapsed ? "px-2" : "px-4"
        )}>
          {/* User Profile */}
          <div className={cn(
            "flex items-center gap-3 p-2 rounded-lg",
            "hover:bg-slate-700/50 transition-colors duration-200 cursor-pointer",
            sidebarCollapsed && "justify-center"
          )}>
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            {!sidebarCollapsed && (
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">
                  CEO User
                </div>
                <div className="text-xs text-gray-400 truncate">
                  Administrator
                </div>
              </div>
            )}
          </div>
          
          {/* Settings */}
          {!sidebarCollapsed && (
            <button
              className={cn(
                "w-full flex items-center gap-3 px-2 py-2 mt-2 rounded-lg",
                "text-gray-400 hover:text-white hover:bg-slate-700/50",
                "transition-colors duration-200 text-left",
                "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900"
              )}
            >
              <Settings className="w-4 h-4" />
              <span className="text-sm">Settings</span>
            </button>
          )}
        </div>
      </aside>
    );
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab metrics={metrics} loading={loading} />;
      case 'strategy':
        return <StrategyTab />;
      case 'operations':
        return <OperationsTab />;
      case 'insights':
        return <InsightsTab />;
      case 'notifications':
        return <NotificationsTab />;
      case 'security':
        return <SecurityTab />;
      default:
        return <OverviewTab metrics={metrics} loading={loading} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar Navigation */}
      <SidebarNavigation />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Enhanced Header */}
        <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-700/50 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Mobile menu toggle */}
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-slate-700/50"
              >
                <Menu className="w-5 h-5" />
              </button>

              {/* Breadcrumb Navigation */}
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <span>Dashboard</span>
                <span>/</span>
                <span className="text-white font-medium">
                  {NAVIGATION_ITEMS.find(item => item.id === activeTab)?.label || 'Executive'}
                </span>
              </div>
            </div>

            {/* Connection Status & Actions */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-gray-300">Connected</span>
              </div>
              <Button variant="ghost" size="sm">
                <Bell className="w-4 h-4" />
              </Button>
              {/* Contextual sidebar toggle for mobile */}
              <button
                onClick={() => setContextualSidebarCollapsed(!contextualSidebarCollapsed)}
                className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-slate-700/50"
              >
                <Activity className="w-4 h-4" />
              </button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            {error && (
              <div className="mb-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200">
                Failed to load metrics: {error.message}
              </div>
            )}

            {/* Enhanced KPI Cards for Executive Dashboard */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <ExecutiveKPICard
                  title="Monthly Revenue"
                  value={metrics?.revenue?.value || '—'}
                  change={metrics?.revenue?.change}
                  trend={metrics?.revenue?.trend}
                  icon={DollarSign}
                  loading={loading}
                />
                <ExecutiveKPICard
                  title="Active Customers"
                  value={metrics?.customers?.value || '—'}
                  change={metrics?.customers?.change}
                  trend={metrics?.customers?.trend}
                  icon={Users}
                  loading={loading}
                />
                <ExecutiveKPICard
                  title="Pipeline Value"
                  value={metrics?.pipeline?.value || '—'}
                  change={metrics?.pipeline?.change}
                  trend={metrics?.pipeline?.trend}
                  icon={TrendingUp}
                  loading={loading}
                />
                <ExecutiveKPICard
                  title="Health Score"
                  value={metrics?.healthScore?.value || '—'}
                  change={metrics?.healthScore?.change}
                  trend={metrics?.healthScore?.trend}
                  icon={Activity}
                  loading={loading}
                />
              </div>
            )}

            {/* Tab Content */}
            {renderTabContent()}
          </div>
        </main>
      </div>

      {/* Contextual Sidebar */}
      {!contextualSidebarCollapsed && (
        <ContextualSidebar 
          activeView={activeTab}
          onViewChange={setActiveTab}
          userId="ceo"
          className="hidden lg:flex"
        />
      )}
    </div>
  );
};

// Enhanced Executive KPI Card Component
const ExecutiveKPICard = ({ title, value, change, trend, icon: Icon, loading, onClick }) => {
  const trendColor = trend === 'up' ? 'text-green-400' : 
                    trend === 'down' ? 'text-red-400' : 'text-gray-400';
  
  return (
    <div 
      className={cn(
        "p-6 rounded-xl border border-slate-700/50 cursor-pointer transition-all duration-200",
        "bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm",
        "hover:scale-102 hover:shadow-xl hover:border-blue-500/50",
        "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900"
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`${title}: ${value}, ${change}`}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-400">{title}</h3>
        <Icon className="h-5 w-5 text-blue-400" aria-hidden="true" />
      </div>
      
      {loading ? (
        <div className="animate-pulse">
          <div className="h-8 bg-slate-700 rounded mb-2"></div>
          <div className="h-4 bg-slate-700 rounded w-1/2"></div>
        </div>
      ) : (
        <>
          <div className="text-2xl font-bold text-white mb-2">
            {value}
          </div>
          {change && (
            <div className="flex items-center">
              <TrendingUp 
                className={cn("h-3 w-3 mr-1", trendColor)}
                aria-hidden="true"
              />
              <span className={cn("text-sm", trendColor)}>
                {change}
              </span>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Enhanced Tab Components with better styling
const OverviewTab = ({ metrics, loading }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <GlassCard>
          <h2 className="text-h3 font-semibold mb-6">Revenue Trend</h2>
          <div className="h-64 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg flex items-center justify-center">
            <p className="text-gray-400">Revenue chart visualization</p>
          </div>
        </GlassCard>
      </div>

      <div className="space-y-6">
        <GlassCard>
          <h3 className="text-h4 font-medium mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Button variant="primary" className="w-full" icon={BarChart3}>
              Generate Report
            </Button>
            <Button variant="secondary" className="w-full" icon={Building2}>
              Property Analysis
            </Button>
          </div>
        </GlassCard>

        <GlassCard>
          <h3 className="text-h4 font-medium mb-4">AI Insights</h3>
          <div className="space-y-3">
            <div className="p-3 bg-purple-900/20 border border-purple-700 rounded-lg">
              <p className="text-sm text-purple-300">
                Revenue growth is 23% above market average
              </p>
            </div>
            <div className="p-3 bg-blue-900/20 border border-blue-700 rounded-lg">
              <p className="text-sm text-blue-300">
                Customer retention improved by 15% this quarter
              </p>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};

// Additional Tab Components (keeping existing functionality)
const StrategyTab = () => {
  return (
    <GlassCard gradient>
      <h2 className="text-h2 font-semibold mb-6">Strategic Planning</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Growth Opportunities</h3>
          <div className="space-y-3">
            {['Market Expansion', 'Product Development', 'Customer Acquisition'].map((item) => (
              <div key={item} className="p-4 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors cursor-pointer">
                <p className="font-medium text-white">{item}</p>
                <p className="text-sm text-gray-400 mt-1">Click to view detailed analysis</p>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Risk Assessment</h3>
          <div className="p-4 bg-slate-800 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">Overall Risk Score</span>
              <span className="text-2xl font-bold text-green-400">Low</span>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Market Risk</span>
                <span className="text-green-400">Low</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Operational Risk</span>
                <span className="text-yellow-400">Medium</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Financial Risk</span>
                <span className="text-green-400">Low</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};

const OperationsTab = () => {
  return (
    <div className="space-y-6">
      <GlassCard>
        <h2 className="text-h2 font-semibold mb-6">Operational Efficiency</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">87%</div>
            <p className="text-sm text-gray-400">Process Automation</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">2.3h</div>
            <p className="text-sm text-gray-400">Avg Response Time</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">99.9%</div>
            <p className="text-sm text-gray-400">System Uptime</p>
          </div>
        </div>
      </GlassCard>

      <GlassCard>
        <h3 className="text-h3 font-semibold mb-4">Active Workflows</h3>
        <div className="space-y-3">
          {['Customer Onboarding', 'Property Assessment', 'Financial Analysis'].map((workflow) => (
            <div key={workflow} className="flex items-center justify-between p-4 bg-slate-800 rounded-lg">
              <span className="font-medium">{workflow}</span>
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-400">Running</span>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
};

const InsightsTab = () => {
  return (
    <GlassCard>
      <h2 className="text-h2 font-semibold mb-6">AI-Powered Insights</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Predictive Analytics</h3>
          <div className="p-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-700 rounded-lg">
            <h4 className="font-medium text-purple-300 mb-2">Revenue Forecast</h4>
            <p className="text-2xl font-bold text-white mb-1">$425,000</p>
            <p className="text-sm text-gray-400">Projected for next month with 85% confidence</p>
          </div>
        </div>
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Recommendations</h3>
          <div className="space-y-3">
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-sm">
                <span className="text-yellow-400 font-medium">Action Required:</span>
                <span className="text-gray-300 ml-2">Contact high-value customers showing churn signals</span>
              </p>
            </div>
            <div className="p-3 bg-slate-800 rounded-lg">
              <p className="text-sm">
                <span className="text-green-400 font-medium">Opportunity:</span>
                <span className="text-gray-300 ml-2">Upsell potential identified for 23 accounts</span>
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-6">
        <h3 className="text-h4 font-medium mb-2">Try a command</h3>
        <NaturalLanguageInterface />
      </div>
    </GlassCard>
  );
};

// New Tab Components
const NotificationsTab = () => {
  return (
    <GlassCard>
      <h2 className="text-h2 font-semibold mb-6">System Notifications</h2>
      <div className="space-y-4">
        <div className="p-4 bg-blue-900/20 border border-blue-700 rounded-lg">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-blue-300">Revenue Alert</h4>
              <p className="text-sm text-gray-300 mt-1">Monthly revenue target achieved 5 days early</p>
            </div>
            <span className="text-xs text-gray-400">2 mins ago</span>
          </div>
        </div>
        <div className="p-4 bg-yellow-900/20 border border-yellow-700 rounded-lg">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-medium text-yellow-300">System Update</h4>
              <p className="text-sm text-gray-300 mt-1">Scheduled maintenance tonight 2:00 AM - 4:00 AM EST</p>
            </div>
            <span className="text-xs text-gray-400">1 hour ago</span>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};

const SecurityTab = () => {
  return (
    <GlassCard>
      <h2 className="text-h2 font-semibold mb-6">Security & Access Control</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Access Logs</h3>
          <div className="space-y-3">
            <div className="p-3 bg-slate-800 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm font-medium text-white">CEO Dashboard Access</p>
                  <p className="text-xs text-gray-400">IP: 192.168.1.100</p>
                </div>
                <span className="text-xs text-green-400">Success</span>
              </div>
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <h3 className="text-h4 font-medium">Security Status</h3>
          <div className="p-4 bg-green-900/20 border border-green-700 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-300">Overall Security Score</span>
              <span className="text-xl font-bold text-green-400">Excellent</span>
            </div>
            <div className="text-xs text-gray-400">All security checks passed</div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
};

export default DashboardLayout;
