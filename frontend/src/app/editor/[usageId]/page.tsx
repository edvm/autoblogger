"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useAuth } from "@clerk/nextjs"
import { useParams, useRouter } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { MarkdownViewer } from "@/components/ui/markdown-viewer"
import { createApiClient, type BloggerResponse } from "@/lib/api"
import { 
  ArrowLeft, 
  RefreshCw, 
  Loader2, 
  FileText, 
  Settings,
  Sparkles,
  AlertCircle,
  CheckCircle
} from "lucide-react"

export const dynamic = 'force-dynamic'

export default function EditorPage() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  const params = useParams()
  const router = useRouter()
  const usageId = parseInt(params.usageId as string)
  
  const [content, setContent] = useState<BloggerResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  
  // Future refinement controls (basic structure)
  const [refinementTopic, setRefinementTopic] = useState("")
  const [refinementInstructions, setRefinementInstructions] = useState("")

  const loadContent = useCallback(async () => {
    try {
      setError(null)
      const data = await api.getBloggerUsageStatus(usageId)
      setContent(data)
      
      // Set initial refinement topic from current content
      if (data.final_content && !refinementTopic) {
        // Extract title/topic from content if available
        const lines = data.final_content.split('\n')
        const firstHeader = lines.find(line => line.startsWith('# '))
        if (firstHeader) {
          setRefinementTopic(firstHeader.replace('# ', '').trim())
        }
      }
    } catch (error) {
      console.error("Failed to load content:", error)
      setError("Failed to load content. Please try again.")
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [api, usageId, refinementTopic])

  const handleRefresh = async () => {
    setRefreshing(true)
    await loadContent()
  }

  useEffect(() => {
    if (usageId) {
      loadContent()
    } else {
      setError("Invalid content ID")
      setLoading(false)
    }
  }, [usageId, loadContent])

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case "completed":
        return {
          icon: CheckCircle,
          text: "Generation Complete",
          color: "text-green-600",
          bgColor: "bg-green-50 dark:bg-green-900/20"
        }
      case "failed":
        return {
          icon: AlertCircle,
          text: "Generation Failed",
          color: "text-red-600",
          bgColor: "bg-red-50 dark:bg-red-900/20"
        }
      case "in_progress":
        return {
          icon: Loader2,
          text: "Generating...",
          color: "text-blue-600",
          bgColor: "bg-blue-50 dark:bg-blue-900/20"
        }
      default:
        return {
          icon: AlertCircle,
          text: "Pending",
          color: "text-yellow-600",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/20"
        }
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navigation />
        <main className="flex-1 flex items-center justify-center bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-900/10 dark:to-purple-900/10">
          <div className="text-center animate-in fade-in-0 zoom-in-95 duration-500">
            <div className="w-20 h-20 bg-gradient-to-r from-violet-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
              <FileText className="h-10 w-10 text-white animate-bounce" />
            </div>
            <h2 className="text-2xl font-bold text-foreground mb-2">Loading Your Content</h2>
            <p className="text-muted-foreground mb-4">Getting your article ready for editing...</p>
            <div className="flex items-center justify-center space-x-1">
              <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-violet-500 rounded-full animate-bounce"></div>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (error || !content) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navigation />
        <main className="flex-1 flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardContent className="text-center py-8">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">Content Not Found</h3>
              <p className="text-muted-foreground mb-4">
                {error || "The requested content could not be found."}
              </p>
              <Button onClick={() => router.push('/dashboard')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    )
  }

  const statusDisplay = getStatusDisplay(content.status)
  const StatusIcon = statusDisplay.icon

  return (
    <div className="flex min-h-screen flex-col">
      <Navigation />
      
      <main className="flex-1 bg-muted/30">
        <div className="container py-6 animate-in fade-in-0 slide-in-from-bottom-4 duration-700">
          {/* Header */}
          <div className="flex items-center justify-between mb-6 animate-in fade-in-0 slide-in-from-top-4 duration-500 delay-150">
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                onClick={() => router.push('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Dashboard</span>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-foreground">Content Editor</h1>
                <p className="text-muted-foreground">
                  Review and refine your generated content
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full ${statusDisplay.bgColor}`}>
                <StatusIcon className={`h-4 w-4 ${statusDisplay.color} ${content.status === 'in_progress' ? 'animate-spin' : ''}`} />
                <span className={`text-sm font-medium ${statusDisplay.color}`}>
                  {statusDisplay.text}
                </span>
              </div>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Editor Controls - Left Side */}
            <div className="lg:col-span-1 space-y-6 animate-in fade-in-0 slide-in-from-left-4 duration-500 delay-300">
              {/* Current Content Info */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Content Details</span>
                  </CardTitle>
                  <CardDescription>
                    Information about your generated content
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Status</Label>
                    <div className={`mt-1 flex items-center space-x-2 px-2 py-1 rounded ${statusDisplay.bgColor}`}>
                      <StatusIcon className={`h-3 w-3 ${statusDisplay.color}`} />
                      <span className={`text-xs font-medium ${statusDisplay.color}`}>
                        {statusDisplay.text}
                      </span>
                    </div>
                  </div>
                  
                  {content.final_content && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Word Count</Label>
                      <p className="text-sm font-medium text-foreground mt-1">
                        {content.final_content.split(' ').length} words
                      </p>
                    </div>
                  )}
                  
                  {content.sources && content.sources.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Sources Used</Label>
                      <p className="text-sm font-medium text-foreground mt-1">
                        {content.sources.length} source{content.sources.length > 1 ? 's' : ''}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Future Refinement Controls */}
              <Card className="opacity-60">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="h-5 w-5" />
                    <span>Refinement Tools</span>
                  </CardTitle>
                  <CardDescription>
                    Enhance and iterate on your content (Coming Soon)
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="refinement-topic" className="text-sm font-medium">
                      Focus Topic
                    </Label>
                    <Input
                      id="refinement-topic"
                      placeholder="Refine focus or add specific angle..."
                      value={refinementTopic}
                      onChange={(e) => setRefinementTopic(e.target.value)}
                      disabled
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="refinement-instructions" className="text-sm font-medium">
                      Specific Instructions
                    </Label>
                    <Input
                      id="refinement-instructions"
                      placeholder="Make it more technical, add examples, etc..."
                      value={refinementInstructions}
                      onChange={(e) => setRefinementInstructions(e.target.value)}
                      disabled
                    />
                  </div>
                  
                  <Button 
                    className="w-full" 
                    disabled
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    Refine Content
                  </Button>
                  
                  <p className="text-xs text-muted-foreground text-center">
                    Content refinement features coming in a future update
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Content Preview - Right Side */}
            <div className="lg:col-span-2 animate-in fade-in-0 slide-in-from-right-4 duration-500 delay-500">
              {content.final_content ? (
                <MarkdownViewer
                  content={content.final_content}
                  title="Generated Article"
                  sources={content.sources}
                  className="h-full"
                />
              ) : content.error_message ? (
                <Card className="border-red-200 bg-red-50 dark:bg-red-900/20">
                  <CardContent className="text-center py-8">
                    <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
                      Generation Failed
                    </h3>
                    <p className="text-red-600 dark:text-red-300 mb-4">
                      {content.error_message}
                    </p>
                    <Button 
                      variant="outline" 
                      onClick={() => router.push('/dashboard')}
                      className="border-red-200 text-red-600 hover:bg-red-100"
                    >
                      Try Again
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="text-center py-12">
                    <Loader2 className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-spin" />
                    <h3 className="text-lg font-medium text-foreground mb-2">
                      Content Generation in Progress
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      Your article is being generated. This usually takes a few minutes.
                    </p>
                    <Button 
                      variant="outline" 
                      onClick={handleRefresh}
                      disabled={refreshing}
                    >
                      <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                      Check Status
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}