import React from 'react';
import { Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const KnowledgeSearchPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Advanced Search</h2>
        <p className="text-gray-600 mt-1">
          Powerful search capabilities for your knowledge base
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5 text-purple-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Advanced search features will include:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li>• Semantic search with AI understanding</li>
            <li>• Filter by date, author, and tags</li>
            <li>• Search within specific content types</li>
            <li>• Save and share search queries</li>
            <li>• Export search results</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
