# V0.dev Natural Language UI Generation Guide

## Overview

Sophia AI now integrates V0.dev for AI-powered UI component generation through natural language commands. This guide explains how to use natural language to create UI components via the unified chat interface.

## How It Works

### Architecture Flow

1. **Natural Language Input** → User types UI generation request in chat
2. **Intent Detection** → Unified chat service detects UI generation intent
3. **MCP Orchestration** → Request routed to V0.dev MCP server
4. **Component Generation** → V0.dev creates the component
5. **Multi-Server Validation** → Quality checks via Figma, UI/UX Agent, and Codacy
6. **Response with Preview** → Component code returned with live preview

### Integration Points

- **Unified Chat Service**: `backend/services/enhanced_unified_intelligence_service.py`
- **UI Intent Handler**: `backend/services/ui_generation_intent_handler.py`
- **MCP Orchestration**: `backend/services/mcp_orchestration_service.py`
- **V0.dev MCP Server**: `mcp-servers/v0dev/v0dev_mcp_server.py`

## Natural Language Commands

### Basic Component Creation

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

## Chat Integration

### Using with Sophia Chat

1. **Open Sophia Chat Interface**
   ```
   Navigate to /dashboard/chat or use the chat widget
   ```

2. **Type Natural Language Command**
   ```
   User: "Create a modern dashboard component with dark theme and real-time charts"
   ```

3. **Receive Generated Component**
   - Component code displayed in chat
   - Live preview link provided
   - Quality scores shown (accessibility, code quality)
   - Suggestions for improvements

4. **Iterate with Feedback**
   ```
   User: "Make the charts more colorful and add animations"
   ```

### Frontend Integration

```typescript
// In your React component
import { v0devClient } from '@/services/v0devClient';
import { UIComponentPreview } from '@/components/UIComponentPreview';

const ChatInterface = () => {
  const [componentCode, setComponentCode] = useState('');
  const [previewUrl, setPreviewUrl] = useState('');
  
  const handleUIGeneration = async (message: string) => {
    // This happens automatically through chat, but you can also call directly
    const response = await v0devClient.generateComponent({
      prompt: message,
      stream: true
    });
    
    setComponentCode(response.code);
    setPreviewUrl(response.previewUrl);
  };
  
  return (
    <div>
      {/* Chat interface */}
      {previewUrl && <UIComponentPreview url={previewUrl} />}
    </div>
  );
};
```

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

## API Reference

### Direct API Usage (Advanced)

```python
# Python example
from backend.services.ui_generation_intent_handler import get_ui_generation_handler

handler = get_ui_generation_handler()
response = await handler.generate_ui_from_chat(
    message="Create a dashboard component",
    user_id="user123",
    session_id="session456"
)
```

### WebSocket Integration

```javascript
// JavaScript WebSocket example
const ws = new WebSocket('ws://localhost:8000/api/v1/chat/ws/user123');

ws.send(JSON.stringify({
  type: 'chat',
  message: 'Create a modern dashboard component',
  session_id: 'session123'
}));

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  if (response.type === 'ui_generation') {
    console.log('Component:', response.data.component_code);
    console.log('Preview:', response.data.preview_url);
  }
};
```

## FastAPI Migration Note

As part of the platform-wide migration to FastAPI (10-week plan), the V0.dev integration is built with FastAPI from the start:

- **FastAPI-based MCP server** with async support
- **Pydantic models** for request/response validation
- **WebSocket support** for real-time streaming
- **Auto-generated OpenAPI docs** at `/docs`
- **Built-in CORS and middleware** support

This ensures the V0.dev integration is future-proof and aligned with the FastAPI migration strategy. 