/**
 * Sophia AI CEO Dashboard - Retool Template
 * 
 * This template creates a fully functional CEO dashboard with:
 * - Strategic Intelligence Chat
 * - Real-time System Monitoring
 * - Executive KPIs and Analytics
 * 
 * To use:
 * 1. Create a new Retool app
 * 2. Copy this entire code into the app's code editor
 * 3. Configure the SophiaAPI resource with your backend URL and admin key
 */

// Dashboard Configuration
const dashboardConfig = {
  tabs: [
    {
      name: "Strategic Intelligence",
      icon: "fas fa-brain",
      components: ["strategicChat", "executiveKPIs", "clientHealth", "marketIntel"]
    },
    {
      name: "AI System Status",
      icon: "fas fa-robot",
      components: ["agentStatus", "taskQueue", "memoryAnalytics", "performance"]
    },
    {
      name: "Infrastructure Monitor",
      icon: "fas fa-server",
      components: ["systemHealth", "apiCatalog", "integrationStatus", "alerts"]
    }
  ]
};

// Component Templates
const components = {
  // Strategic Chat Component
  strategicChat: {
    type: "container",
    title: "Strategic Intelligence Chat",
    components: [
      {
        id: "chatModeSelector",
        type: "select",
        label: "Intelligence Mode",
        options: [
          { label: "Internal Data Only", value: "internal" },
          { label: "External Intelligence", value: "external" },
          { label: "Combined Analysis", value: "combined" }
        ],
        defaultValue: "combined"
      },
      {
        id: "modelSelector",
        type: "select",
        label: "AI Model",
        options: "{{ getOpenRouterModels.data.models }}",
        optionLabels: "{{ item.name }}",
        optionValues: "{{ item.id }}",
        defaultValue: "anthropic/claude-3-sonnet"
      },
      {
        id: "chatInput",
        type: "textInput",
        label: "Ask a strategic question",
        placeholder: "What are our key growth opportunities this quarter?",
        submitOnEnter: true,
        onSubmit: "{{ strategicChat.trigger() }}"
      },
      {
        id: "chatHistory",
        type: "listView",
        data: "{{ chatMessages.value }}",
        itemTemplate: `
          <div class="chat-message {{ item.role }}">
            <div class="message-header">
              <span class="role">{{ item.role === 'user' ? 'You' : 'Sophia AI' }}</span>
              <span class="timestamp">{{ item.timestamp }}</span>
            </div>
            <div class="message-content">{{ item.content }}</div>
            {{ item.metadata ? '<div class="metadata">' + JSON.stringify(item.metadata) + '</div>' : '' }}
          </div>
        `
      }
    ]
  },

  // Executive KPIs Component
  executiveKPIs: {
    type: "container",
    title: "Executive Dashboard",
    components: [
      {
        id: "kpiCards",
        type: "grid",
        columns: 4,
        components: [
          {
            type: "statistic",
            label: "Total Revenue",
            value: "{{ getDashboardSummary.data.revenue.total }}",
            prefix: "$",
            suffix: "M",
            trend: "{{ getDashboardSummary.data.revenue.trend }}",
            trendColor: "{{ getDashboardSummary.data.revenue.trend > 0 ? 'green' : 'red' }}"
          },
          {
            type: "statistic",
            label: "Client Health Score",
            value: "{{ getDashboardSummary.data.clientHealth.average }}",
            suffix: "%",
            trend: "{{ getDashboardSummary.data.clientHealth.trend }}",
            progressBar: true
          },
          {
            type: "statistic",
            label: "Active Deals",
            value: "{{ getDashboardSummary.data.sales.activeDeals }}",
            trend: "{{ getDashboardSummary.data.sales.newThisWeek }}",
            trendLabel: "new this week"
          },
          {
            type: "statistic",
            label: "AI Tasks Completed",
            value: "{{ getDashboardSummary.data.aiMetrics.tasksCompleted }}",
            suffix: "today",
            progressBar: true,
            progressValue: "{{ getDashboardSummary.data.aiMetrics.completionRate }}"
          }
        ]
      }
    ]
  },

  // Client Health Portfolio
  clientHealth: {
    type: "container",
    title: "Client Health Portfolio",
    components: [
      {
        id: "clientHealthTable",
        type: "table",
        data: "{{ getClientHealth.data.clients }}",
        columns: [
          { 
            key: "name", 
            label: "Client Name",
            sortable: true
          },
          { 
            key: "healthScore", 
            label: "Health Score",
            sortable: true,
            cellRenderer: `
              <div style="display: flex; align-items: center;">
                <div style="width: 100px; height: 20px; background: #e0e0e0; border-radius: 10px; margin-right: 10px;">
                  <div style="width: {{ item.healthScore }}%; height: 100%; background: {{ item.healthScore > 80 ? '#4caf50' : item.healthScore > 60 ? '#ff9800' : '#f44336' }}; border-radius: 10px;"></div>
                </div>
                <span>{{ item.healthScore }}%</span>
              </div>
            `
          },
          { 
            key: "revenue", 
            label: "Monthly Revenue",
            sortable: true,
            cellRenderer: "${{ item.revenue.toLocaleString() }}"
          },
          { 
            key: "riskFactors", 
            label: "Risk Factors",
            cellRenderer: `
              {{ item.riskFactors.map(risk => '<span class="risk-badge ' + risk.severity + '">' + risk.name + '</span>').join(' ') }}
            `
          },
          {
            key: "actions",
            label: "Actions",
            cellRenderer: `
              <button onclick="{{ viewClientDetails(item.id) }}">View Details</button>
            `
          }
        ],
        pagination: true,
        pageSize: 10,
        searchable: true
      }
    ]
  },

  // Agent Status Grid
  agentStatus: {
    type: "container",
    title: "AI Agent Status",
    components: [
      {
        id: "agentGrid",
        type: "grid",
        columns: 3,
        data: "{{ getAgentStatus.data.agents }}",
        itemTemplate: `
          <div class="agent-card {{ item.status }}">
            <div class="agent-header">
              <i class="{{ item.icon }}"></i>
              <h3>{{ item.name }}</h3>
              <span class="status-badge {{ item.status }}">{{ item.status }}</span>
            </div>
            <div class="agent-metrics">
              <div class="metric">
                <span class="label">Tasks Today:</span>
                <span class="value">{{ item.tasksCompleted }}</span>
              </div>
              <div class="metric">
                <span class="label">Avg Response:</span>
                <span class="value">{{ item.avgResponseTime }}ms</span>
              </div>
              <div class="metric">
                <span class="label">Success Rate:</span>
                <span class="value">{{ item.successRate }}%</span>
              </div>
            </div>
            <div class="agent-current-task">
              {{ item.currentTask ? 'Working on: ' + item.currentTask : 'Idle' }}
            </div>
          </div>
        `
      }
    ]
  },

  // System Health Dashboard
  systemHealth: {
    type: "container",
    title: "Infrastructure Health",
    components: [
      {
        id: "healthMatrix",
        type: "grid",
        columns: 2,
        components: [
          {
            type: "chart",
            title: "System Performance",
            chartType: "line",
            data: "{{ getInfrastructure.data.performance }}",
            xAxis: "timestamp",
            yAxis: ["cpu", "memory", "disk"],
            colors: ["#2196F3", "#4CAF50", "#FF9800"]
          },
          {
            type: "chart",
            title: "API Response Times",
            chartType: "bar",
            data: "{{ getInfrastructure.data.apiMetrics }}",
            xAxis: "endpoint",
            yAxis: "avgResponseTime",
            color: "#9C27B0"
          }
        ]
      },
      {
        id: "serviceStatus",
        type: "table",
        title: "Service Status",
        data: "{{ getInfrastructure.data.services }}",
        columns: [
          { key: "name", label: "Service" },
          { 
            key: "status", 
            label: "Status",
            cellRenderer: `<span class="status-indicator {{ item.status }}">{{ item.status }}</span>`
          },
          { key: "uptime", label: "Uptime" },
          { key: "lastCheck", label: "Last Check" }
        ]
      }
    ]
  }
};

// Queries Configuration
const queries = {
  // Dashboard Summary Query
  getDashboardSummary: {
    resource: "SophiaAPI",
    type: "GET",
    url: "/api/retool/executive/dashboard-summary",
    runOnPageLoad: true,
    pollingInterval: 30000 // Refresh every 30 seconds
  },

  // Client Health Query
  getClientHealth: {
    resource: "SophiaAPI",
    type: "GET",
    url: "/api/retool/executive/client-health-portfolio",
    runOnPageLoad: true
  },

  // Strategic Chat Query
  strategicChat: {
    resource: "SophiaAPI",
    type: "POST",
    url: "/api/retool/executive/strategic-chat",
    body: {
      message: "{{ chatInput.value }}",
      mode: "{{ chatModeSelector.value }}",
      model_id: "{{ modelSelector.value }}",
      context: {
        previousMessages: "{{ chatMessages.value.slice(-5) }}"
      }
    },
    onSuccess: `
      // Add user message to chat history
      chatMessages.setValue([
        ...chatMessages.value,
        {
          role: 'user',
          content: chatInput.value,
          timestamp: new Date().toISOString()
        }
      ]);
      
      // Add AI response to chat history
      chatMessages.setValue([
        ...chatMessages.value,
        {
          role: 'assistant',
          content: strategicChat.data.response,
          metadata: strategicChat.data.metadata,
          timestamp: new Date().toISOString()
        }
      ]);
      
      // Clear input
      chatInput.setValue('');
      
      // Scroll to bottom
      chatHistory.scrollToBottom();
    `
  },

  // OpenRouter Models Query
  getOpenRouterModels: {
    resource: "SophiaAPI",
    type: "GET",
    url: "/api/retool/executive/openrouter-models",
    runOnPageLoad: true
  },

  // Agent Status Query
  getAgentStatus: {
    resource: "SophiaAPI",
    type: "GET",
    url: "/api/system/agents",
    runOnPageLoad: true,
    pollingInterval: 10000 // Refresh every 10 seconds
  },

  // Infrastructure Query
  getInfrastructure: {
    resource: "SophiaAPI",
    type: "GET",
    url: "/api/system/infrastructure",
    runOnPageLoad: true,
    pollingInterval: 15000 // Refresh every 15 seconds
  }
};

// State Variables
const stateVariables = {
  chatMessages: {
    defaultValue: [],
    persist: true
  },
  selectedClient: {
    defaultValue: null
  },
  activeTab: {
    defaultValue: "Strategic Intelligence"
  }
};

// Custom CSS
const customCSS = `
/* Chat Styles */
.chat-message {
  padding: 12px;
  margin: 8px 0;
  border-radius: 8px;
  background: #f5f5f5;
}

.chat-message.user {
  background: #e3f2fd;
  margin-left: 20%;
}

.chat-message.assistant {
  background: #f5f5f5;
  margin-right: 20%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
}

/* Status Indicators */
.status-indicator {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-indicator.healthy,
.status-indicator.active {
  background: #4caf50;
  color: white;
}

.status-indicator.warning {
  background: #ff9800;
  color: white;
}

.status-indicator.error,
.status-indicator.inactive {
  background: #f44336;
  color: white;
}

/* Agent Cards */
.agent-card {
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: white;
}

.agent-card.active {
  border-color: #4caf50;
}

.agent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.agent-metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.metric .label {
  color: #666;
}

.metric .value {
  font-weight: 500;
}

/* Risk Badges */
.risk-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  margin-right: 4px;
}

.risk-badge.high {
  background: #ffebee;
  color: #c62828;
}

.risk-badge.medium {
  background: #fff3e0;
  color: #ef6c00;
}

.risk-badge.low {
  background: #e8f5e9;
  color: #2e7d32;
}
`;

// Export configuration
module.exports = {
  dashboardConfig,
  components,
  queries,
  stateVariables,
  customCSS
};
