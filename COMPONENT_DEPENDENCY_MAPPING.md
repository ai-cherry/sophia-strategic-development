# Component Dependency Mapping

## UI Component Dependencies

### Main Frontend UI Components (Already Present)
```
frontend/src/components/ui/
├── alert-dialog.tsx    - Uses @radix-ui/react-alert-dialog
├── alert.tsx          - Basic alert component
├── avatar.tsx         - Uses @radix-ui/react-avatar
├── badge.tsx          - Basic badge component
├── button.tsx         - Uses @radix-ui/react-slot
├── card.tsx           - Basic card component
├── input.tsx          - Basic input component
├── progress.tsx       - Uses @radix-ui/react-progress
├── select.tsx         - Uses @radix-ui/react-select
├── table.tsx          - Basic table component
└── tabs.tsx           - Uses @radix-ui/react-tabs
```

### Knowledge Admin UI Components (To Be Migrated)
```
frontend/knowledge-admin/src/components/ui/
├── accordion.jsx      → frontend/src/components/ui/knowledge/accordion.tsx
├── aspect-ratio.jsx   → frontend/src/components/ui/knowledge/aspect-ratio.tsx
├── breadcrumb.jsx     → frontend/src/components/ui/knowledge/breadcrumb.tsx
├── calendar.jsx       → frontend/src/components/ui/knowledge/calendar.tsx
├── carousel.jsx       → frontend/src/components/ui/knowledge/carousel.tsx
├── chart.jsx          → frontend/src/components/ui/knowledge/chart.tsx
├── checkbox.jsx       → frontend/src/components/ui/knowledge/checkbox.tsx
├── collapsible.jsx    → frontend/src/components/ui/knowledge/collapsible.tsx
├── command.jsx        → frontend/src/components/ui/knowledge/command.tsx
├── context-menu.jsx   → frontend/src/components/ui/knowledge/context-menu.tsx
├── dialog.jsx         → frontend/src/components/ui/knowledge/dialog.tsx
├── drawer.jsx         → frontend/src/components/ui/knowledge/drawer.tsx
├── dropdown-menu.jsx  → frontend/src/components/ui/knowledge/dropdown-menu.tsx
├── form.jsx           → frontend/src/components/ui/knowledge/form.tsx
├── hover-card.jsx     → frontend/src/components/ui/knowledge/hover-card.tsx
├── input-otp.jsx      → frontend/src/components/ui/knowledge/input-otp.tsx
├── label.jsx          → frontend/src/components/ui/knowledge/label.tsx
├── menubar.jsx        → frontend/src/components/ui/knowledge/menubar.tsx
├── navigation-menu.jsx → frontend/src/components/ui/knowledge/navigation-menu.tsx
├── pagination.jsx     → frontend/src/components/ui/knowledge/pagination.tsx
├── popover.jsx        → frontend/src/components/ui/knowledge/popover.tsx
├── radio-group.jsx    → frontend/src/components/ui/knowledge/radio-group.tsx
├── resizable.jsx      → frontend/src/components/ui/knowledge/resizable.tsx
├── scroll-area.jsx    → frontend/src/components/ui/knowledge/scroll-area.tsx
├── separator.jsx      → frontend/src/components/ui/knowledge/separator.tsx
├── sheet.jsx          → frontend/src/components/ui/knowledge/sheet.tsx
├── sidebar.jsx        → frontend/src/components/ui/knowledge/sidebar.tsx
├── skeleton.jsx       → frontend/src/components/ui/knowledge/skeleton.tsx
├── slider.jsx         → frontend/src/components/ui/knowledge/slider.tsx
├── sonner.jsx         → frontend/src/components/ui/knowledge/sonner.tsx
├── switch.jsx         → frontend/src/components/ui/knowledge/switch.tsx
├── textarea.jsx       → frontend/src/components/ui/knowledge/textarea.tsx
├── toggle-group.jsx   → frontend/src/components/ui/knowledge/toggle-group.tsx
├── toggle.jsx         → frontend/src/components/ui/knowledge/toggle.tsx
└── tooltip.jsx        → frontend/src/components/ui/knowledge/tooltip.tsx
```

## Component Usage Mapping

### DocumentsPage Dependencies
```typescript
// UI Components Used:
- Button (main & knowledge)
- Input (main & knowledge)
- Card (main)
- Badge (main)
- Tabs (main & knowledge)
- Select (main & knowledge)
- Textarea (knowledge)
- Label (knowledge)
- Dialog (knowledge)
- Alert (main)
- Progress (main)

// Icons from lucide-react:
- Search, Plus, FileText, Filter, Eye, Edit, Trash2, Save, X, CheckCircle, FileUp

// External Dependencies:
- react-router-dom (Link)
- No additional libraries needed
```

### DiscoveryQueuePage Dependencies
```typescript
// UI Components Used:
- Card (main)
- Badge (main)
- Button (main & knowledge)
- Dialog (knowledge)
- Textarea (knowledge)
- Alert (main)

// Icons from lucide-react:
- Lightbulb, AlertTriangle, ThumbsUp, ThumbsDown, Edit, CheckCircle, X

// External Dependencies:
- No additional libraries needed
```

### CurationChatPage Dependencies
```typescript
// UI Components Used:
- Card (main)
- Button (main & knowledge)
- Input (main & knowledge)
- Badge (main)
- ScrollArea (knowledge)

// Icons from lucide-react:
- MessageSquare, ThumbsUp, ThumbsDown, RefreshCw, Send

// External Dependencies:
- No additional libraries needed
```

### KnowledgeAnalyticsPage Dependencies
```typescript
// UI Components Used:
- Card (main)
- Tabs (main & knowledge)
- Progress (main)
- Badge (main)

// Icons from lucide-react:
- BarChart3, TrendingUp, Users, Clock, FileText, Search

// External Dependencies:
- recharts (already in main frontend)
```

### KnowledgeSearchPage Dependencies
```typescript
// UI Components Used:
- Input (main & knowledge)
- Button (main & knowledge)
- Card (main)
- Badge (main)
- Skeleton (knowledge)

// Icons from lucide-react:
- Search, Filter

// External Dependencies:
- No additional libraries needed
```

### KnowledgeSettingsPage Dependencies
```typescript
// UI Components Used:
- Card (main)
- Tabs (main & knowledge)
- Switch (knowledge)
- Button (main & knowledge)
- Input (main & knowledge)
- Label (knowledge)
- Select (main & knowledge)

// Icons from lucide-react:
- Settings, Save, RefreshCw

// External Dependencies:
- No additional libraries needed
```

## Shared Component Conflicts & Resolution

### Components with Name Conflicts
These components exist in both frontends and need careful handling:

1. **Button** - Keep both, use main's Button by default
   ```typescript
   import { Button } from '@/components/ui/button'; // Main button
   import { Button as KnowledgeButton } from '@/components/ui/knowledge/button'; // If needed
   ```

2. **Input** - Keep both, use main's Input by default
3. **Select** - Keep both, use main's Select by default
4. **Tabs** - Keep both, use main's Tabs by default
5. **Badge** - Use main's Badge only (identical functionality)
6. **Card** - Use main's Card only (identical functionality)
7. **Alert** - Use main's Alert only (identical functionality)
8. **Progress** - Use main's Progress only (identical functionality)

### Unique Knowledge Admin Components
These don't exist in main frontend and can be imported directly:

- Dialog, Drawer, Sheet (modal variants)
- Form (with react-hook-form integration)
- Command (command palette)
- Calendar (date picker)
- Carousel (embla-carousel)
- Checkbox, Radio Group, Switch (form controls)
- Dropdown Menu, Context Menu, Menubar (menu variants)
- Popover, Hover Card, Tooltip (popover variants)
- Scroll Area (custom scrollbar)
- Skeleton (loading state)
- Sonner (toast notifications)
- And many more...

## Import Path Updates

### Before (in knowledge-admin):
```javascript
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Dialog } from '@/components/ui/dialog';
```

### After (in main frontend):
```typescript
// Use main UI components where possible
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

// Use knowledge-specific components
import { Dialog } from '@/components/ui/knowledge/dialog';
import { Calendar } from '@/components/ui/knowledge/calendar';
import { Command } from '@/components/ui/knowledge/command';
```

## Utility Function Updates

### Knowledge Admin Utils
```javascript
// frontend/knowledge-admin/src/lib/utils.js
import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}
```

### Main Frontend Utils
```typescript
// frontend/src/lib/utils.ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Resolution**: Use main frontend's utils.ts (already TypeScript)

## CSS and Styling Dependencies

### Tailwind Configuration Merge
Both apps use Tailwind CSS but knowledge-admin has additional animations:

```javascript
// Add to main frontend's tailwind.config.js
module.exports = {
  // ... existing config
  plugins: [
    // ... existing plugins
    require("tailwindcss-animate"), // Already present in both
  ],
}
```

### Additional CSS Files
```
frontend/knowledge-admin/src/App.css → frontend/src/styles/knowledge.css
```

## Hook Dependencies

### Knowledge Admin Hooks
```
frontend/knowledge-admin/src/hooks/use-mobile.js → frontend/src/hooks/useMobile.ts
```

Convert to TypeScript:
```typescript
import { useEffect, useState } from "react"

export function useMobile(breakpoint: number = 768): boolean {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < breakpoint)
    }

    checkMobile()
    window.addEventListener("resize", checkMobile)

    return () => window.removeEventListener("resize", checkMobile)
  }, [breakpoint])

  return isMobile
}
```

## State Management Integration

### Current State Management
- **Main Frontend**: React Query (@tanstack/react-query)
- **Knowledge Admin**: Local React state

### Migration Strategy
Convert knowledge admin's local state to React Query:

```typescript
// Before (local state)
const [documents, setDocuments] = useState(mockDocuments);

// After (React Query)
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { knowledgeAPI } from '@/services/knowledgeAPI';

const { data: documents, isLoading } = useQuery({
  queryKey: ['knowledge', 'documents'],
  queryFn: knowledgeAPI.documents.list
});

const createDocument = useMutation({
  mutationFn: knowledgeAPI.documents.create,
  onSuccess: () => {
    queryClient.invalidateQueries(['knowledge', 'documents']);
  }
});
```

## Testing Considerations

### Component Testing Strategy
1. Test shared UI components in isolation
2. Test page components with mocked API responses
3. Test routing integration
4. Test responsive behavior (mobile hooks)

### E2E Testing Paths
```
/dashboard                    - Existing dashboard
/knowledge                    - Knowledge base home
/knowledge/discovery          - Discovery queue
/knowledge/curation          - Curation chat
/knowledge/analytics         - Analytics
/knowledge/search            - Search
/knowledge/settings          - Settings
```

## Performance Considerations

### Code Splitting
```typescript
// Lazy load knowledge routes
const KnowledgeLayout = lazy(() => import('./components/knowledge/KnowledgeLayout'));
const DocumentsPage = lazy(() => import('./pages/knowledge/DocumentsPage'));
// ... other pages
```

### Bundle Size Impact
- Additional dependencies: ~200KB (gzipped)
- UI components: ~150KB (can be tree-shaken)
- Total estimated increase: ~350KB gzipped

### Optimization Strategies
1. Use dynamic imports for heavy components (Calendar, Chart)
2. Tree-shake unused UI components
3. Lazy load knowledge routes
4. Share common dependencies (React, Tailwind, etc.)
