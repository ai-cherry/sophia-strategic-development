import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DocumentCard } from '@/components/knowledge/DocumentCard';
import { DocumentEditor } from '@/components/knowledge/DocumentEditor';
import { knowledgeAPI } from '@/services/knowledgeAPI';
import { Document, ContentType } from '@/types/knowledge';

const contentTypes: ContentType[] = [
  { value: 'product', label: 'Product Info', color: 'bg-blue-100 text-blue-800' },
  { value: 'competitor', label: 'Competitor Intel', color: 'bg-red-100 text-red-800' },
  { value: 'market', label: 'Market Analysis', color: 'bg-green-100 text-green-800' },
  { value: 'technical', label: 'Technical Docs', color: 'bg-purple-100 text-purple-800' },
  { value: 'sales', label: 'Sales Material', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'other', label: 'Other', color: 'bg-gray-100 text-gray-800' },
];

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    filterDocuments();
  }, [documents, searchQuery, filterType, filterStatus]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await knowledgeAPI.documents.list();
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterDocuments = () => {
    let filtered = [...documents];

    if (searchQuery) {
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(doc => doc.contentType === filterType);
    }

    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => doc.status === filterStatus);
    }

    setFilteredDocuments(filtered);
  };

  const handleSave = async (document: Partial<Document>) => {
    try {
      if (selectedDocument) {
        await knowledgeAPI.documents.update(selectedDocument.id, document);
      } else {
        await knowledgeAPI.documents.create(document);
      }
      loadDocuments();
      setSelectedDocument(null);
      setIsCreating(false);
    } catch (error) {
      console.error('Failed to save document:', error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await knowledgeAPI.documents.delete(id);
      loadDocuments();
      setSelectedDocument(null);
    } catch (error) {
      console.error('Failed to delete document:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading documents...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Knowledge Documents</h2>
          <p className="text-gray-600 mt-1">
            {filteredDocuments.length} of {documents.length} documents
          </p>
        </div>
        <Button onClick={() => setIsCreating(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Document
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 bg-white p-4 rounded-lg shadow-sm">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Content Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {contentTypes.map(type => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="review">In Review</SelectItem>
            <SelectItem value="published">Published</SelectItem>
            <SelectItem value="archived">Archived</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Document Grid or Editor */}
      {selectedDocument || isCreating ? (
        <DocumentEditor
          document={selectedDocument}
          contentTypes={contentTypes}
          onSave={handleSave}
          onCancel={() => {
            setSelectedDocument(null);
            setIsCreating(false);
          }}
          onDelete={selectedDocument ? () => handleDelete(selectedDocument.id) : undefined}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map(doc => (
            <DocumentCard
              key={doc.id}
              document={doc}
              contentTypes={contentTypes}
              onClick={() => setSelectedDocument(doc)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
