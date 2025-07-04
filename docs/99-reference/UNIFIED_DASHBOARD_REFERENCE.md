# Unified Dashboard Reference

> Documentation for the consolidated dashboard system introduced in July 2025

## Overview

The Unified Dashboard consolidates all executive interface functionality into a single, tabbed component that provides a comprehensive view of business metrics, knowledge management, and AI interaction capabilities. This replaces multiple separate dashboard implementations with one cohesive interface.

## Component Architecture

### Main Component
```frontend/src/components/dashboard/UnifiedDashboard.jsx
├── Executive Overview Tab
├── Knowledge Management Tab
└── AI Interaction Tab
```

### Sub-Components
- **UnifiedKPICard**: Enhanced KPI display with trends and targets
- **AgnoPerformanceCard**: Agent performance monitoring
- **LLMCostAnalysis**: Cost visualization for LLM usage
- **KnowledgeManagement**: Data ingestion and sync controls
- **ExecutiveChatInterface**: Integrated AI assistant

## Features

### Executive Overview Tab

#### KPI Cards
Display key performance indicators with:
- Current value with smart formatting (K/M notation)
- Trend indicators (increase/decrease/stable)
- Percentage change from previous period
- Target progress bars
- Hover effects and animations

**Example KPIs:**
- Monthly Recurring Revenue
- Active Agents
- Agent Success Rate
- Total API Calls

#### Analytics Components

**LLM Cost Analysis**
- Bar chart visualization
- Provider cost comparison
- Interactive tooltips
- Responsive design

**Agno Performance Metrics**
- Average instantiation time (microseconds)
- Pool size and utilization
- Performance samples
- Real-time updates

### Knowledge Management Tab

#### Manual Ingestion
- File upload interface
- Drag-and-drop support
- Progress indicators
- Error handling

#### Data Source Sync
- One-click sync for:
  - Gong calls
  - HubSpot CRM
  - Snowflake tables
- Loading states
- Success/error feedback

#### Ingestion Status Table
- Recent job tracking
- Status indicators (Success/Processing/Failed/Queued)
- Timestamp display
- Source and document information

### AI Interaction Tab

#### Executive Chat Interface
- Conversational AI assistant
- Context-aware responses
- Message history
- Suggested prompts
- Real-time typing indicators

## Component Props

### UnifiedDashboard
No required props - fully self-contained with internal state management.

### UnifiedKPICard Props
```javascript
{
  title: string,          // KPI name
  value: number|string,   // Current value
  change: string,         // e.g., "+3.2%"
  changeType: 'increase'|'decrease'|'stable',
  icon: Component,        // Lucide icon component
  target: number          // Optional target value
}
```

### AgnoPerformanceCard Props
```javascript
{
  metrics: object,        // Performance data
  loading: boolean,       // Loading state
  error: string          // Error message
}
```

## Styling

### Design System
- **Colors**: Purple-600 primary, gray scale for secondary
- **Shadows**: Tailwind shadow utilities
- **Borders**: Gray-200 default, purple-300 on hover
- **Spacing**: Consistent padding/margin using Tailwind classes

### Responsive Design
- Mobile-first approach
- Grid layouts with responsive breakpoints
- Collapsible sections on mobile
- Touch-friendly interactions

## Integration

### API Integration
```javascript
import { api } from '../../services/apiClient';

// Fetch KPI data
const kpiData = await api.dashboard.getKPIs();

// Get Agno metrics
const agnoMetrics = await api.agno.getPerformanceMetrics();

// Knowledge management operations
await api.knowledge.uploadFile(file);
await api.knowledge.syncSource('gong');
```

### State Management
- React hooks for local state
- Effect hooks for data fetching
- Optimistic UI updates
- Error boundaries for resilience

## Usage Example

```jsx
import UnifiedDashboard from '@/components/dashboard/UnifiedDashboard';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <UnifiedDashboard />
    </div>
  );
}
```

## Performance Optimizations

### Lazy Loading
- Tab content loaded on demand
- Charts rendered only when visible
- Heavy components use React.lazy()

### Data Caching
- API responses cached with TTL
- Optimistic updates for user actions
- Background refresh for real-time data

### Rendering Optimization
- React.memo for expensive components
- useCallback for event handlers
- Virtualization for large lists

## Accessibility

### WCAG 2.1 Compliance
- Semantic HTML structure
- ARIA labels and descriptions
- Keyboard navigation support
- Screen reader announcements
- Color contrast ratios

### Interactive Elements
- Focus indicators
- Hover states
- Loading announcements
- Error messages

## Mobile Considerations

### Responsive Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Touch Optimizations
- Larger tap targets (minimum 44x44px)
- Swipe gestures for tab navigation
- Pull-to-refresh functionality
- Optimized scrolling performance

## Future Enhancements

### Planned Features
- Customizable dashboard layouts
- Widget drag-and-drop
- Real-time collaboration
- Advanced filtering and search
- Export functionality

### Performance Goals
- Initial load < 2 seconds
- Tab switch < 100ms
- Chart updates < 200ms
- 60fps scrolling performance

## Troubleshooting

### Common Issues

**Data not loading**
- Check API connectivity
- Verify authentication
- Review console errors

**Performance issues**
- Check network tab for slow requests
- Profile React components
- Review browser performance metrics

**Style conflicts**
- Ensure Tailwind CSS is properly configured
- Check for CSS specificity issues
- Verify component isolation

---

*Last Updated: July 2025*
*Component Version: 2.0.0*
