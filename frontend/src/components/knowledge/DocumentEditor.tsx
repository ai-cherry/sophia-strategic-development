import React, { useState, useEffect } from 'react';
import { Save, X, Trash2, Tag as TagIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Document, ContentType } from '@/types/knowledge';

interface DocumentEditorProps {
  document: Document | null;
  contentTypes: ContentType[];
  onSave: (document: Partial<Document>) => void;
  onCancel: () => void;
  onDelete?: () => void;
}

export const DocumentEditor: React.FC<DocumentEditorProps> = ({
  document,
  contentTypes,
  onSave,
  onCancel,
  onDelete
}) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('product');
  const [status, setStatus] = useState<Document['status']>('draft');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');

  useEffect(() => {
    if (document) {
      setTitle(document.title);
      setContent(document.content);
      setContentType(document.contentType);
      setStatus(document.status);
      setTags(document.tags);
    } else {
      // Reset for new document
      setTitle('');
      setContent('');
      setContentType('product');
      setStatus('draft');
      setTags([]);
    }
  }, [document]);

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setTags([...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSave = () => {
    const documentData: Partial<Document> = {
      title,
      content,
      contentType,
      status,
      tags,
      updatedAt: new Date().toISOString()
    };

    if (!document) {
      documentData.createdAt = new Date().toISOString();
      documentData.createdBy = 'Current User'; // Would come from auth context
      documentData.version = 1;
    } else {
      documentData.version = document.version + 1;
    }

    onSave(documentData);
  };

  const isValid = title.trim() && content.trim();

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>
            {document ? 'Edit Document' : 'Create New Document'}
          </CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onCancel}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            {document && onDelete && (
              <Button variant="destructive" onClick={onDelete}>
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            )}
            <Button onClick={handleSave} disabled={!isValid}>
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div>
          <label className="text-sm font-medium mb-2 block">Title</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter document title..."
            className="text-lg"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Content Type</label>
            <Select value={contentType} onValueChange={setContentType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {contentTypes.map(type => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">Status</label>
            <Select value={status} onValueChange={(value) => setStatus(value as Document['status'])}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="review">In Review</SelectItem>
                <SelectItem value="published">Published</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Content</label>
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter document content..."
            rows={12}
            className="font-mono text-sm"
          />
        </div>

        <div>
          <label className="text-sm font-medium mb-2 block">Tags</label>
          <div className="space-y-2">
            <div className="flex gap-2">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                placeholder="Add a tag..."
              />
              <Button type="button" variant="outline" onClick={handleAddTag}>
                <TagIcon className="w-4 h-4 mr-2" />
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => handleRemoveTag(tag)}
                >
                  {tag} ×
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {document && (
          <div className="text-sm text-gray-500 space-y-1">
            <p>Created by: {document.createdBy}</p>
            <p>Created at: {new Date(document.createdAt).toLocaleString()}</p>
            <p>Last updated: {new Date(document.updatedAt).toLocaleString()}</p>
            <p>Version: {document.version}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
