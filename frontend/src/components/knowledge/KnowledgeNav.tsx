import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  FileText,
  Search,
  BarChart3,
  Settings,
  Lightbulb,
  MessageSquare,
  ArrowLeft
} from 'lucide-react';

export const KnowledgeNav: React.FC = () => {
  const location = useLocation();

  const navItems = [
    { path: '/knowledge', label: 'Documents', icon: FileText },
    { path: '/knowledge/discovery', label: 'Discovery Queue', icon: Lightbulb },
    { path: '/knowledge/curation', label: 'Curation Chat', icon: MessageSquare },
    { path: '/knowledge/search', label: 'Search', icon: Search },
    { path: '/knowledge/analytics', label: 'Analytics', icon: BarChart3 },
    { path: '/knowledge/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Link>
            <h1 className="text-xl font-semibold">Knowledge Base</h1>
          </div>

          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path ||
                             (item.path !== '/knowledge' && location.pathname.startsWith(item.path));

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};
