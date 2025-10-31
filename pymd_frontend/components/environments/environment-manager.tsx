'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useEnvironmentStore } from '@/stores/environmentStore'
import { useToast } from '@/hooks/use-toast'
import { PackageList } from './package-list'
import { PackageInstaller } from './package-installer'
import {
  Plus,
  Trash2,
  RefreshCw,
  Package,
  Settings,
  Loader2,
} from 'lucide-react'
import type { Environment } from '@/types/environment'

interface EnvironmentManagerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function EnvironmentManager({ open, onOpenChange }: EnvironmentManagerProps) {
  const {
    environments,
    activeEnvironmentId,
    setActiveEnvironment,
    createEnvironment,
    deleteEnvironment,
    resetEnvironment,
    loadEnvironments,
    loadPackages,
    isLoadingEnvironments,
    isLoadingPackages,
  } = useEnvironmentStore()
  const { toast } = useToast()

  const [selectedEnvId, setSelectedEnvId] = useState<string | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showResetDialog, setShowResetDialog] = useState(false)
  const [newEnvName, setNewEnvName] = useState('')
  const [envToDelete, setEnvToDelete] = useState<Environment | null>(null)
  const [envToReset, setEnvToReset] = useState<Environment | null>(null)
  const [isCreating, setIsCreating] = useState(false)

  // Load environments when dialog opens
  useEffect(() => {
    if (open) {
      loadEnvironments()
      if (activeEnvironmentId) {
        setSelectedEnvId(activeEnvironmentId)
      }
    }
  }, [open, loadEnvironments, activeEnvironmentId])

  // Load packages when selected environment changes
  useEffect(() => {
    if (selectedEnvId) {
      loadPackages(selectedEnvId)
    }
  }, [selectedEnvId, loadPackages])

  const selectedEnvironment = environments.find((env) => env.id === selectedEnvId)

  const handleCreateEnvironment = async () => {
    if (!newEnvName.trim()) {
      toast({
        title: 'Invalid name',
        description: 'Please enter a valid environment name',
        variant: 'destructive',
      })
      return
    }

    setIsCreating(true)
    const newEnv = await createEnvironment(newEnvName, '3.11')

    if (newEnv) {
      toast({
        title: 'Environment created',
        description: `Successfully created environment "${newEnvName}"`,
      })
      setNewEnvName('')
      setShowCreateDialog(false)
      setSelectedEnvId(newEnv.id)
    }

    setIsCreating(false)
  }

  const handleDeleteEnvironment = async () => {
    if (!envToDelete) return

    const success = await deleteEnvironment(envToDelete.id)

    if (success) {
      toast({
        title: 'Environment deleted',
        description: `Successfully deleted environment "${envToDelete.name}"`,
      })

      // If deleted environment was selected, clear selection
      if (selectedEnvId === envToDelete.id) {
        setSelectedEnvId(environments.length > 0 ? environments[0].id : null)
      }
    } else {
      toast({
        title: 'Delete failed',
        description: `Failed to delete environment "${envToDelete.name}"`,
        variant: 'destructive',
      })
    }

    setEnvToDelete(null)
    setShowDeleteDialog(false)
  }

  const handleResetEnvironment = async () => {
    if (!envToReset) return

    const success = await resetEnvironment(envToReset.id)

    if (success) {
      toast({
        title: 'Environment reset',
        description: `Successfully reset environment "${envToReset.name}"`,
      })
    } else {
      toast({
        title: 'Reset failed',
        description: `Failed to reset environment "${envToReset.name}"`,
        variant: 'destructive',
      })
    }

    setEnvToReset(null)
    setShowResetDialog(false)
  }

  const formatSize = (bytes: number) => {
    const mb = bytes / (1024 * 1024)
    if (mb < 1) {
      return `${(bytes / 1024).toFixed(1)} KB`
    }
    return `${mb.toFixed(1)} MB`
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-h-[90vh] max-w-6xl overflow-hidden">
          <DialogHeader>
            <DialogTitle>Manage Environments</DialogTitle>
            <DialogDescription>
              Create and manage Python environments for your projects
            </DialogDescription>
          </DialogHeader>

          <div className="grid grid-cols-[300px_1fr] gap-6 overflow-hidden">
            {/* Environment List Sidebar */}
            <div className="flex flex-col gap-4 overflow-y-auto pr-2">
              <Button
                onClick={() => setShowCreateDialog(true)}
                className="w-full"
                size="sm"
              >
                <Plus className="mr-2 h-4 w-4" />
                New Environment
              </Button>

              {isLoadingEnvironments ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : environments.length === 0 ? (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <Package className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">No environments</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {environments.map((env) => (
                    <Card
                      key={env.id}
                      className={`cursor-pointer transition-colors ${
                        selectedEnvId === env.id
                          ? 'border-primary bg-accent'
                          : 'hover:bg-accent'
                      }`}
                      onClick={() => setSelectedEnvId(env.id)}
                    >
                      <CardHeader className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-sm">{env.name}</CardTitle>
                            <CardDescription className="mt-1 text-xs">
                              Python {env.python_version}
                            </CardDescription>
                          </div>
                          <Badge
                            variant={env.status === 'active' ? 'default' : 'secondary'}
                            className="ml-2 text-xs"
                          >
                            {env.status}
                          </Badge>
                        </div>
                        <div className="mt-2 flex gap-2 text-xs text-muted-foreground">
                          <span>{env.package_count} packages</span>
                          <span>•</span>
                          <span>{formatSize(env.total_size_bytes)}</span>
                        </div>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Main Content Area */}
            <div className="flex flex-col overflow-hidden">
              {selectedEnvironment ? (
                <Tabs defaultValue="packages" className="flex flex-1 flex-col overflow-hidden">
                  <div className="flex items-center justify-between border-b pb-4">
                    <div>
                      <h3 className="text-lg font-semibold">{selectedEnvironment.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        Python {selectedEnvironment.python_version} •{' '}
                        {selectedEnvironment.package_count} packages •{' '}
                        {formatSize(selectedEnvironment.total_size_bytes)}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEnvToReset(selectedEnvironment)
                          setShowResetDialog(true)
                        }}
                      >
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Reset
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setEnvToDelete(selectedEnvironment)
                          setShowDeleteDialog(true)
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                      {selectedEnvironment.id !== activeEnvironmentId && (
                        <Button
                          size="sm"
                          onClick={() => {
                            setActiveEnvironment(selectedEnvironment.id)
                            toast({
                              title: 'Environment activated',
                              description: `Switched to "${selectedEnvironment.name}"`,
                            })
                          }}
                        >
                          Activate
                        </Button>
                      )}
                    </div>
                  </div>

                  <TabsList className="mt-4 grid w-full grid-cols-2">
                    <TabsTrigger value="packages">
                      <Package className="mr-2 h-4 w-4" />
                      Installed Packages
                    </TabsTrigger>
                    <TabsTrigger value="install">
                      <Settings className="mr-2 h-4 w-4" />
                      Install Packages
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="packages" className="flex-1 overflow-y-auto">
                    <PackageList
                      environmentId={selectedEnvironment.id}
                      isLoading={isLoadingPackages}
                    />
                  </TabsContent>

                  <TabsContent value="install" className="flex-1 overflow-y-auto">
                    <PackageInstaller environmentId={selectedEnvironment.id} />
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="flex flex-1 items-center justify-center">
                  <div className="text-center">
                    <Package className="mx-auto mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      Select an environment to view details
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Create Environment Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Environment</DialogTitle>
            <DialogDescription>
              Create a new isolated Python environment for your project
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="env-name">Environment Name</Label>
              <Input
                id="env-name"
                placeholder="my-project"
                value={newEnvName}
                onChange={(e) => setNewEnvName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateEnvironment()
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                Use lowercase letters, numbers, and hyphens
              </p>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateEnvironment} disabled={isCreating}>
              {isCreating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete environment?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{envToDelete?.name}</strong>? All installed
              packages and data will be permanently removed. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteEnvironment}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reset Confirmation Dialog */}
      <AlertDialog open={showResetDialog} onOpenChange={setShowResetDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Reset environment?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to reset <strong>{envToReset?.name}</strong>? All installed
              packages will be removed, but the environment will remain. This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleResetEnvironment}>Reset</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
