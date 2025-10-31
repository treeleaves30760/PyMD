/**
 * Package API client
 */

import axios from 'axios';
import type {
  Package,
  PackageInstallRequest,
  PackageInstallResponse,
  PackageListResponse,
  RequirementsImportRequest,
  RequirementsImportResponse,
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
 * Package API methods
 */
export const packageApi = {
  /**
   * List packages in an environment
   */
  list: async (environmentId: string): Promise<PackageListResponse> => {
    const response = await apiClient.get<PackageListResponse>(
      `/environments/${environmentId}/packages`
    );
    return response.data;
  },

  /**
   * Install packages in an environment
   */
  install: async (
    environmentId: string,
    packages: string[]
  ): Promise<PackageInstallResponse> => {
    const response = await apiClient.post<PackageInstallResponse>(
      `/environments/${environmentId}/packages`,
      { packages } as PackageInstallRequest
    );
    return response.data;
  },

  /**
   * Uninstall a package from an environment
   */
  uninstall: async (environmentId: string, packageName: string): Promise<void> => {
    await apiClient.delete(`/environments/${environmentId}/packages/${packageName}`);
  },

  /**
   * Get information about a specific package
   */
  get: async (environmentId: string, packageName: string): Promise<Package> => {
    const response = await apiClient.get<Package>(
      `/environments/${environmentId}/packages/${packageName}`
    );
    return response.data;
  },

  /**
   * Import packages from requirements.txt
   */
  importRequirements: async (
    environmentId: string,
    requirements: string
  ): Promise<RequirementsImportResponse> => {
    const response = await apiClient.post<RequirementsImportResponse>(
      `/environments/${environmentId}/packages/import`,
      { requirements } as RequirementsImportRequest
    );
    return response.data;
  },
};

export default apiClient;
