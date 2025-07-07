import React from 'react';
import { FileText, Calendar, User, Tag } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Document, ContentType } from '@/types/knowledge';

interface DocumentCardProps {
  document: Document;
  contentTypes: ContentType[];
  onClick: () => void;
}

export const DocumentCard: React.FC<DocumentCardProps> = ({ document, contentTypes, onClick }) => {
  const contentType = contentTypes.find(ct => ct.value === document.contentType);

  const getStatusColor = (status: Document['status']) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'published': return 'bg-green-100 text-green-800';
      case 'archived': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <Card
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <FileText className="w-5 h-5 text-gray-400" />
          <Badge className={getStatusColor(document.status)} variant="secondary">
            {document.status}
          </Badge>
        </div>
        <CardTitle className="text-lg line-clamp-2">{document.title}</CardTitle>
      </CardHeader>

      <CardContent className="space-y-3">
        <p className="text-sm text-gray-600 line-clamp-3">{document.content}</p>

        <div className="flex items-center gap-2">
          {contentType && (
            <Badge className={contentType.color} variant="secondary">
              {contentType.label}
            </Badge>
          )}
          <Badge variant="outline" className="text-xs">
            v{document.version}
          </Badge>
        </div>

        <div className="flex flex-wrap gap-1">
          {document.tags.map((tag, index) => (
            <span key={index} className="inline-flex items-center text-xs text-gray-500">
              <Tag className="w-3 h-3 mr-1" />
              {tag}
            </span>
          ))}
        </div>

        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <User className="w-3 h-3" />
            {document.createdBy}
          </div>
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            {formatDate(document.updatedAt)}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
