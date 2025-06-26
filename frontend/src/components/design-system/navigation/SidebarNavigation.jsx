import React, { useState } from 'react';
import { 
  Crown, 
  Brain, 
  Kanban, 
  BarChart3, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  User,
  Zap,
  Database,
  Bell,
  Shield
} from 'lucide-react';
import { cn } from '@/lib/utils';

const NAVIGATION_ITEMS = [
  { 
    id: 'executive', 
    label: 'Executive', 
    icon: Crown, 
    badge: 'Live',
    description: 'CEO Dashboard & Analytics'
  },
  { 
    id: 'knowledge', 
    label: 'Knowledge', 
    icon: Brain, 
    badge: null,
    description: 'Knowledge Base & Search'
  },
  { 
    id: 'projects', 
    label: 'Projects', 
    icon: Kanban, 
    badge: null,
    description: 'Project Management'
  },
  { 
    id: 'analytics', 
    label: 'Analytics', 
    icon: BarChart3, 
    badge: null,
    description: 'Business Intelligence'
  },
  { 
    id: 'ai-insights', 
    label: 'AI Insights', 
    icon: Zap, 
    badge: 'New',
    description: 'AI-Powered Analysis'
  },
  { 
    id: 'integrations', 
    label: 'Integrations', 
    icon: Database, 
    badge: null,
    description: 'Data Sources & APIs'
  },
];

const SidebarNavigation = ({ 
  activeTab, 
  onTabChange, 
  collapsed = false, 
  onToggleCollapse,
  className = "" 
}) => {
  const [hoveredItem, setHoveredItem] = useState(null);

  const NavigationItem = ({ item, isActive, isCollapsed }) => {
    const Icon = item.icon;
    
    return (
      <button
        onClick={() => onTabChange(item.id)}
        onMouseEnter={() => setHoveredItem(item.id)}
        onMouseLeave={() => setHoveredItem(null)}
        className={cn(
          // Base styles with Pay Ready branding
          "w-full flex items-center gap-3 px-3 py-2.5 mx-2 rounded-lg",
          "transition-all duration-200 text-left min-h-[44px]",
          "focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900",
          
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
              {hoveredItem === item.id && item.description && (
                <div className="text-xs text-gray-400 truncate mt-0.5">
                  {item.description}
                </div>
              )}
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
        collapsed ? "w-16" : "w-72",
        
        className
      )}
      aria-label="Main navigation"
    >
      {/* Header */}
      <div className={cn(
        "flex items-center border-b border-slate-700/50 p-4",
        collapsed ? "justify-center" : "justify-between"
      )}>
        {!collapsed && (
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
        
        {onToggleCollapse && (
          <button
            onClick={onToggleCollapse}
            className={cn(
              "p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-slate-700/50",
              "transition-colors duration-200",
              "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900",
              collapsed && "mx-auto"
            )}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 py-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent">
        <div className="space-y-1">
          {NAVIGATION_ITEMS.map((item) => (
            <NavigationItem
              key={item.id}
              item={item}
              isActive={activeTab === item.id}
              isCollapsed={collapsed}
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
            isCollapsed={collapsed}
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
            isCollapsed={collapsed}
          />
        </div>
      </nav>

      {/* Footer */}
      <div className={cn(
        "border-t border-slate-700/50 p-4",
        collapsed ? "px-2" : "px-4"
      )}>
        {/* User Profile */}
        <div className={cn(
          "flex items-center gap-3 p-2 rounded-lg",
          "hover:bg-slate-700/50 transition-colors duration-200 cursor-pointer",
          collapsed && "justify-center"
        )}>
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          {!collapsed && (
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
        {!collapsed && (
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

export default SidebarNavigation; 