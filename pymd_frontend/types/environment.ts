/**
 * Environment and Package types
 */

export interface Environment {
  id: string
  user_id: string
  name: string
  python_version: string
  volume_name: string
  status: 'active' | 'creating' | 'error' | 'deleted'
  total_size_bytes: number
  package_count: number
  last_used_at: string | null
  created_at: string
  updated_at: string
}

export interface EnvironmentCreate {
  name: string
  python_version?: string
}

export interface EnvironmentUpdate {
  name?: string
  python_version?: string
}

export interface EnvironmentListResponse {
  environments: Environment[]
  total: number
}

export interface EnvironmentStats {
  environment_count: number
  environment_limit: number
  total_size_bytes: number
  size_limit_bytes: number
  total_packages: number
  package_limit: number
  can_create_environment: boolean
}

export interface Package {
  id: string
  environment_id: string
  package_name: string
  version: string | null
  size_bytes: number | null
  installed_at: string
}

export interface PackageInstallRequest {
  packages: string[]
}

export interface PackageInstallResponse {
  success_count: number
  fail_count: number
  successful: Array<{
    package: string
    version: string | null
    message: string
  }>
  failed: Array<{
    package: string
    version: string | null
    message: string
  }>
}

export interface PackageListResponse {
  packages: Package[]
  total: number
  total_size_bytes: number
}

export interface RequirementsImportRequest {
  requirements: string
}

export interface RequirementsImportResponse {
  success_count: number
  fail_count: number
  successful: Array<{
    package: string
    version: string | null
    message: string
  }>
  failed: Array<{
    package: string
    version: string | null
    message: string
  }>
}
