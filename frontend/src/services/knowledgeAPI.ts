import apiClient from './apiClient';
import { Document, ProactiveInsight, KnowledgeStats } from '@/types/knowledge';

export const knowledgeAPI = {
  documents: {
    list: () => apiClient.get<Document[]>('/api/v1/knowledge/documents'),
    get: (id: string) => apiClient.get<Document>(`/api/v1/knowledge/documents/${id}`),
    create: (data: Partial<Document>) => apiClient.post<Document>('/api/v1/knowledge/documents', data),
    update: (id: string, data: Partial<Document>) => apiClient.put<Document>(`/api/v1/knowledge/documents/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/v1/knowledge/documents/${id}`),
    search: (query: string) => apiClient.get<Document[]>(`/api/v1/knowledge/documents/search?q=${query}`)
  },

  insights: {
    list: () => apiClient.get<ProactiveInsight[]>('/api/v1/knowledge/insights'),
    approve: (id: string) => apiClient.post(`/api/v1/knowledge/insights/${id}/approve`),
    reject: (id: string) => apiClient.post(`/api/v1/knowledge/insights/${id}/reject`),
    edit: (id: string, data: Partial<ProactiveInsight>) => apiClient.put(`/api/v1/knowledge/insights/${id}`, data)
  },

  analytics: {
    stats: () => apiClient.get<KnowledgeStats>('/api/v1/knowledge/analytics/stats'),
    searchHistory: () => apiClient.get('/api/v1/knowledge/analytics/search-history'),
    documentActivity: () => apiClient.get('/api/v1/knowledge/analytics/document-activity')
  },

  chat: {
    sendMessage: (message: string) => apiClient.post('/api/v1/knowledge/chat', { message }),
    getHistory: () => apiClient.get('/api/v1/knowledge/chat/history'),
    provideFeedback: (messageId: string, feedback: 'positive' | 'negative', correction?: string) =>
      apiClient.post(`/api/v1/knowledge/chat/${messageId}/feedback`, { feedback, correction })
  }
};
