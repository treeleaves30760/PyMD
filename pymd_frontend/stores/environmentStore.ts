/**
 * Environment Store
 *
 * Manages user environments and packages state
 */

import { create } from 'zustand'
import type {
  Environment,
  EnvironmentCreate,
  EnvironmentStats,
  Package,
  PackageInstallResponse,
  RequirementsImportResponse,
} from '@/types/environment'
import { environmentApi } from '@/lib/api/environments'
import { packageApi } from '@/lib/api/packages'

interface EnvironmentState {
  // Environment State
  environments: Environment[]
  activeEnvironmentId: string | null
  stats: EnvironmentStats | null
  isLoadingEnvironments: boolean
  environmentsError: string | null

  // Package State
  packages: Package[]
  isLoadingPackages: boolean
  packagesError: string | null

  // Installation State
  isInstalling: boolean
  installProgress: number
  installError: string | null
  installResult: PackageInstallResponse | null

  // Environment Actions
  loadEnvironments: () => Promise<void>
  loadStats: () => Promise<void>
  createEnvironment: (name: string, pythonVersion?: string) => Promise<Environment | null>
  deleteEnvironment: (id: string) => Promise<boolean>
  resetEnvironment: (id: string) => Promise<boolean>
  setActiveEnvironment: (id: string) => void
  refreshActiveEnvironment: () => Promise<void>

  // Package Actions
  loadPackages: (envId: string) => Promise<void>
  installPackages: (envId: string, packages: string[]) => Promise<PackageInstallResponse | null>
  uninstallPackage: (envId: string, packageName: string) => Promise<boolean>
  importRequirements: (envId: string, requirements: string) => Promise<RequirementsImportResponse | null>

  // UI Helpers
  clearInstallResult: () => void
  reset: () => void
}

const initialState = {
  environments: [],
  activeEnvironmentId: null,
  stats: null,
  isLoadingEnvironments: false,
  environmentsError: null,
  packages: [],
  isLoadingPackages: false,
  packagesError: null,
  isInstalling: false,
  installProgress: 0,
  installError: null,
  installResult: null,
}

export const useEnvironmentStore = create<EnvironmentState>((set, get) => ({
  ...initialState,

  // Load all environments
  loadEnvironments: async () => {
    set({ isLoadingEnvironments: true, environmentsError: null })
    try {
      const response = await environmentApi.list()
      const envs = response.environments

      // Set first environment as active if none selected
      const currentActive = get().activeEnvironmentId
      const newActive = currentActive || (envs.length > 0 ? envs[0].id : null)

      set({
        environments: envs,
        activeEnvironmentId: newActive,
        isLoadingEnvironments: false,
      })

      // Load packages for active environment
      if (newActive) {
        get().loadPackages(newActive)
      }
    } catch (error: any) {
      console.error('Failed to load environments:', error)
      set({
        environmentsError: error.response?.data?.detail || error.message || 'Failed to load environments',
        isLoadingEnvironments: false,
      })
    }
  },

  // Load environment statistics
  loadStats: async () => {
    try {
      const stats = await environmentApi.getStats()
      set({ stats })
    } catch (error: any) {
      console.error('Failed to load stats:', error)
    }
  },

  // Create a new environment
  createEnvironment: async (name: string, pythonVersion = '3.11') => {
    set({ isLoadingEnvironments: true, environmentsError: null })
    try {
      const newEnv = await environmentApi.create({ name, python_version: pythonVersion })

      // Add to list and set as active
      set((state) => ({
        environments: [...state.environments, newEnv],
        activeEnvironmentId: newEnv.id,
        isLoadingEnvironments: false,
      }))

      // Reload stats
      get().loadStats()

      return newEnv
    } catch (error: any) {
      console.error('Failed to create environment:', error)
      set({
        environmentsError: error.response?.data?.detail || error.message || 'Failed to create environment',
        isLoadingEnvironments: false,
      })
      return null
    }
  },

  // Delete an environment
  deleteEnvironment: async (id: string) => {
    try {
      await environmentApi.delete(id)

      const state = get()
      const newEnvs = state.environments.filter((env) => env.id !== id)

      // If deleted env was active, select another
      let newActive = state.activeEnvironmentId
      if (state.activeEnvironmentId === id) {
        newActive = newEnvs.length > 0 ? newEnvs[0].id : null
      }

      set({
        environments: newEnvs,
        activeEnvironmentId: newActive,
        packages: newActive ? state.packages : [],
      })

      // Reload stats
      get().loadStats()

      // Load packages for new active environment
      if (newActive) {
        get().loadPackages(newActive)
      }

      return true
    } catch (error: any) {
      console.error('Failed to delete environment:', error)
      set({
        environmentsError: error.response?.data?.detail || error.message || 'Failed to delete environment',
      })
      return false
    }
  },

  // Reset an environment (clear packages)
  resetEnvironment: async (id: string) => {
    try {
      const updatedEnv = await environmentApi.reset(id)

      // Update environment in list
      set((state) => ({
        environments: state.environments.map((env) =>
          env.id === id ? updatedEnv : env
        ),
        packages: state.activeEnvironmentId === id ? [] : state.packages,
      }))

      // Reload stats
      get().loadStats()

      return true
    } catch (error: any) {
      console.error('Failed to reset environment:', error)
      set({
        environmentsError: error.response?.data?.detail || error.message || 'Failed to reset environment',
      })
      return false
    }
  },

  // Set active environment
  setActiveEnvironment: (id: string) => {
    set({ activeEnvironmentId: id, packages: [] })
    get().loadPackages(id)
  },

  // Refresh active environment data
  refreshActiveEnvironment: async () => {
    const activeId = get().activeEnvironmentId
    if (!activeId) return

    try {
      const updatedEnv = await environmentApi.get(activeId)
      set((state) => ({
        environments: state.environments.map((env) =>
          env.id === activeId ? updatedEnv : env
        ),
      }))
    } catch (error: any) {
      console.error('Failed to refresh environment:', error)
    }
  },

  // Load packages for an environment
  loadPackages: async (envId: string) => {
    set({ isLoadingPackages: true, packagesError: null })
    try {
      const response = await packageApi.list(envId)
      set({
        packages: response.packages,
        isLoadingPackages: false,
      })
    } catch (error: any) {
      console.error('Failed to load packages:', error)
      set({
        packagesError: error.response?.data?.detail || error.message || 'Failed to load packages',
        isLoadingPackages: false,
      })
    }
  },

  // Install packages
  installPackages: async (envId: string, packages: string[]) => {
    set({
      isInstalling: true,
      installError: null,
      installResult: null,
      installProgress: 0,
    })

    try {
      const result = await packageApi.install(envId, packages)

      set({
        installResult: result,
        isInstalling: false,
        installProgress: 100,
      })

      // Reload packages and environment
      await get().loadPackages(envId)
      await get().refreshActiveEnvironment()
      await get().loadStats()

      return result
    } catch (error: any) {
      console.error('Failed to install packages:', error)
      set({
        installError: error.response?.data?.detail || error.message || 'Failed to install packages',
        isInstalling: false,
        installProgress: 0,
      })
      return null
    }
  },

  // Uninstall a package
  uninstallPackage: async (envId: string, packageName: string) => {
    try {
      await packageApi.uninstall(envId, packageName)

      // Remove package from list
      set((state) => ({
        packages: state.packages.filter((pkg) => pkg.package_name !== packageName),
      }))

      // Reload environment and stats
      await get().refreshActiveEnvironment()
      await get().loadStats()

      return true
    } catch (error: any) {
      console.error('Failed to uninstall package:', error)
      set({
        packagesError: error.response?.data?.detail || error.message || 'Failed to uninstall package',
      })
      return false
    }
  },

  // Import requirements.txt
  importRequirements: async (envId: string, requirements: string) => {
    set({
      isInstalling: true,
      installError: null,
      installResult: null,
      installProgress: 0,
    })

    try {
      const result = await packageApi.importRequirements(envId, requirements)

      // Convert to PackageInstallResponse format
      const installResult: PackageInstallResponse = {
        success_count: result.success_count,
        fail_count: result.fail_count,
        successful: result.successful,
        failed: result.failed,
      }

      set({
        installResult,
        isInstalling: false,
        installProgress: 100,
      })

      // Reload packages and environment
      await get().loadPackages(envId)
      await get().refreshActiveEnvironment()
      await get().loadStats()

      return result
    } catch (error: any) {
      console.error('Failed to import requirements:', error)
      set({
        installError: error.response?.data?.detail || error.message || 'Failed to import requirements',
        isInstalling: false,
        installProgress: 0,
      })
      return null
    }
  },

  // Clear install result
  clearInstallResult: () => {
    set({
      installResult: null,
      installError: null,
      installProgress: 0,
    })
  },

  // Reset store
  reset: () => set(initialState),
}))
