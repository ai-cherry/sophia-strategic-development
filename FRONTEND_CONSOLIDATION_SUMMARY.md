# Frontend Consolidation Summary

## Quick Overview

Consolidating two React apps:
- **Main Frontend**: Executive dashboard (TypeScript, React 18)
- **Knowledge Admin**: Knowledge base management (JavaScript, React 19)

Goal: Merge Knowledge Admin into Main Frontend as `/knowledge/*` routes

## Key Actions

### 1. Run Migration Script (Automated)
```bash
./scripts/migrate-knowledge-admin.sh
```

This script will:
- Create backups
- Set up directory structure
- Create TypeScript types
- Copy UI components
- Update package.json
- Generate migration files

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Manual Steps Required

#### Update App.tsx
Replace `frontend/src/App.tsx` with `frontend/src/App-updated.tsx`:
```bash
cd frontend
mv src/App.tsx src/App-old.tsx
mv src/App-updated.tsx src/App.tsx
```

#### Convert Components to TypeScript
The migration script extracts components but they need TypeScript conversion:
- Navigation → KnowledgeNav.tsx
- DocumentCard → DocumentCard.tsx
- DocumentEditor → DocumentEditor.tsx
- All page components (DocumentsPage, etc.)

#### Update Main Navigation
Add "Knowledge Base" link to the main dashboard navigation

### 4. Test Integration
```bash
cd frontend
npm run dev
```

Test all routes:
- `/dashboard` - Existing dashboard (should work as before)
- `/knowledge` - Knowledge documents
- `/knowledge/discovery` - Discovery queue
- `/knowledge/curation` - Curation chat
- `/knowledge/analytics` - Analytics
- `/knowledge/search` - Search
- `/knowledge/settings` - Settings

### 5. Cleanup (After Successful Testing)
```bash
rm -rf frontend/knowledge-admin
```

## File Structure After Migration

```
frontend/src/
├── components/
│   ├── dashboard/        # Existing dashboard components
│   ├── knowledge/        # New knowledge components
│   │   ├── KnowledgeLayout.tsx
│   │   ├── KnowledgeNav.tsx
│   │   ├── DocumentCard.tsx
│   │   └── DocumentEditor.tsx
│   └── ui/
│       ├── ...          # Existing UI components
│       └── knowledge/   # Knowledge-specific UI components
├── pages/
│   └── knowledge/       # Knowledge page components
├── services/
│   ├── apiClient.js     # Existing API client
│   └── knowledgeAPI.ts  # New knowledge API
└── types/
    └── knowledge.ts     # Knowledge TypeScript types
```

## Dependencies Added

- `@hookform/resolvers` - Form validation
- `cmdk` - Command palette
- `date-fns` - Date utilities
- `embla-carousel-react` - Carousel
- `framer-motion` - Animations
- `react-hook-form` - Forms
- `react-resizable-panels` - Resizable panels
- `sonner` - Toast notifications
- `vaul` - Drawer component
- `zod` - Schema validation

## Potential Issues & Solutions

### React Version Conflict
- **Issue**: Knowledge Admin uses React 19, Main uses React 18
- **Solution**: Standardize on React 18 (more stable)

### UI Component Conflicts
- **Issue**: Both apps have Button, Input, Select, etc.
- **Solution**: Namespace knowledge components in `/ui/knowledge/`

### TypeScript Conversion
- **Issue**: Knowledge Admin is JavaScript
- **Solution**: Manual conversion using provided types

### State Management
- **Issue**: Knowledge Admin uses local state
- **Solution**: Convert to React Query (already in main app)

## Success Criteria

✅ All knowledge features accessible via `/knowledge/*` routes
✅ No regression in dashboard functionality
✅ Consistent UI/UX across both sections
✅ Single build/deploy process
✅ Reduced maintenance overhead

## Timeline

- **Day 1**: Run migration script, install dependencies
- **Day 2-3**: Convert components to TypeScript
- **Day 4**: Test integration thoroughly
- **Day 5**: Fix issues and optimize
- **Day 6**: Update documentation
- **Day 7**: Deploy consolidated app

Total: ~1 week with minimal disruption
