// src/pages/KnowledgeDashboard.jsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

// Mock Data
const ingestionJobs = [
  { id: 'job_123', source: 'Gong Sync', document: 'Call with Acme Corp', status: 'Success', timestamp: '2024-07-21 10:00 AM' },
  { id: 'job_124', source: 'File Upload', document: 'Q3_Financials.pdf', status: 'Processing', timestamp: '2024-07-21 10:05 AM' },
  { id: 'job_125', source: 'HubSpot Sync', document: 'New Contacts Q3', status: 'Queued', timestamp: '2024-07-21 10:06 AM' },
  { id: 'job_122', source: 'File Upload', document: 'competitor_analysis.docx', status: 'Failed', timestamp: '2024-07-21 09:55 AM' },
];

const KnowledgeDashboard = () => {
  return (
    <div className="p-4 md:p-8 bg-gray-50 min-h-screen">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Knowledge Admin Panel</h1>
        <p className="text-gray-600">Manage and monitor the AI's knowledge base.</p>
      </header>

      <div className="grid gap-8 md:grid-cols-3">
        {/* Control Panel */}
        <div className="md:col-span-1 flex flex-col gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Manual Ingestion</CardTitle>
              <CardDescription>Upload a document to the knowledge base.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input type="file" />
              <Button className="w-full">Upload and Ingest</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Data Source Sync</CardTitle>
              <CardDescription>Trigger a full sync from a connected data source.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col space-y-2">
              <Button variant="outline">Sync Gong Calls</Button>
              <Button variant="outline">Sync HubSpot CRM</Button>
              <Button variant="outline">Sync Snowflake Tables</Button>
            </CardContent>
          </Card>
        </div>

        {/* Ingestion Status */}
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Ingestion Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Source</TableHead>
                    <TableHead>Document</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {ingestionJobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.source}</TableCell>
                      <TableCell className="font-medium">{job.document}</TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          job.status === 'Success' ? 'bg-green-100 text-green-800' :
                          job.status === 'Processing' ? 'bg-blue-100 text-blue-800' :
                          job.status === 'Failed' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {job.status}
                        </span>
                      </TableCell>
                      <TableCell>{job.timestamp}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeDashboard;
