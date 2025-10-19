/**
 * Document type definitions
 */

export interface Document {
  id: string;
  owner_id: string;
  title: string;
  content: string;
  render_format: 'html' | 'markdown';
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  last_accessed_at: string;
}

export interface DocumentCreate {
  title: string;
  content?: string;
  render_format?: 'html' | 'markdown';
}

export interface DocumentUpdate {
  title?: string;
  content?: string;
  render_format?: 'html' | 'markdown';
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface DocumentListParams {
  page?: number;
  page_size?: number;
  search?: string;
  sort_by?: 'created_at' | 'updated_at' | 'title';
  sort_order?: 'asc' | 'desc';
}

export interface RenderRequest {
  content: string;
  format?: 'html' | 'markdown';
}

export interface RenderResponse {
  rendered: string;
  cached: boolean;
}

export interface ValidationError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResponse {
  valid: boolean;
  errors: ValidationError[];
}
