import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Save, PlusCircle, Trash2 } from 'lucide-react';

const WorkflowDesignerTab = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Visual Workflow Designer</CardTitle>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm"><PlusCircle className="h-4 w-4 mr-2" /> New Agent</Button>
              <Button variant="outline" size="sm"><Save className="h-4 w-4 mr-2" /> Save Workflow</Button>
              <Button size="sm"><Play className="h-4 w-4 mr-2" /> Run Workflow</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex h-[60vh] border-2 border-dashed rounded-lg">
            <div className="w-1/4 p-4 border-r bg-gray-50">
              <h3 className="font-semibold mb-4">Agent Palette</h3>
              <div className="space-y-2">
                <div className="p-2 border rounded-md bg-white cursor-pointer hover:bg-gray-100">Development Group</div>
                <div className="p-2 border rounded-md bg-white cursor-pointer hover:bg-gray-100">BI Group</div>
                <div className="p-2 border rounded-md bg-white cursor-pointer hover:bg-gray-100">Supervisor</div>
              </div>
            </div>
            <div className="w-3/4 p-4">
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Drag and drop agents from the palette to build your workflow.</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default WorkflowDesignerTab;
