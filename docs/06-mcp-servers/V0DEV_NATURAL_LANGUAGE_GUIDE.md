# V0.dev Natural Language UI Generation Guide

## Overview

V0.dev AI-powered UI component generation is fully integrated into Sophia AI's **Unified Chat** interface within the **Unified Dashboard**. There are no separate commands or interfaces - simply type your UI generation requests naturally in the unified chat, and Sophia will automatically detect your intent and route it to the appropriate services.

## How It Works

### Architecture Flow

1. **Unified Chat Input** → Type UI request in the unified chat interface
2. **Automatic Intent Detection** → Unified intelligence service detects UI generation intent
3. **Intelligent Routing** → Request automatically routed through MCP orchestration
4. **Component Generation** → V0.dev creates the component behind the scenes
5. **Multi-Server Validation** → Quality checks via integrated services
6. **Unified Response** → Component returned in the chat with preview

### Key Integration Points

- **Single Entry Point**: `frontend/src/components/dashboard/UnifiedDashboard.tsx`
- **Unified Chat Service**: All requests go through `backend/services/enhanced_unified_intelligence_service.py`
- **Automatic Routing**: No manual server selection - intelligence service handles everything
- **Seamless Experience**: No need to know which MCP server handles what

## Using V0.dev Through Unified Chat

### IMPORTANT: No Special Commands Needed

Simply type your UI generation requests naturally in the unified chat. The system automatically understands and routes your request. **Do NOT use @v0dev or any other prefix**.

### Natural Language Examples

Type these directly in the unified chat:

```
"Create a dashboard component with glassmorphism styling"
"Build a responsive navigation bar with dropdown menus"
"Generate a data table component with sorting and filtering"
"Design a modal dialog with form validation"
"Create a chart component for revenue visualization"
"Build a user profile card with avatar and social links"
```

### Style-Specific Requests

```
"Create a modern dashboard with dark theme"
"Build a minimal contact form with validation"
"Generate a glassmorphism card component"
"Design a neomorphic button set"
"Create a gradient hero section"
```

### Framework-Specific Commands

```
"Create a React component for user authentication"
"Build a Next.js dashboard layout"
"Generate a TypeScript interface for the data table"
"Create a Tailwind CSS card component"
```

### Advanced Requests

```
"Create a dashboard showing KPIs with real-time updates"
"Build a form that integrates with our Snowflake data"
"Generate a component matching our Figma design system"
"Create an accessible data visualization component"
```

## Usage Examples

### Example 1: Executive Dashboard Component

**Natural Language Request:**
```
"Create an executive dashboard component with KPI cards showing revenue, 
user growth, and performance metrics with glassmorphism styling"
```

**Response:**
```tsx
// Generated Executive Dashboard Component
import React from 'react';
import { Card, Grid, Typography } from '@mui/material';
import { TrendingUp, Users, Speed } from 'lucide-react';

const ExecutiveDashboard = () => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card className="glassmorphism-card">
          <div className="kpi-content">
            <TrendingUp className="kpi-icon" />
            <Typography variant="h6">Revenue</Typography>
            <Typography variant="h3">$2.4M</Typography>
            <Typography variant="body2" color="success">
              +12% from last month
            </Typography>
          </div>
        </Card>
      </Grid>
      {/* Additional KPI cards... */}
    </Grid>
  );
};

export default ExecutiveDashboard;
```

### Example 2: Data Table with Actions

**Natural Language Request:**
```
"Build a data table component for customer management with sorting, 
filtering, and action buttons for edit and delete"
```

**Response:**
```tsx
// Generated Customer Data Table Component
import React, { useState } from 'react';
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  IconButton,
  TextField,
  TableSortLabel
} from '@mui/material';
import { Edit, Delete, Search } from 'lucide-react';

const CustomerDataTable = ({ data }) => {
  const [filter, setFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Sorting and filtering logic
  const filteredData = data.filter(customer =>
    customer.name.toLowerCase().includes(filter.toLowerCase())
  );
  
  return (
    <div>
      <TextField
        placeholder="Search customers..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        InputProps={{
          startAdornment: <Search size={20} />
        }}
      />
      <Table>
        {/* Table implementation... */}
      </Table>
    </div>
  );
};

export default CustomerDataTable;
```

## Using Within the Unified Dashboard

### Access Through Unified Chat Tab

1. **Open Unified Dashboard**
   - Navigate to your Sophia AI instance
   - The unified dashboard is your single entry point

2. **Select Unified Chat Tab**
   - Click on the "Unified Chat" tab
   - This is where all interactions happen

3. **Type Natural Language Requests**
   ```
   User: "Create a modern dashboard component with dark theme and real-time charts"
   ```

4. **Receive Integrated Response**
   - Component code displayed in chat
   - Live preview embedded in response
   - Quality scores integrated
   - Suggestions included

5. **Iterate Naturally**
   ```
   User: "Make the charts more colorful and add animations"
   ```

### Unified Dashboard Integration

The generated components are designed to work seamlessly within the unified dashboard:

```typescript
// Components automatically integrate with UnifiedDashboard.tsx
const UnifiedDashboard = () => {
  // Your generated components can be added as new tabs or within existing tabs
  {activeTab === 'custom-dashboard' && <YourGeneratedComponent />}
};
```

### No Separate Interfaces

- ❌ No separate V0.dev interface
- ❌ No command-line tools needed
- ❌ No direct API calls required
- ✅ Everything through unified chat
- ✅ All within unified dashboard
- ✅ Automatic intelligent routing

## Best Practices

### 1. Be Specific About Requirements
```
Good: "Create a dashboard with 3 KPI cards showing revenue, users, and performance with trend indicators"
Better: "Create an executive dashboard with glassmorphism KPI cards for revenue (with monthly trend), active users (with growth percentage), and system performance (with uptime metric)"
```

### 2. Specify Style Preferences
```
"Create a button" → Basic button
"Create a modern gradient button with hover effects" → Styled button
"Create a glassmorphism button matching our design system" → Brand-aligned button
```

### 3. Include Functionality Details
```
"Create a form" → Basic form
"Create a contact form with email validation and submit handling" → Functional form
"Create a multi-step form with progress indicator and field validation" → Complex form
```

### 4. Mention Framework/Library Preferences
```
"Use Material-UI components"
"Implement with Tailwind CSS"
"Create using shadcn/ui components"
"Build with vanilla CSS"
```

## Supported Component Types

- **Dashboards**: KPI cards, analytics, metrics
- **Forms**: Contact, login, registration, multi-step
- **Tables**: Data grids, sortable, filterable
- **Navigation**: Headers, sidebars, breadcrumbs
- **Cards**: Product, user profile, content
- **Modals**: Dialogs, confirmations, forms
- **Charts**: Line, bar, pie, area charts
- **Buttons**: Primary, secondary, icon buttons
- **Inputs**: Text fields, selects, checkboxes
- **Layouts**: Grid, flex, responsive layouts

## Quality Assurance

Each generated component goes through:

1. **Accessibility Check** (UI/UX Agent)
   - WCAG 2.1 compliance
   - Keyboard navigation
   - Screen reader support

2. **Code Quality** (Codacy)
   - TypeScript compliance
   - Best practices
   - Performance optimization

3. **Design Validation** (Figma Context)
   - Design system alignment
   - Consistent styling
   - Responsive design

## Troubleshooting

### Component Not Generating
- Ensure V0.dev MCP server is running (port 9023)
- Check if prompt contains UI-related keywords
- Verify API key configuration

### Preview Not Loading
- Check network connectivity
- Ensure preview service is accessible
- Try regenerating the component

### Style Issues
- Be more specific about styling requirements
- Reference existing design system
- Provide color/theme preferences

## Technical Architecture (For Developers)

### How It Works Under the Hood

While users interact only through the unified chat, here's what happens internally:

1. **Unified Chat** receives the message
2. **Intent Detection** in `enhanced_unified_intelligence_service.py`
3. **Routing** through `ui_generation_intent_handler.py`
4. **Orchestration** via `mcp_orchestration_service.py`
5. **Generation** by V0.dev MCP server
6. **Response** back through unified chat

### Integration Points

- All UI generation requests are automatically handled
- No direct API calls needed - use unified chat
- Components integrate directly with `UnifiedDashboard.tsx`
- WebSocket connections managed by unified chat service

### IMPORTANT: Always Use Unified Chat

Direct API usage is not recommended. All interactions should go through the unified chat interface to ensure:
- Proper authentication and authorization
- Consistent user experience
- Automatic context management
- Integrated response handling

## FastAPI Migration Note

As part of the platform-wide migration to FastAPI (10-week plan), the V0.dev integration is built with FastAPI from the start:

- **FastAPI-based MCP server** with async support
- **Pydantic models** for request/response validation
- **WebSocket support** for real-time streaming
- **Auto-generated OpenAPI docs** at `/docs`
- **Built-in CORS and middleware** support

This ensures the V0.dev integration is future-proof and aligned with the FastAPI migration strategy. 