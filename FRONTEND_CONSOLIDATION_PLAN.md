# Sophia AI Frontend Consolidation Plan

## Executive Summary

This plan outlines the consolidation of two frontend applications:
1. **Main Frontend** (`/frontend/`) - React 18 + Vite + TypeScript app for executive dashboard
2. **Knowledge Admin** (`/frontend/knowledge-admin/`) - React 19 + Vite + JavaScript app for knowledge base management

The goal is to merge Knowledge Admin into the main frontend as a route/module while maintaining all functionality.

## Current Architecture Analysis

### Main Frontend (sophia-unified-frontend)
- **Tech Stack**: React 18, TypeScript, Vite 7, React Router 6
- **Purpose**: Executive dashboard with business intelligence
- **Key Features**:
  - Executive Overview with KPIs
  - Infrastructure Health monitoring
  - AI Memory management
  - Deployment tracking
  - Data Flow visualization
  - Project management (Asana integration)
- **Routing**: Simple structure with `/dashboard` as main route
- **UI Components**: Custom components using Radix UI primitives

### Knowledge Admin (sophia-admin-knowledge)
- **Tech Stack**: React 19, JavaScript (no TypeScript), Vite 6, React Router 7
- **Purpose**: Knowledge base management system
- **Key Features**:
  - Document management (CRUD operations)
  - Discovery Queue for proactive insights
  - Curation Chat interface
  - Analytics dashboard
  - Search functionality
  - Settings management
- **Routing**: Multi-page app with 6 main routes
- **UI Components**: Extensive shadcn/ui component library

## Dependency Analysis

### Version Conflicts to Resolve
1. **React**: 18.2.0 (main) vs 19.1.0 (knowledge-admin) → Standardize on React 18
2. **React Router**: 6.22.3 (main) vs 7.6.1 (knowledge-admin) → Use React Router 6
3. **Vite**: 7.0.2 (main) vs 6.3.5 (knowledge-admin) → Keep Vite 7
4. **Lucide Icons**: 0.363.0 (main) vs 0.510.0 (knowledge-admin) → Update to latest

### New Dependencies to Add to Main Frontend
- `@hookform/resolvers` - Form validation
- `cmdk` - Command menu component
- `date-fns` - Date utilities
- `embla-carousel-react` - Carousel component
- `framer-motion` - Animation library
- `react-hook-form` - Form management
- `react-resizable-panels` - Resizable panels
- `sonner` - Toast notifications
- `vaul` - Drawer component
- `zod` - Schema validation

## Migration Strategy

### Phase 1: Preparation (Day 1)
1. **Backup Current State**
   ```bash
   cp -r frontend frontend-backup-$(date +%Y%m%d)
   cp -r frontend/knowledge-admin frontend/knowledge-admin-backup-$(date +%Y%m%d)
   ```

2. **Update Main Frontend Dependencies**
   - Add missing dependencies from knowledge-admin
   - Resolve version conflicts
   - Update package.json

3. **TypeScript Configuration**
   - Create type definitions for migrated components
   - Set up path aliases for cleaner imports

### Phase 2: Component Migration (Day 2-3)

#### Component Mapping

| Knowledge Admin Component | Target Location in Main Frontend | Notes |
|--------------------------|----------------------------------|-------|
| `/src/components/ui/*` | `/src/components/ui/knowledge/*` | Namespace to avoid conflicts |
| `/src/App.jsx` (routes) | `/src/components/knowledge/KnowledgeRoutes.tsx` | Convert to TypeScript |
| Navigation | `/src/components/knowledge/KnowledgeNav.tsx` | Integrate with main nav |
| DocumentCard | `/src/components/knowledge/DocumentCard.tsx` | |
| DocumentEditor | `/src/components/knowledge/DocumentEditor.tsx` | |
| DiscoveryQueue | `/src/components/knowledge/DiscoveryQueue.tsx` | |
| CurationChat | `/src/components/knowledge/CurationChat.tsx` | |

#### Migration Steps for Each Component:
1. Copy component file to new location
2. Convert from `.jsx` to `.tsx`
3. Add TypeScript types and interfaces
4. Update import paths
5. Test component in isolation

### Phase 3: Routing Integration (Day 4)

#### New Routing Structure
```typescript
// src/App.tsx
<Router>
  <Routes>
    {/* Existing routes */}
    <Route path="/dashboard" element={<UnifiedDashboard />} />

    {/* Knowledge Base routes */}
    <Route path="/knowledge" element={<KnowledgeLayout />}>
      <Route index element={<DocumentsPage />} />
      <Route path="discovery" element={<DiscoveryQueuePage />} />
      <Route path="curation" element={<CurationChatPage />} />
      <Route path="analytics" element={<KnowledgeAnalyticsPage />} />
      <Route path="search" element={<KnowledgeSearchPage />} />
      <Route path="settings" element={<KnowledgeSettingsPage />} />
    </Route>

    <Route path="/" element={<Navigate to="/dashboard" />} />
  </Routes>
</Router>
```

### Phase 4: UI Integration (Day 5)

1. **Navigation Integration**
   - Add "Knowledge Base" to main navigation
   - Create unified navigation component
   - Ensure consistent styling

2. **Theme Consistency**
   - Merge Tailwind configurations
   - Standardize color schemes
   - Ensure responsive design

3. **Component Library Consolidation**
   - Map shadcn/ui components to existing UI components
   - Create adapter layer where needed
   - Standardize component APIs

### Phase 5: API Integration (Day 6)

1. **Update API Client**
   ```typescript
   // Add knowledge base endpoints
   export const knowledgeAPI = {
     documents: {
       list: () => apiClient.get('/api/v1/knowledge/documents'),
       create: (data) => apiClient.post('/api/v1/knowledge/documents', data),
       update: (id, data) => apiClient.put(`/api/v1/knowledge/documents/${id}`, data),
       delete: (id) => apiClient.delete(`/api/v1/knowledge/documents/${id}`)
     },
     insights: {
       list: () => apiClient.get('/api/v1/knowledge/insights'),
       approve: (id) => apiClient.post(`/api/v1/knowledge/insights/${id}/approve`),
       reject: (id) => apiClient.post(`/api/v1/knowledge/insights/${id}/reject`)
     }
   };
   ```

2. **State Management**
   - Use React Query for data fetching (already in main app)
   - Migrate local state to React Query mutations

### Phase 6: Testing & Cleanup (Day 7)

1. **Testing Checklist**
   - [ ] All routes accessible
   - [ ] Document CRUD operations work
   - [ ] Discovery queue functions properly
   - [ ] Curation chat sends/receives messages
   - [ ] Analytics display correctly
   - [ ] Search returns results
   - [ ] Settings save properly
   - [ ] Navigation between sections smooth
   - [ ] Responsive design intact

2. **Cleanup**
   - Remove knowledge-admin directory
   - Remove duplicate dependencies
   - Update documentation
   - Update deployment scripts

## File-by-File Migration Guide

### Core Application Files

```bash
# 1. Main App Component
frontend/knowledge-admin/src/App.jsx → frontend/src/components/knowledge/KnowledgeApp.tsx

# 2. Pages
frontend/knowledge-admin/src/App.jsx (DocumentsPage) → frontend/src/pages/knowledge/DocumentsPage.tsx
frontend/knowledge-admin/src/App.jsx (DiscoveryQueuePage) → frontend/src/pages/knowledge/DiscoveryQueuePage.tsx
frontend/knowledge-admin/src/App.jsx (CurationChatPage) → frontend/src/pages/knowledge/CurationChatPage.tsx
frontend/knowledge-admin/src/App.jsx (AnalyticsPage) → frontend/src/pages/knowledge/AnalyticsPage.tsx
frontend/knowledge-admin/src/App.jsx (SearchPage) → frontend/src/pages/knowledge/SearchPage.tsx
frontend/knowledge-admin/src/App.jsx (SettingsPage) → frontend/src/pages/knowledge/SettingsPage.tsx

# 3. Components
frontend/knowledge-admin/src/App.jsx (Navigation) → frontend/src/components/knowledge/KnowledgeNav.tsx
frontend/knowledge-admin/src/App.jsx (DocumentCard) → frontend/src/components/knowledge/DocumentCard.tsx
frontend/knowledge-admin/src/App.jsx (DocumentEditor) → frontend/src/components/knowledge/DocumentEditor.tsx

# 4. UI Components (namespace to avoid conflicts)
frontend/knowledge-admin/src/components/ui/*.jsx → frontend/src/components/ui/knowledge/*.tsx

# 5. Utilities
frontend/knowledge-admin/src/lib/utils.js → frontend/src/lib/knowledge-utils.ts
frontend/knowledge-admin/src/hooks/use-mobile.js → frontend/src/hooks/useMobile.ts

# 6. Styles
frontend/knowledge-admin/src/App.css → frontend/src/styles/knowledge.css
```

## Implementation Commands

### Step 1: Install Dependencies
```bash
cd frontend
npm install @hookform/resolvers cmdk date-fns embla-carousel-react framer-motion react-hook-form react-resizable-panels sonner vaul zod
```

### Step 2: Create Directory Structure
```bash
mkdir -p src/pages/knowledge
mkdir -p src/components/knowledge
mkdir -p src/components/ui/knowledge
```

### Step 3: Migration Script
```bash
# Create a migration script to automate file copying and conversion
cat > migrate-knowledge-admin.sh << 'EOF'
#!/bin/bash

# Copy and convert components
echo "Migrating Knowledge Admin components..."

# Create TypeScript interfaces
cat > src/types/knowledge.ts << 'TYPES'
export interface Document {
  id: string;
  title: string;
  content: string;
  contentType: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  tags: string[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  version: number;
}

export interface ProactiveInsight {
  id: string;
  type: 'new_competitor' | 'product_gap' | 'use_case';
  source: string;
  sourceUrl: string;
  insight: string;
  question: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected';
  confidence: number;
  context: string;
}
TYPES

echo "Knowledge Admin migration complete!"
EOF

chmod +x migrate-knowledge-admin.sh
```

## Success Criteria

1. **Functionality Preserved**
   - All knowledge admin features work as before
   - No regression in main dashboard functionality

2. **Performance Maintained**
   - Page load times remain under 2 seconds
   - Smooth navigation between sections

3. **Code Quality**
   - All components properly typed with TypeScript
   - No console errors or warnings
   - ESLint passes without errors

4. **User Experience**
   - Seamless integration with main app
   - Consistent UI/UX across all sections
   - Responsive design maintained

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**
   ```bash
   git checkout main
   rm -rf frontend
   cp -r frontend-backup-[date] frontend
   ```

2. **Partial Rollback**
   - Keep knowledge-admin as separate app
   - Add iframe integration as temporary solution
   - Plan phased migration over longer period

## Post-Migration Tasks

1. **Documentation Updates**
   - Update README with new structure
   - Document new routes and components
   - Update deployment guides

2. **CI/CD Updates**
   - Update build scripts
   - Remove knowledge-admin build step
   - Update deployment configuration

3. **Monitoring**
   - Set up error tracking for new routes
   - Monitor performance metrics
   - Track user engagement with knowledge features

## Timeline Summary

- **Day 1**: Preparation and dependency updates
- **Day 2-3**: Component migration and TypeScript conversion
- **Day 4**: Routing integration
- **Day 5**: UI and theme integration
- **Day 6**: API integration and state management
- **Day 7**: Testing and cleanup

Total estimated time: 7 working days with minimal disruption to existing functionality.
