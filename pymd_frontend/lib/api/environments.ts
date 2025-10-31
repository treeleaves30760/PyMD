/**
 * Environment API client
 */

import axios from 'axios';
import type {
  Environment,
  EnvironmentCreate,
  EnvironmentUpdate,
  EnvironmentListResponse,
  EnvironmentStats,
} from '@/types/environment';

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
 * Environment API methods
 */
export const environmentApi = {
  /**
   * List all environments for the current user
   */
  list: async (): Promise<EnvironmentListResponse> => {
    const response = await apiClient.get<EnvironmentListResponse>('/environments');
    return response.data;
  },

  /**
   * Get environment usage statistics
   */
  getStats: async (): Promise<EnvironmentStats> => {
    const response = await apiClient.get<EnvironmentStats>('/environments/stats');
    return response.data;
  },

  /**
   * Create a new environment
   */
  create: async (data: EnvironmentCreate): Promise<Environment> => {
    const response = await apiClient.post<Environment>('/environments', data);
    return response.data;
  },

  /**
   * Get a single environment by ID
   */
  get: async (id: string): Promise<Environment> => {
    const response = await apiClient.get<Environment>(`/environments/${id}`);
    return response.data;
  },

  /**
   * Update an environment
   */
  update: async (id: string, data: EnvironmentUpdate): Promise<Environment> => {
    const response = await apiClient.patch<Environment>(`/environments/${id}`, data);
    return response.data;
  },

  /**
   * Delete an environment
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/environments/${id}`);
  },

  /**
   * Reset an environment (remove all packages)
   */
  reset: async (id: string): Promise<Environment> => {
    const response = await apiClient.post<Environment>(`/environments/${id}/reset`);
    return response.data;
  },
};

export default apiClient;
