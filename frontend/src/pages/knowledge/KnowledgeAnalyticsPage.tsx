import React from 'react';
import { BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const KnowledgeAnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Knowledge Analytics</h2>
        <p className="text-gray-600 mt-1">
          Insights and metrics about your knowledge base usage
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Analytics will provide insights including:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li>• Document views and engagement</li>
            <li>• Search query analysis</li>
            <li>• Knowledge coverage metrics</li>
            <li>• User activity patterns</li>
            <li>• Content performance tracking</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
