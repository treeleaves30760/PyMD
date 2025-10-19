/**
 * Document API client
 */

import axios from 'axios';
import type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentListResponse,
  DocumentListParams,
  RenderRequest,
  RenderResponse,
  ValidationResponse,
} from '@/types/document';

// Use Next.js API proxy for authenticated requests
const API_URL = '/api/backend';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Send cookies with requests
});

/**
 * Document API methods
 */
export const documentApi = {
  /**
   * List documents with pagination and search
   */
  list: async (params?: DocumentListParams): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/documents', {
      params,
    });
    return response.data;
  },

  /**
   * Create a new document
   */
  create: async (data: DocumentCreate): Promise<Document> => {
    const response = await apiClient.post<Document>('/documents', data);
    return response.data;
  },

  /**
   * Get a single document by ID
   */
  get: async (id: string): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${id}`);
    return response.data;
  },

  /**
   * Update a document
   */
  update: async (id: string, data: DocumentUpdate): Promise<Document> => {
    const response = await apiClient.patch<Document>(`/documents/${id}`, data);
    return response.data;
  },

  /**
   * Delete a document (soft delete)
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/documents/${id}`);
  },

  /**
   * Duplicate a document
   */
  duplicate: async (id: string): Promise<Document> => {
    const response = await apiClient.post<Document>(`/documents/${id}/duplicate`);
    return response.data;
  },

  /**
   * Search documents (deprecated - use list with search param)
   */
  search: async (query: string, page = 1, page_size = 20): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/documents/search', {
      params: { q: query, page, page_size },
    });
    return response.data;
  },
};

/**
 * Render API methods
 */
export const renderApi = {
  /**
   * Render PyMD content
   */
  render: async (data: RenderRequest): Promise<RenderResponse> => {
    const response = await apiClient.post<RenderResponse>('/render', data);
    return response.data;
  },

  /**
   * Quick preview rendering (optimized for live preview)
   */
  preview: async (data: RenderRequest): Promise<RenderResponse> => {
    const response = await apiClient.post<RenderResponse>('/render/preview', data);
    return response.data;
  },

  /**
   * Validate PyMD syntax
   */
  validate: async (content: string): Promise<ValidationResponse> => {
    const response = await apiClient.post<ValidationResponse>('/render/validate', {
      content,
    });
    return response.data;
  },

  /**
   * Render a stored document
   */
  renderDocument: async (
    id: string,
    format: 'html' | 'markdown' = 'html',
    use_cache = true
  ): Promise<RenderResponse> => {
    const response = await apiClient.get<RenderResponse>(`/render/documents/${id}`, {
      params: { format, use_cache },
    });
    return response.data;
  },

  /**
   * Export a document
   */
  export: async (id: string, format: 'html' | 'markdown' | 'json' = 'html'): Promise<Blob> => {
    const response = await apiClient.get(`/render/documents/${id}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Download exported document
   */
  downloadExport: async (
    id: string,
    title: string,
    format: 'html' | 'markdown' | 'json' = 'html'
  ): Promise<void> => {
    const blob = await renderApi.export(id, format);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;

    const extension = format === 'html' ? 'html' : format === 'markdown' ? 'md' : 'json';
    link.download = `${title}.${extension}`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};

export default apiClient;
