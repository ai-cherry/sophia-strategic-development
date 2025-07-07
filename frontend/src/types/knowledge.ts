export interface Document {
  id: string;
  title: string;
  content: string;
  contentType: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  tags: string[];
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  version: number;
}

export interface ProactiveInsight {
  id: string;
  type: 'new_competitor' | 'product_gap' | 'use_case';
  source: string;
  sourceUrl: string;
  insight: string;
  question: string;
  timestamp: string;
  status: 'pending' | 'approved' | 'rejected';
  confidence: number;
  context: string;
}

export interface KnowledgeStats {
  totalDocuments: number;
  publishedDocuments: number;
  draftDocuments: number;
  totalSearches: number;
  avgResponseTime: string;
  knowledgeCoverage: number;
}

export interface ContentType {
  value: string;
  label: string;
  color: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: 'positive' | 'negative';
  correction?: string;
}
