import React from 'react';
import { MessageSquare } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const CurationChatPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Curation Chat</h2>
        <p className="text-gray-600 mt-1">
          Interactive AI assistant for knowledge base curation
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-blue-500" />
            Coming Soon
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            The Curation Chat will provide an AI assistant to help you:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-gray-600">
            <li>• Ask questions about your knowledge base</li>
            <li>• Get suggestions for improving content</li>
            <li>• Identify gaps and inconsistencies</li>
            <li>• Generate new content based on existing knowledge</li>
            <li>• Provide feedback to improve AI responses</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
