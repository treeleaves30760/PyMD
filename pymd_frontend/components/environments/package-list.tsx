'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
import { Skeleton } from '@/components/ui/skeleton'
import { useEnvironmentStore } from '@/stores/environmentStore'
import { Trash2, Package } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import type { Package as PackageType } from '@/types/environment'

interface PackageListProps {
  environmentId: string
  isLoading?: boolean
}

export function PackageList({ environmentId, isLoading = false }: PackageListProps) {
  const { packages, uninstallPackage } = useEnvironmentStore()
  const { toast } = useToast()
  const [uninstalling, setUninstalling] = useState<string | null>(null)
  const [packageToDelete, setPackageToDelete] = useState<PackageType | null>(null)

  const handleUninstall = async () => {
    if (!packageToDelete) return

    setUninstalling(packageToDelete.package_name)
    const success = await uninstallPackage(environmentId, packageToDelete.package_name)

    if (success) {
      toast({
        title: 'Package uninstalled',
        description: `Successfully uninstalled ${packageToDelete.package_name}`,
      })
    } else {
      toast({
        title: 'Uninstall failed',
        description: `Failed to uninstall ${packageToDelete.package_name}`,
        variant: 'destructive',
      })
    }

    setUninstalling(null)
    setPackageToDelete(null)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatSize = (bytes: number | null) => {
    if (!bytes) return 'N/A'
    const mb = bytes / (1024 * 1024)
    if (mb < 1) {
      return `${(bytes / 1024).toFixed(1)} KB`
    }
    return `${mb.toFixed(1)} MB`
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }

  if (packages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12 text-center">
        <Package className="mb-4 h-12 w-12 text-muted-foreground" />
        <h3 className="mb-2 text-lg font-semibold">No packages installed</h3>
        <p className="text-sm text-muted-foreground">
          Install packages to get started with your environment
        </p>
      </div>
    )
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[200px]">Package</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Size</TableHead>
              <TableHead>Installed</TableHead>
              <TableHead className="w-[80px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {packages.map((pkg) => (
              <TableRow key={pkg.id}>
                <TableCell className="font-medium">{pkg.package_name}</TableCell>
                <TableCell>
                  {pkg.version ? (
                    <Badge variant="outline">{pkg.version}</Badge>
                  ) : (
                    <span className="text-muted-foreground">Unknown</span>
                  )}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {formatSize(pkg.size_bytes)}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {formatDate(pkg.installed_at)}
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setPackageToDelete(pkg)}
                    disabled={uninstalling === pkg.package_name}
                    title="Uninstall package"
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="mt-4 text-sm text-muted-foreground">
        Total: {packages.length} packages •{' '}
        {formatSize(packages.reduce((sum, pkg) => sum + (pkg.size_bytes || 0), 0))}
      </div>

      <AlertDialog
        open={!!packageToDelete}
        onOpenChange={(open) => !open && setPackageToDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Uninstall package?</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to uninstall <strong>{packageToDelete?.package_name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleUninstall}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Uninstall
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
