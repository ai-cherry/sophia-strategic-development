import React, { useState, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, X, File, FileSpreadsheet } from 'lucide-react';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  extractedText?: string;
  metadata?: {
    category: string;
    tags: string[];
    description: string;
  };
  error?: string;
}

interface KBDocumentUploadProps {
  onFileProcessed?: (file: UploadedFile) => void;
  onError?: (error: string) => void;
}

const KBDocumentUpload: React.FC<KBDocumentUploadProps> = ({ onFileProcessed, onError }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedTypes = {
    'application/pdf': { icon: FileText, label: 'PDF' },
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': { icon: FileText, label: 'DOCX' },
    'text/plain': { icon: File, label: 'TXT' },
    'application/json': { icon: File, label: 'JSON' },
    'text/csv': { icon: FileSpreadsheet, label: 'CSV' }
  };

  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      handleFiles(selectedFiles);
    }
  }, []);

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize) {
      return `File size exceeds 10MB limit`;
    }
    
    if (!Object.keys(supportedTypes).includes(file.type)) {
      return `Unsupported file type: ${file.type}`;
    }
    
    return null;
  };

  const handleFiles = async (fileList: File[]) => {
    setIsUploading(true);
    
    for (const file of fileList) {
      const validationError = validateFile(file);
      if (validationError) {
        onError?.(validationError);
        continue;
      }

      const uploadedFile: UploadedFile = {
        id: `${Date.now()}_${Math.random()}`,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        progress: 0
      };

      setFiles(prev => [...prev, uploadedFile]);

      try {
        await processFile(file, uploadedFile.id);
      } catch (error) {
        updateFileStatus(uploadedFile.id, 'error', 0, undefined, error.message);
        onError?.(error.message);
      }
    }
    
    setIsUploading(false);
  };

  const processFile = async (file: File, fileId: string) => {
    // Simulate upload progress
    for (let progress = 0; progress <= 100; progress += 10) {
      updateFileStatus(fileId, 'uploading', progress);
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    updateFileStatus(fileId, 'processing', 100);
    await new Promise(resolve => setTimeout(resolve, 2000));

    let extractedText = '';
    try {
      if (file.type === 'text/plain') {
        extractedText = await file.text();
      } else if (file.type === 'application/json') {
        const jsonContent = await file.text();
        extractedText = JSON.stringify(JSON.parse(jsonContent), null, 2);
      } else {
        extractedText = `Extracted text from ${file.name}. This would contain the actual document content.`;
      }

      updateFileStatus(fileId, 'completed', 100, extractedText);
      
      const processedFile = files.find(f => f.id === fileId);
      if (processedFile) {
        onFileProcessed?.(processedFile);
      }

    } catch (error) {
      updateFileStatus(fileId, 'error', 0, undefined, `Failed to extract text: ${error.message}`);
    }
  };

  const updateFileStatus = (
    fileId: string, 
    status: UploadedFile['status'], 
    progress: number, 
    extractedText?: string, 
    error?: string
  ) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, status, progress, extractedText, error }
        : file
    ));
  };

  const updateFileMetadata = (fileId: string, metadata: UploadedFile['metadata']) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, metadata }
        : file
    ));
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const getFileIcon = (fileType: string) => {
    const typeInfo = supportedTypes[fileType];
    return typeInfo ? typeInfo.icon : File;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Knowledge Base Documents
          </CardTitle>
          <CardDescription>
            Upload PDFs, Word documents, text files, and other documents to add to the knowledge base.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              Drop files here or click to browse
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supported formats: PDF, DOCX, TXT, JSON, CSV
            </p>
            <Button 
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              Select Files
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.json,.csv"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Files ({files.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {files.map((file) => {
              const IconComponent = getFileIcon(file.type);
              
              return (
                <div key={file.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <IconComponent className="h-8 w-8 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(file.size)} • {supportedTypes[file.type]?.label || 'Unknown'}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>

                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize">{file.status}...</span>
                        <span>{file.progress}%</span>
                      </div>
                      <Progress value={file.progress} className="h-2" />
                    </div>
                  )}

                  {file.status === 'error' && file.error && (
                    <Alert className="mb-3">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription>{file.error}</AlertDescription>
                    </Alert>
                  )}

                  {file.status === 'completed' && (
                    <div className="space-y-3 pt-3 border-t">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <Label>Category</Label>
                          <Select 
                            onValueChange={(value) => 
                              updateFileMetadata(file.id, { 
                                ...file.metadata, 
                                category: value 
                              })
                            }
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="policies">Policies & Procedures</SelectItem>
                              <SelectItem value="technical">Technical Documentation</SelectItem>
                              <SelectItem value="training">Training Materials</SelectItem>
                              <SelectItem value="customer">Customer Information</SelectItem>
                              <SelectItem value="product">Product Documentation</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Tags (comma-separated)</Label>
                          <Input
                            placeholder="e.g., onboarding, security, api"
                            onChange={(e) => 
                              updateFileMetadata(file.id, { 
                                ...file.metadata, 
                                tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                              })
                            }
                          />
                        </div>
                      </div>
                      <div>
                        <Label>Description</Label>
                        <Textarea
                          placeholder="Brief description of the document content..."
                          rows={2}
                          onChange={(e) => 
                            updateFileMetadata(file.id, { 
                              ...file.metadata, 
                              description: e.target.value 
                            })
                          }
                        />
                      </div>
                      
                      {file.extractedText && (
                        <div>
                          <Label>Extracted Text Preview</Label>
                          <div className="mt-1 p-3 bg-gray-50 rounded border text-sm max-h-32 overflow-y-auto">
                            {file.extractedText.substring(0, 500)}
                            {file.extractedText.length > 500 && '...'}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default KBDocumentUpload;
