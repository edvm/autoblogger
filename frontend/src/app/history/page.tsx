"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useAuth } from "@clerk/nextjs"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { createApiClient, type AppUsage } from "@/lib/api"
import { History, Clock, CheckCircle, XCircle, AlertCircle, Loader2, RefreshCw } from "lucide-react"

export const dynamic = 'force-dynamic'

export default function HistoryPage() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  
  const [usage, setUsage] = useState<AppUsage[]>([])
  const [loading, setLoading] = useState(true)

  const loadUsageHistory = useCallback(async () => {
    try {
      const data = await api.getAppUsageHistory(50, 0)
      setUsage(data)
    } catch (error) {
      console.error("Failed to load usage history:", error)
    } finally {
      setLoading(false)
    }
  }, [api])

  useEffect(() => {
    loadUsageHistory()
  }, [loadUsageHistory])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "in_progress":
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600"
      case "failed":
        return "text-red-600"
      case "in_progress":
        return "text-blue-600"
      default:
        return "text-yellow-600"
    }
  }

  const formatDuration = (startedAt: string, completedAt?: string) => {
    const start = new Date(startedAt)
    const end = completedAt ? new Date(completedAt) : new Date()
    const duration = Math.round((end.getTime() - start.getTime()) / 1000)
    
    if (duration < 60) return `${duration}s`
    if (duration < 3600) return `${Math.round(duration / 60)}m`
    return `${Math.round(duration / 3600)}h`
  }

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center">
        <Navigation />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin" />
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <Navigation />
      
      <main className="flex-1 container py-6">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Usage History</h1>
              <p className="text-muted-foreground">
                View your app usage history and generated content
              </p>
            </div>
            <Button onClick={loadUsageHistory} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>

          {usage.length === 0 ? (
            <Card>
              <CardContent className="text-center py-8">
                <History className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No usage history</h3>
                <p className="text-muted-foreground">
                  You haven&apos;t generated any blog posts yet. Start creating!
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {usage.map((item) => (
                <Card key={item.id} className="cursor-pointer hover:bg-muted/50 transition-colors">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center space-x-2">
                        {getStatusIcon(item.status)}
                        <span className="capitalize">{item.app_name} App</span>
                      </CardTitle>
                      <div className="text-right text-sm text-muted-foreground">
                        <div>{new Date(item.started_at).toLocaleDateString()}</div>
                        <div>{new Date(item.started_at).toLocaleTimeString()}</div>
                      </div>
                    </div>
                    <CardDescription className="flex items-center justify-between">
                      <span className={getStatusColor(item.status)}>
                        Status: {item.status.toUpperCase()}
                      </span>
                      <span className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>{formatDuration(item.started_at, item.completed_at)}</span>
                      </span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium">Credits Used:</span>
                        <span className="text-sm">{item.credits_consumed}</span>
                      </div>
                      
                      {item.error_message && (
                        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                          <p className="text-red-800 dark:text-red-200 text-sm">
                            {item.error_message}
                          </p>
                        </div>
                      )}

                      {item.completed_at && (
                        <div className="text-sm text-muted-foreground">
                          Completed: {new Date(item.completed_at).toLocaleDateString()} at{' '}
                          {new Date(item.completed_at).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}