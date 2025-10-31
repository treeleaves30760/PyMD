'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from '@/components/ui/dropdown-menu'
import { useEnvironmentStore } from '@/stores/environmentStore'
import { Package, Settings, Plus, RefreshCw } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface EnvironmentSelectorProps {
  onManage?: () => void
}

export function EnvironmentSelector({ onManage }: EnvironmentSelectorProps) {
  const {
    environments,
    activeEnvironmentId,
    setActiveEnvironment,
    loadEnvironments,
    isLoadingEnvironments,
  } = useEnvironmentStore()

  // Load environments on mount
  useEffect(() => {
    loadEnvironments()
  }, [loadEnvironments])

  const activeEnvironment = environments.find((env) => env.id === activeEnvironmentId)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="min-w-[180px] justify-start"
          disabled={isLoadingEnvironments}
        >
          <Package className="mr-2 h-4 w-4" />
          {isLoadingEnvironments ? (
            <span className="text-muted-foreground">Loading...</span>
          ) : activeEnvironment ? (
            <span className="flex items-center gap-2">
              {activeEnvironment.name}
              <Badge variant="secondary" className="text-xs">
                {activeEnvironment.package_count}
              </Badge>
            </span>
          ) : (
            <span className="text-muted-foreground">No environment</span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[280px]">
        <DropdownMenuLabel className="flex items-center justify-between">
          <span>Select Environment</span>
          <Button
            variant="ghost"
            size="sm"
            className="h-6 w-6 p-0"
            onClick={(e) => {
              e.stopPropagation()
              loadEnvironments()
            }}
            title="Refresh environments"
          >
            <RefreshCw className="h-3 w-3" />
          </Button>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        {environments.length === 0 ? (
          <div className="px-2 py-6 text-center text-sm text-muted-foreground">
            No environments found
          </div>
        ) : (
          environments.map((env) => (
            <DropdownMenuItem
              key={env.id}
              onClick={() => setActiveEnvironment(env.id)}
              className="flex items-center justify-between"
            >
              <div className="flex flex-col gap-1">
                <span className="font-medium">
                  {env.name}
                  {env.id === activeEnvironmentId && (
                    <span className="ml-2 text-xs text-primary">(Active)</span>
                  )}
                </span>
                <span className="text-xs text-muted-foreground">
                  Python {env.python_version} • {env.package_count} packages
                </span>
              </div>
              <Badge
                variant={env.status === 'active' ? 'default' : 'secondary'}
                className="ml-2 text-xs"
              >
                {env.status}
              </Badge>
            </DropdownMenuItem>
          ))
        )}

        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={onManage}
          className="flex items-center text-primary"
        >
          <Settings className="mr-2 h-4 w-4" />
          Manage Environments
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
