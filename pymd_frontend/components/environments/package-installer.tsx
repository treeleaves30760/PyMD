'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useEnvironmentStore } from '@/stores/environmentStore'
import { useToast } from '@/hooks/use-toast'
import { Package, FileText, Loader2, CheckCircle2, XCircle, AlertCircle } from 'lucide-react'

interface PackageInstallerProps {
  environmentId: string
}

export function PackageInstaller({ environmentId }: PackageInstallerProps) {
  const {
    installPackages,
    importRequirements,
    isInstalling,
    installResult,
    installError,
    clearInstallResult,
    stats,
  } = useEnvironmentStore()
  const { toast } = useToast()

  const [packageInput, setPackageInput] = useState('')
  const [requirementsInput, setRequirementsInput] = useState('')

  const handleInstallPackages = async () => {
    if (!packageInput.trim()) {
      toast({
        title: 'No packages specified',
        description: 'Please enter at least one package name',
        variant: 'destructive',
      })
      return
    }

    // Split by comma or newline, trim whitespace
    const packages = packageInput
      .split(/[,\n]/)
      .map((pkg) => pkg.trim())
      .filter((pkg) => pkg.length > 0)

    if (packages.length === 0) {
      toast({
        title: 'No packages specified',
        description: 'Please enter at least one package name',
        variant: 'destructive',
      })
      return
    }

    if (packages.length > 10) {
      toast({
        title: 'Too many packages',
        description: 'You can install a maximum of 10 packages at once',
        variant: 'destructive',
      })
      return
    }

    const result = await installPackages(environmentId, packages)

    if (result) {
      if (result.success_count > 0) {
        toast({
          title: 'Installation complete',
          description: `Successfully installed ${result.success_count} package(s)`,
        })
        setPackageInput('')
      }

      if (result.fail_count > 0) {
        toast({
          title: 'Some packages failed',
          description: `${result.fail_count} package(s) failed to install`,
          variant: 'destructive',
        })
      }
    }
  }

  const handleImportRequirements = async () => {
    if (!requirementsInput.trim()) {
      toast({
        title: 'No requirements provided',
        description: 'Please paste your requirements.txt content',
        variant: 'destructive',
      })
      return
    }

    const result = await importRequirements(environmentId, requirementsInput)

    if (result) {
      if (result.success_count > 0) {
        toast({
          title: 'Import complete',
          description: `Successfully installed ${result.success_count} package(s)`,
        })
        setRequirementsInput('')
      }

      if (result.fail_count > 0) {
        toast({
          title: 'Some packages failed',
          description: `${result.fail_count} package(s) failed to install`,
          variant: 'destructive',
        })
      }
    }
  }

  const quotaUsage = stats
    ? `${stats.total_packages} / ${stats.package_limit} packages`
    : 'Loading...'

  const quotaPercent = stats
    ? Math.round((stats.total_packages / stats.package_limit) * 100)
    : 0

  return (
    <div className="space-y-4">
      {/* Quota Info */}
      {stats && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Package Quota</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{quotaUsage}</span>
              <Badge variant={quotaPercent > 80 ? 'destructive' : 'default'}>
                {quotaPercent}% used
              </Badge>
            </div>
            <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className={`h-full transition-all ${
                  quotaPercent > 80 ? 'bg-destructive' : 'bg-primary'
                }`}
                style={{ width: `${quotaPercent}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Installation Results */}
      {installResult && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="mb-2 font-semibold">Installation Results:</div>
            <div className="space-y-1 text-sm">
              {installResult.successful.length > 0 && (
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 text-green-500" />
                  <div>
                    <strong>Successful ({installResult.success_count}):</strong>
                    <div className="ml-1 text-muted-foreground">
                      {installResult.successful.map((pkg) => pkg.package).join(', ')}
                    </div>
                  </div>
                </div>
              )}
              {installResult.failed.length > 0 && (
                <div className="flex items-start gap-2">
                  <XCircle className="mt-0.5 h-4 w-4 text-destructive" />
                  <div>
                    <strong>Failed ({installResult.fail_count}):</strong>
                    <div className="ml-1 text-muted-foreground">
                      {installResult.failed.map((pkg) => `${pkg.package}: ${pkg.message}`).join(', ')}
                    </div>
                  </div>
                </div>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2"
              onClick={clearInstallResult}
            >
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {installError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{installError}</AlertDescription>
        </Alert>
      )}

      {/* Installation Tabs */}
      <Tabs defaultValue="packages" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="packages">
            <Package className="mr-2 h-4 w-4" />
            Install Packages
          </TabsTrigger>
          <TabsTrigger value="requirements">
            <FileText className="mr-2 h-4 w-4" />
            Import Requirements
          </TabsTrigger>
        </TabsList>

        <TabsContent value="packages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Install Packages</CardTitle>
              <CardDescription>
                Install Python packages using pip. Separate multiple packages with commas or newlines.
                Supports version pinning (e.g., "numpy==1.24.0").
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="packages">Packages (max 10)</Label>
                <Textarea
                  id="packages"
                  placeholder="numpy, pandas==2.0.0, matplotlib>=3.5"
                  value={packageInput}
                  onChange={(e) => setPackageInput(e.target.value)}
                  disabled={isInstalling}
                  rows={4}
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground">
                  Examples: numpy, pandas==2.0.0, flask>=2.0, requests~=2.28
                </p>
              </div>

              <Button
                onClick={handleInstallPackages}
                disabled={isInstalling || !packageInput.trim()}
                className="w-full"
              >
                {isInstalling ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Installing...
                  </>
                ) : (
                  <>
                    <Package className="mr-2 h-4 w-4" />
                    Install Packages
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Import Requirements.txt</CardTitle>
              <CardDescription>
                Paste the contents of your requirements.txt file to install multiple packages at once.
                Comments and empty lines will be ignored.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="requirements">Requirements.txt Content</Label>
                <Textarea
                  id="requirements"
                  placeholder="numpy>=1.24.0&#10;pandas==2.0.0&#10;matplotlib&#10;# This is a comment"
                  value={requirementsInput}
                  onChange={(e) => setRequirementsInput(e.target.value)}
                  disabled={isInstalling}
                  rows={10}
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground">
                  Tip: Copy and paste the entire contents of your requirements.txt file
                </p>
              </div>

              <Button
                onClick={handleImportRequirements}
                disabled={isInstalling || !requirementsInput.trim()}
                className="w-full"
              >
                {isInstalling ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Import Requirements
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
