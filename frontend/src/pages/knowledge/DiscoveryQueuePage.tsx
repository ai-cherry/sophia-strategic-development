import React from 'react';
import { Lightbulb } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const DiscoveryQueuePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Discovery Queue</h2>
        <p className="text-gray-600 mt-1">
          AI-powered insights and suggestions for your knowledge base
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            The Discovery Queue will show proactive insights discovered by AI, including:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li>• New competitor information</li>
            <li>• Product gaps and opportunities</li>
            <li>• Emerging use cases</li>
            <li>• Content suggestions</li>
            <li>• Knowledge gaps to fill</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
