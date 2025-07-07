import React from 'react';
import { Settings } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const KnowledgeSettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Knowledge Base Settings</h2>
        <p className="text-gray-600 mt-1">
          Configure your knowledge base preferences
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-gray-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Settings will allow you to configure:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li>• AI model preferences</li>
            <li>• Auto-tagging rules</li>
            <li>• Content type definitions</li>
            <li>• Access permissions</li>
            <li>• Integration settings</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
