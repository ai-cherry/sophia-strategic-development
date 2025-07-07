#!/bin/bash

# Sophia AI Frontend Consolidation Script
# This script automates the migration of knowledge-admin into the main frontend

set -e  # Exit on error

echo "🚀 Starting Sophia AI Frontend Consolidation..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "frontend" ] || [ ! -d "frontend/knowledge-admin" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Create backups
print_status "Creating backups..."
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
cp -r frontend "frontend-backup-${BACKUP_DATE}"
print_status "Backup created: frontend-backup-${BACKUP_DATE}"

# Step 2: Create directory structure
print_status "Creating directory structure..."
mkdir -p frontend/src/pages/knowledge
mkdir -p frontend/src/components/knowledge
mkdir -p frontend/src/components/ui/knowledge
mkdir -p frontend/src/styles

# Step 3: Create TypeScript type definitions
print_status "Creating TypeScript type definitions..."
cat > frontend/src/types/knowledge.ts << 'EOF'
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

export interface KnowledgeStats {
  totalDocuments: number;
  publishedDocuments: number;
  draftDocuments: number;
  totalSearches: number;
  avgResponseTime: string;
  knowledgeCoverage: number;
}

export interface ContentType {
  value: string;
  label: string;
  color: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: 'positive' | 'negative';
  correction?: string;
}
EOF

# Step 4: Create the migration helper script
print_status "Creating migration helper functions..."
cat > frontend/src/utils/migrate-jsx-to-tsx.js << 'EOF'
const fs = require('fs');
const path = require('path');

function convertJsxToTsx(jsxContent, componentName) {
    // Add TypeScript imports
    let tsxContent = jsxContent;

    // Replace React import if needed
    tsxContent = tsxContent.replace(
        "import React from 'react'",
        "import React from 'react'"
    );

    // Add type annotations to function components
    tsxContent = tsxContent.replace(
        /function\s+(\w+)\s*\((.*?)\)\s*{/g,
        (match, name, params) => {
            if (params.trim() === '') {
                return `function ${name}(): React.ReactElement {`;
            } else {
                return `function ${name}(${params}: any): React.ReactElement {`;
            }
        }
    );

    // Convert arrow functions
    tsxContent = tsxContent.replace(
        /const\s+(\w+)\s*=\s*\((.*?)\)\s*=>\s*{/g,
        (match, name, params) => {
            if (params.trim() === '') {
                return `const ${name}: React.FC = () => {`;
            } else {
                return `const ${name}: React.FC<any> = (${params}) => {`;
            }
        }
    );

    // Add basic type annotations to useState
    tsxContent = tsxContent.replace(
        /useState\((.*?)\)/g,
        (match, initialValue) => {
            if (initialValue === 'null' || initialValue === 'undefined') {
                return `useState<any>(${initialValue})`;
            } else if (initialValue.startsWith('[') || initialValue.startsWith('{')) {
                return `useState<any>(${initialValue})`;
            } else if (initialValue === 'true' || initialValue === 'false') {
                return `useState<boolean>(${initialValue})`;
            } else if (!isNaN(initialValue)) {
                return `useState<number>(${initialValue})`;
            } else if (initialValue.startsWith("'") || initialValue.startsWith('"')) {
                return `useState<string>(${initialValue})`;
            }
            return match;
        }
    );

    return tsxContent;
}

module.exports = { convertJsxToTsx };
EOF

# Step 5: Extract components from App.jsx
print_status "Extracting components from knowledge-admin App.jsx..."

# Create a Node.js script to extract components
cat > frontend/extract-components.mjs << 'EOF'
import fs from 'fs';
import path from 'path';

// Read the App.jsx file
const appContent = fs.readFileSync('knowledge-admin/src/App.jsx', 'utf8');

// Extract Navigation component
const navStart = appContent.indexOf('function Navigation()');
const navEnd = appContent.indexOf('\n}\n', navStart) + 3;
const navigationComponent = appContent.substring(navStart, navEnd);

// Extract DocumentCard component
const cardStart = appContent.indexOf('function DocumentCard(');
const cardEnd = appContent.indexOf('\n}\n', cardStart) + 3;
const documentCardComponent = appContent.substring(cardStart, cardEnd);

// Extract DocumentEditor component
const editorStart = appContent.indexOf('function DocumentEditor(');
const editorEnd = appContent.indexOf('\n}\n', editorStart) + 3;
const documentEditorComponent = appContent.substring(editorStart, editorEnd);

// Extract page components
const pages = [
    'DocumentsPage',
    'AnalyticsPage',
    'SearchPage',
    'SettingsPage',
    'DiscoveryQueuePage',
    'CurationChatPage'
];

const extractedPages = {};
pages.forEach(pageName => {
    const pageStart = appContent.indexOf(`function ${pageName}()`);
    if (pageStart !== -1) {
        const pageEnd = appContent.indexOf(`\n}\n`, pageStart) + 3;
        extractedPages[pageName] = appContent.substring(pageStart, pageEnd);
    }
});

// Save extracted components
console.log('✓ Components extracted successfully');
console.log(`  - Navigation: ${navigationComponent.length} chars`);
console.log(`  - DocumentCard: ${documentCardComponent.length} chars`);
console.log(`  - DocumentEditor: ${documentEditorComponent.length} chars`);
console.log(`  - Pages: ${Object.keys(extractedPages).length} pages extracted`);

// Write to temporary files for further processing
fs.writeFileSync('frontend/temp-navigation.jsx', navigationComponent);
fs.writeFileSync('frontend/temp-documentcard.jsx', documentCardComponent);
fs.writeFileSync('frontend/temp-documenteditor.jsx', documentEditorComponent);
Object.entries(extractedPages).forEach(([name, content]) => {
    fs.writeFileSync(`frontend/temp-${name.toLowerCase()}.jsx`, content);
});
EOF

# Run the extraction script
cd frontend && node extract-components.mjs && cd ..

# Step 6: Copy UI components
print_status "Copying UI components..."
if [ -d "frontend/knowledge-admin/src/components/ui" ]; then
    cp -r frontend/knowledge-admin/src/components/ui/* frontend/src/components/ui/knowledge/
    print_status "UI components copied"
else
    print_warning "No UI components directory found"
fi

# Step 7: Create the Knowledge Layout component
print_status "Creating Knowledge Layout component..."
cat > frontend/src/components/knowledge/KnowledgeLayout.tsx << 'EOF'
import React from 'react';
import { Outlet } from 'react-router-dom';
import { KnowledgeNav } from './KnowledgeNav';

export const KnowledgeLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <KnowledgeNav />
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
};
EOF

# Step 8: Create API integration
print_status "Creating API integration..."
cat > frontend/src/services/knowledgeAPI.ts << 'EOF'
import apiClient from './apiClient';
import { Document, ProactiveInsight, KnowledgeStats } from '@/types/knowledge';

export const knowledgeAPI = {
  documents: {
    list: () => apiClient.get<Document[]>('/api/v1/knowledge/documents'),
    get: (id: string) => apiClient.get<Document>(`/api/v1/knowledge/documents/${id}`),
    create: (data: Partial<Document>) => apiClient.post<Document>('/api/v1/knowledge/documents', data),
    update: (id: string, data: Partial<Document>) => apiClient.put<Document>(`/api/v1/knowledge/documents/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/v1/knowledge/documents/${id}`),
    search: (query: string) => apiClient.get<Document[]>(`/api/v1/knowledge/documents/search?q=${query}`)
  },

  insights: {
    list: () => apiClient.get<ProactiveInsight[]>('/api/v1/knowledge/insights'),
    approve: (id: string) => apiClient.post(`/api/v1/knowledge/insights/${id}/approve`),
    reject: (id: string) => apiClient.post(`/api/v1/knowledge/insights/${id}/reject`),
    edit: (id: string, data: Partial<ProactiveInsight>) => apiClient.put(`/api/v1/knowledge/insights/${id}`, data)
  },

  analytics: {
    stats: () => apiClient.get<KnowledgeStats>('/api/v1/knowledge/analytics/stats'),
    searchHistory: () => apiClient.get('/api/v1/knowledge/analytics/search-history'),
    documentActivity: () => apiClient.get('/api/v1/knowledge/analytics/document-activity')
  },

  chat: {
    sendMessage: (message: string) => apiClient.post('/api/v1/knowledge/chat', { message }),
    getHistory: () => apiClient.get('/api/v1/knowledge/chat/history'),
    provideFeedback: (messageId: string, feedback: 'positive' | 'negative', correction?: string) =>
      apiClient.post(`/api/v1/knowledge/chat/${messageId}/feedback`, { feedback, correction })
  }
};
EOF

# Step 9: Update App.tsx with new routes
print_status "Updating App.tsx with knowledge routes..."
cat > frontend/src/App-updated.tsx << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import UnifiedDashboard from './components/dashboard/UnifiedDashboard';
import { KnowledgeLayout } from './components/knowledge/KnowledgeLayout';
import { DocumentsPage } from './pages/knowledge/DocumentsPage';
import { DiscoveryQueuePage } from './pages/knowledge/DiscoveryQueuePage';
import { CurationChatPage } from './pages/knowledge/CurationChatPage';
import { KnowledgeAnalyticsPage } from './pages/knowledge/KnowledgeAnalyticsPage';
import { KnowledgeSearchPage } from './pages/knowledge/KnowledgeSearchPage';
import { KnowledgeSettingsPage } from './pages/knowledge/KnowledgeSettingsPage';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Dashboard routes */}
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

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
};

export default App;
EOF

# Step 10: Create package.json merge script
print_status "Creating package.json merge script..."
cat > frontend/merge-dependencies.js << 'EOF'
const fs = require('fs');

// Read both package.json files
const mainPkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const knowledgePkg = JSON.parse(fs.readFileSync('knowledge-admin/package.json', 'utf8'));

// Dependencies to add from knowledge-admin
const newDependencies = {
  '@hookform/resolvers': '^5.0.1',
  'cmdk': '^1.1.1',
  'date-fns': '^4.1.0',
  'embla-carousel-react': '^8.6.0',
  'framer-motion': '^12.15.0',
  'react-hook-form': '^7.56.3',
  'react-resizable-panels': '^3.0.2',
  'sonner': '^2.0.3',
  'vaul': '^1.1.2',
  'zod': '^3.24.4'
};

// Merge dependencies
Object.entries(newDependencies).forEach(([key, value]) => {
  if (!mainPkg.dependencies[key]) {
    mainPkg.dependencies[key] = value;
  }
});

// Update lucide-react to latest version
mainPkg.dependencies['lucide-react'] = '^0.510.0';

// Write updated package.json
fs.writeFileSync('package.json', JSON.stringify(mainPkg, null, 2));
console.log('✓ Dependencies merged successfully');
EOF

# Run the merge script
cd frontend && node merge-dependencies.js && cd ..

# Step 11: Clean up temporary files
print_status "Cleaning up temporary files..."
rm -f frontend/temp-*.jsx
rm -f frontend/extract-components.js
rm -f frontend/merge-dependencies.js

# Step 12: Create migration summary
print_status "Creating migration summary..."
cat > MIGRATION_SUMMARY.md << EOF
# Frontend Consolidation Migration Summary

Date: $(date)

## Completed Steps

1. ✅ Created backup: frontend-backup-${BACKUP_DATE}
2. ✅ Created directory structure for knowledge components
3. ✅ Created TypeScript type definitions
4. ✅ Extracted components from knowledge-admin App.jsx
5. ✅ Copied UI components to knowledge namespace
6. ✅ Created Knowledge Layout component
7. ✅ Created API integration layer
8. ✅ Updated App.tsx with new routes
9. ✅ Merged package.json dependencies

## Next Steps

1. Install new dependencies:
   \`\`\`bash
   cd frontend && npm install
   \`\`\`

2. Convert extracted JSX components to TypeScript manually or using the helper

3. Test the integrated application

4. Remove knowledge-admin directory after successful testing

## Files Created/Modified

- frontend/src/types/knowledge.ts
- frontend/src/components/knowledge/KnowledgeLayout.tsx
- frontend/src/services/knowledgeAPI.ts
- frontend/src/App-updated.tsx (review and replace App.tsx)
- frontend/package.json (dependencies updated)

## Backup Location

- frontend-backup-${BACKUP_DATE}
EOF

print_status "Migration script completed!"
print_warning "Please review MIGRATION_SUMMARY.md for next steps"
print_warning "Remember to install new dependencies: cd frontend && npm install"
