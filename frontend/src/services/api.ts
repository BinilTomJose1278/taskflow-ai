import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  file_hash: string;
  status: string;
  processing_progress: number;
  extracted_text?: string;
  ai_summary?: string;
  ai_insights: Record<string, any>;
  confidence_score?: number;
  organization_id: number;
  uploaded_by: number;
  created_at: string;
  updated_at?: string;
  title?: string;
  description?: string;
  category?: string;
  tags: string[];
}

export interface DocumentUploadResponse {
  message: string;
  filename: string;
  size: number;
  title: string;
  description: string | null;
}

export interface DocumentsResponse {
  documents: Document[];
  total: number;
}

export interface AnalyticsResponse {
  total_documents: number;
  processed_documents: number;
  processing_rate: number;
  average_processing_time: number;
  status: string;
}

export const documentApi = {
  // Upload a document
  uploadDocument: async (
    file: File,
    title?: string,
    description?: string
  ): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (description) formData.append('description', description);

    const response = await api.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get all documents
  getDocuments: async (): Promise<DocumentsResponse> => {
    const response = await api.get('/api/v1/documents/');
    return response.data;
  },

  // Get analytics overview
  getAnalytics: async (): Promise<AnalyticsResponse> => {
    const response = await api.get('/api/v1/analytics/overview');
    return response.data;
  },

  // Document Analysis
  analyzeDocument: async (documentId: string, analysisType: string = 'all'): Promise<any> => {
    const response = await api.post(`/api/v1/documents/${documentId}/analyze?analysis_type=${analysisType}`);
    return response.data;
  },

  getDocumentAnalysis: async (documentId: number): Promise<any> => {
    const response = await api.get(`/api/v1/documents/${documentId}/analysis`);
    return response.data;
  },

  getDocumentReport: async (documentId: number, format: string = 'json'): Promise<any> => {
    const response = await api.get(`/api/v1/documents/${documentId}/report?format=${format}`);
    return response.data;
  },

  // Get single document
  getDocument: async (documentId: number): Promise<Document> => {
    const response = await api.get(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  // Health check
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
