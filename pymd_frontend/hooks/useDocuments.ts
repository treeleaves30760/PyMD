/**
 * React Query hooks for documents
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type {
  Document,
  DocumentCreate,
  DocumentUpdate,
  DocumentListParams,
} from '@/types/document';
import { documentApi, renderApi } from '@/lib/api/documents';

/**
 * Query keys
 */
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (params?: DocumentListParams) => [...documentKeys.lists(), params] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

/**
 * List documents with pagination
 */
export function useDocuments(params?: DocumentListParams) {
  return useQuery({
    queryKey: documentKeys.list(params),
    queryFn: () => documentApi.list(params),
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Get a single document
 */
export function useDocument(id: string, enabled = true) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentApi.get(id),
    enabled: enabled && !!id,
    staleTime: 30000,
  });
}

/**
 * Create a new document
 */
export function useCreateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentCreate) => documentApi.create(data),
    onSuccess: () => {
      // Invalidate and refetch document lists
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

/**
 * Update a document
 */
export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      documentApi.update(id, data),
    onSuccess: (updatedDoc) => {
      // Update the document in cache
      queryClient.setQueryData(documentKeys.detail(updatedDoc.id), updatedDoc);
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

/**
 * Delete a document
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentApi.delete(id),
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: documentKeys.detail(id) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

/**
 * Duplicate a document
 */
export function useDuplicateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentApi.duplicate(id),
    onSuccess: () => {
      // Invalidate lists to show the new document
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

/**
 * Render document content (for preview)
 */
export function useRenderPreview() {
  return useMutation({
    mutationFn: ({ content, format = 'html' }: { content: string; format?: 'html' | 'markdown' }) =>
      renderApi.preview({ content, format }),
  });
}

/**
 * Validate PyMD syntax
 */
export function useValidateSyntax() {
  return useMutation({
    mutationFn: (content: string) => renderApi.validate(content),
  });
}

/**
 * Render a stored document
 */
export function useRenderDocument(
  id: string,
  format: 'html' | 'markdown' = 'html',
  enabled = true
) {
  return useQuery({
    queryKey: ['render', id, format],
    queryFn: () => renderApi.renderDocument(id, format),
    enabled: enabled && !!id,
    staleTime: 60000, // 1 minute - renders are cached
  });
}

/**
 * Export and download a document
 */
export function useExportDocument() {
  return useMutation({
    mutationFn: ({
      id,
      title,
      format = 'html',
    }: {
      id: string;
      title: string;
      format?: 'html' | 'markdown' | 'json';
    }) => renderApi.downloadExport(id, title, format),
  });
}
