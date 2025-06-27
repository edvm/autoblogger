"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { MarkdownViewer } from "@/components/ui/markdown-viewer"
import { createApiClient, type UserContentItem, type BloggerResponse } from "@/lib/api"
import { useAuth } from "@clerk/nextjs"
import { 
  X,
  Edit,
  Download,
  Share,
  Copy,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock
} from "lucide-react"

interface ContentPreviewModalProps {
  isOpen: boolean
  onClose: () => void
  item: UserContentItem
  onDownload: (item: UserContentItem) => void
  isDownloading: boolean
}

export function ContentPreviewModal({ 
  isOpen, 
  onClose, 
  item, 
  onDownload,
  isDownloading 
}: ContentPreviewModalProps) {
  const { getToken } = useAuth()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  const router = useRouter()
  
  const [content, setContent] = useState<BloggerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (isOpen && item.has_content) {
      loadContent()
    }
  }, [isOpen, item.id, item.has_content, loadContent])

  const loadContent = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.getBloggerUsageStatus(item.id)
      setContent(data)
    } catch (err) {
      console.error("Failed to load content:", err)
      setError("Failed to load content")
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = () => {
    router.push(`/editor/${item.id}`)
    onClose()
  }

  const handleCopy = async () => {
    if (content?.final_content) {
      try {
        await navigator.clipboard.writeText(content.final_content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (error) {
        console.error("Failed to copy:", error)
      }
    }
  }

  const handleShare = async () => {
    if (navigator.share && content?.final_content) {
      try {
        await navigator.share({
          title: item.topic,
          text: content.final_content.substring(0, 200) + "...",
          url: window.location.href
        })
      } catch (error) {
        // Fallback to copying link
        handleCopy()
      }
    } else {
      handleCopy()
    }
  }

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case "completed":
        return {
          icon: CheckCircle,
          text: "Completed",
          color: "text-green-600"
        }
      case "failed":
        return {
          icon: AlertCircle,
          text: "Failed",
          color: "text-red-600"
        }
      case "in_progress":
        return {
          icon: Loader2,
          text: "Generating...",
          color: "text-blue-600"
        }
      default:
        return {
          icon: Clock,
          text: "Pending",
          color: "text-yellow-600"
        }
    }
  }

  if (!isOpen) return null

  const statusDisplay = getStatusDisplay(item.status)
  const StatusIcon = statusDisplay.icon

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-2xl modal-shadow-enhanced w-full max-w-4xl max-h-[90vh] overflow-hidden modal-border-enhanced modal-glow animate-in fade-in-0 zoom-in-95 duration-200">
        {/* Header */}
        <div className="border-b border-border p-6 bg-muted/30">
          <div className="flex items-start justify-between">
            <div className="flex-1 pr-4">
              <div className="flex items-center space-x-2 mb-2">
                <StatusIcon className={`h-4 w-4 ${statusDisplay.color} ${item.status === 'in_progress' ? 'animate-spin' : ''}`} />
                <span className={`text-sm font-medium ${statusDisplay.color}`}>
                  {statusDisplay.text}
                </span>
              </div>
              <h2 className="text-xl font-bold text-foreground line-clamp-2">
                {item.topic}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                Created {new Date(item.created_at).toLocaleDateString()} • {item.app_name}
              </p>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2 mt-4">
            {item.has_content && (
              <>
                <Button
                  onClick={handleEdit}
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Open in Editor
                </Button>
                <Button
                  variant="outline"
                  onClick={() => onDownload(item)}
                  disabled={isDownloading}
                >
                  {isDownloading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  Download
                </Button>
                <Button
                  variant="outline"
                  onClick={handleCopy}
                >
                  {copied ? (
                    <CheckCircle className="h-4 w-4 mr-2" />
                  ) : (
                    <Copy className="h-4 w-4 mr-2" />
                  )}
                  {copied ? "Copied!" : "Copy"}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleShare}
                >
                  <Share className="h-4 w-4 mr-2" />
                  Share
                </Button>
              </>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                <p className="text-muted-foreground">Loading content...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-12">
              <Card className="border-red-200 bg-red-50 dark:bg-red-900/20">
                <CardContent className="text-center py-8">
                  <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
                    Failed to Load Content
                  </h3>
                  <p className="text-red-600 dark:text-red-300 mb-4">
                    {error}
                  </p>
                  <Button 
                    variant="outline" 
                    onClick={loadContent}
                    className="border-red-200 text-red-600 hover:bg-red-100"
                  >
                    Try Again
                  </Button>
                </CardContent>
              </Card>
            </div>
          ) : content?.final_content ? (
            <MarkdownViewer
              content={content.final_content}
              title={item.topic}
              sources={content.sources}
              className="border-0 shadow-none bg-transparent"
            />
          ) : item.status === 'in_progress' ? (
            <div className="flex items-center justify-center py-12">
              <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
                <CardContent className="text-center py-8">
                  <Loader2 className="h-12 w-12 text-blue-500 mx-auto mb-4 animate-spin" />
                  <h3 className="text-lg font-medium text-blue-800 dark:text-blue-200 mb-2">
                    Content Generation in Progress
                  </h3>
                  <p className="text-blue-600 dark:text-blue-300 mb-4">
                    Your article is being generated. Please check back in a few minutes.
                  </p>
                  <Button 
                    variant="outline" 
                    onClick={loadContent}
                    className="border-blue-200 text-blue-600 hover:bg-blue-100"
                  >
                    Refresh Status
                  </Button>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="flex items-center justify-center py-12">
              <Card>
                <CardContent className="text-center py-8">
                  <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-foreground mb-2">
                    No Content Available
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    This content is not available for preview.
                  </p>
                  {item.status === 'failed' && content?.error_message && (
                    <p className="text-sm text-red-600 dark:text-red-400">
                      Error: {content.error_message}
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}