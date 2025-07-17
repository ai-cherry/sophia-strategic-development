/**
 * 🗄️ DASHBOARD STORE
 * Global state management using Zustand for the Sophia Executive Dashboard
 * 
 * Created as part of Phase 1 Frontend Refactoring
 * - Centralizes dashboard state management
 * - Replaces local state in SophiaExecutiveDashboard
 * - Provides type-safe state operations
 * - Enables state persistence and sharing
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { DashboardStore, ProactiveAlert } from '../types/dashboard';

export const useDashboardStore = create<DashboardStore>()(
  subscribeWithSelector((set, get) => ({
    // State
    activeTab: 'chat',
    sidebarCollapsed: false,
    searchQuery: '',
    searchResults: [],
    isSearching: false,
    temporalLearningEnabled: true,
    personalityMode: 'professional',
    websocket: null,
    proactiveAlerts: [],

    // Actions
    setActiveTab: (tab: string) => set({ activeTab: tab }),
    
    setSidebarCollapsed: (collapsed: boolean) => set({ sidebarCollapsed: collapsed }),
    
    setSearchQuery: (query: string) => set({ searchQuery: query }),
    
    setSearchResults: (results: any[]) => set({ searchResults: results }),
    
    setIsSearching: (searching: boolean) => set({ isSearching: searching }),
    
    setTemporalLearningEnabled: (enabled: boolean) => set({ temporalLearningEnabled: enabled }),
    
    setPersonalityMode: (mode: string) => set({ personalityMode: mode }),
    
    setWebsocket: (ws: WebSocket | null) => set({ websocket: ws }),
    
    addProactiveAlert: (alert: ProactiveAlert) => set((state) => ({
      proactiveAlerts: [...state.proactiveAlerts, alert]
    })),
    
    removeProactiveAlert: (alertId: string) => set((state) => ({
      proactiveAlerts: state.proactiveAlerts.filter(alert => alert.id !== alertId)
    })),

    // Computed getters
    getActiveTabConfig: () => {
      const INTELLIGENCE_TABS = {
        'chat': { icon: 'MessageSquare', label: 'Executive Chat', color: 'blue' },
        'external': { icon: 'Globe', label: 'External Intelligence', color: 'green' },
        'business': { icon: 'BarChart3', label: 'Business Intelligence', color: 'purple' },
        'agents': { icon: 'Bot', label: 'Agent Orchestration', color: 'orange' },
        'memory': { icon: 'Database', label: 'Memory Architecture', color: 'cyan' },
        'learning': { icon: 'Brain', label: 'Temporal Learning', color: 'pink' },
        'workflow': { icon: 'Zap', label: 'Workflow Automation', color: 'yellow' },
        'system': { icon: 'Settings', label: 'System Command', color: 'gray' },
        'project': { icon: 'Briefcase', label: 'Project Management', color: 'teal' }
      };
      
      const { activeTab } = get();
      return INTELLIGENCE_TABS[activeTab as keyof typeof INTELLIGENCE_TABS];
    },

    // Utility functions
    clearSearch: () => set({ searchQuery: '', searchResults: [], isSearching: false }),
    
    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    
    // WebSocket helpers
    connectWebSocket: (url: string) => {
      const { websocket } = get();
      
      // Close existing connection if any
      if (websocket) {
        websocket.close();
      }
      
      try {
        const ws = new WebSocket(url);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected to Sophia AI backend');
          set({ websocket: ws });
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            // Handle different message types
            if (data.type === 'proactive_alert') {
              get().addProactiveAlert(data.alert);
            } else if (data.type === 'search_result') {
              set({ searchResults: data.results, isSearching: false });
            }
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
          }
        };
        
        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
        };
        
        ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          set({ websocket: null });
        };
        
      } catch (error) {
        console.error('❌ Failed to create WebSocket connection:', error);
      }
    },
    
    disconnectWebSocket: () => {
      const { websocket } = get();
      if (websocket) {
        websocket.close();
        set({ websocket: null });
      }
    },

    // Search functionality
    performSearch: async (query: string) => {
      set({ isSearching: true, searchQuery: query });
      
      try {
        // This would be replaced with actual API call
        const response = await fetch(`/api/v3/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        set({ searchResults: results, isSearching: false });
      } catch (error) {
        console.error('❌ Search error:', error);
        set({ isSearching: false, searchResults: [] });
      }
    },

    // Alert management
    clearAllAlerts: () => set({ proactiveAlerts: [] }),
    
    getAlertsByType: (type: ProactiveAlert['type']) => {
      const { proactiveAlerts } = get();
      return proactiveAlerts.filter(alert => alert.type === type);
    },
    
    getAlertsByUrgency: (urgency: ProactiveAlert['urgency']) => {
      const { proactiveAlerts } = get();
      return proactiveAlerts.filter(alert => alert.urgency === urgency);
    },

    // Tab management utilities
    isTabActive: (tabId: string) => get().activeTab === tabId,
    
    getTabHistory: () => {
      // This could be implemented with additional state to track tab history
      return [];
    },

    // Reset functionality
    resetDashboard: () => set({
      activeTab: 'chat',
      sidebarCollapsed: false,
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      proactiveAlerts: []
    })
  }))
);

// Subscribe to tab changes for analytics/logging
useDashboardStore.subscribe(
  (state) => state.activeTab,
  (activeTab, previousActiveTab) => {
    if (activeTab !== previousActiveTab) {
      console.log(`📊 Tab changed from ${previousActiveTab} to ${activeTab}`);
      // Here you could send analytics events
    }
  }
);

// Subscribe to alert changes
useDashboardStore.subscribe(
  (state) => state.proactiveAlerts,
  (alerts) => {
    const criticalAlerts = alerts.filter(alert => alert.urgency === 'critical');
    if (criticalAlerts.length > 0) {
      console.warn(`🚨 ${criticalAlerts.length} critical alerts active`);
      // Here you could trigger notifications
    }
  }
);

export default useDashboardStore; 