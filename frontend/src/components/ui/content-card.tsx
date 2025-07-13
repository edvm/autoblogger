"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { type UserContentItem } from "@/lib/api"
import { 
  FileText, 
  Download, 
  Clock, 
  Loader2,
  Eye,
  Edit,
  MoreHorizontal,
  CheckCircle,
  AlertCircle,
  Copy
} from "lucide-react"

interface ContentCardProps {
  item: UserContentItem
  onDownload: (item: UserContentItem) => void
  onPreview?: (item: UserContentItem) => void
  onDelete?: (item: UserContentItem) => void // Future feature
  isDownloading: boolean
  isSelected?: boolean
  onSelect?: (item: UserContentItem, selected: boolean) => void
}

export function ContentCard({ 
  item, 
  onDownload, 
  onPreview,
  isDownloading,
  isSelected = false,
  onSelect
}: ContentCardProps) {
  const router = useRouter()
  const [showActions, setShowActions] = useState(false)

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case "completed":
        return {
          icon: CheckCircle,
          text: "Completed",
          color: "text-green-600",
          bgColor: "bg-green-50 dark:bg-green-900/20",
          ringColor: "ring-green-200"
        }
      case "failed":
        return {
          icon: AlertCircle,
          text: "Failed",
          color: "text-red-600",
          bgColor: "bg-red-50 dark:bg-red-900/20",
          ringColor: "ring-red-200"
        }
      case "in_progress":
        return {
          icon: Loader2,
          text: "Generating...",
          color: "text-blue-600",
          bgColor: "bg-blue-50 dark:bg-blue-900/20",
          ringColor: "ring-blue-200"
        }
      default:
        return {
          icon: Clock,
          text: "Pending",
          color: "text-yellow-600",
          bgColor: "bg-yellow-50 dark:bg-yellow-900/20",
          ringColor: "ring-yellow-200"
        }
    }
  }

  const statusDisplay = getStatusDisplay(item.status)
  const StatusIcon = statusDisplay.icon

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 1) return "Today"
    if (diffDays === 2) return "Yesterday"
    if (diffDays <= 7) return `${diffDays - 1} days ago`
    return date.toLocaleDateString()
  }

  // Generate preview text from topic (in real app, this would come from actual content)
  const getPreviewText = (topic: string) => {
    return `This article explores ${topic.toLowerCase()}...`
  }

  const estimatedWordCount = 800 + Math.floor(Math.random() * 1200) // Mock word count
  const readingTime = Math.ceil(estimatedWordCount / 200) // 200 WPM average

  const handleEdit = () => {
    router.push(`/editor/${item.id}`)
  }

  const handleCopyTopic = async () => {
    try {
      await navigator.clipboard.writeText(item.topic)
    } catch (error) {
      console.error("Failed to copy:", error)
    }
  }

  return (
    <Card 
      className={`group relative overflow-hidden transition-all duration-200 hover:shadow-lg hover:scale-[1.02] cursor-pointer ${
        isSelected ? `ring-2 ${statusDisplay.ringColor}` : ''
      } ${item.status === 'completed' ? 'border-green-200' : ''}`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Selection Overlay */}
      {onSelect && (
        <div 
          className="absolute top-3 left-3 z-10"
          onClick={(e) => {
            e.stopPropagation()
            onSelect(item, !isSelected)
          }}
        >
          <div className={`w-5 h-5 rounded border-2 transition-colors ${
            isSelected 
              ? 'bg-blue-500 border-blue-500' 
              : 'border-gray-300 hover:border-blue-400'
          }`}>
            {isSelected && (
              <CheckCircle className="w-3 h-3 text-white m-0.5" />
            )}
          </div>
        </div>
      )}

      {/* Quick Actions - Top Right */}
      <div className={`absolute top-3 right-3 z-10 transition-opacity duration-200 ${
        showActions ? 'opacity-100' : 'opacity-0'
      }`}>
        <div className="flex items-center space-x-1 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-1 shadow-sm">
          {item.has_content && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  if (onPreview) onPreview(item)
                }}
                className="h-8 w-8 p-0 hover:bg-blue-100"
              >
                <Eye className="h-3 w-3" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  handleEdit()
                }}
                className="h-8 w-8 p-0 hover:bg-green-100"
              >
                <Edit className="h-3 w-3" />
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              // Show more actions menu
            }}
            className="h-8 w-8 p-0 hover:bg-gray-100"
          >
            <MoreHorizontal className="h-3 w-3" />
          </Button>
        </div>
      </div>

      <div onClick={() => item.has_content && handleEdit()}>
        <CardHeader className="pb-3">
          {/* Status Indicator */}
          <div className={`flex items-center space-x-2 mb-2 px-2 py-1 rounded-full w-fit ${statusDisplay.bgColor}`}>
            <StatusIcon className={`h-3 w-3 ${statusDisplay.color} ${item.status === 'in_progress' ? 'animate-spin' : ''}`} />
            <span className={`text-xs font-medium ${statusDisplay.color}`}>
              {statusDisplay.text}
            </span>
          </div>

          <CardTitle className="text-lg font-semibold line-clamp-2 leading-tight">
            {item.topic}
          </CardTitle>

          {/* Preview Text */}
          {item.has_content && (
            <CardDescription className="text-sm text-muted-foreground line-clamp-2 mt-2">
              {getPreviewText(item.topic)}
            </CardDescription>
          )}
        </CardHeader>

        <CardContent>
          {/* Metadata Row */}
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1">
                <Clock className="h-3 w-3" />
                <span>{formatDate(item.created_at)}</span>
              </span>
              {item.has_content && (
                <span className="flex items-center space-x-1">
                  <FileText className="h-3 w-3" />
                  <span>{estimatedWordCount} words</span>
                </span>
              )}
            </div>
            {item.has_content && (
              <span className="text-xs font-medium">
                {readingTime} min read
              </span>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {item.has_content ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDownload(item)
                    }}
                    disabled={isDownloading}
                    className="flex items-center space-x-1"
                  >
                    {isDownloading ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <Download className="h-3 w-3" />
                    )}
                    <span className="hidden sm:inline">
                      {isDownloading ? "Downloading..." : "Download"}
                    </span>
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleCopyTopic()
                    }}
                    className="h-8 w-8 p-0"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                </>
              ) : (
                <div className="text-xs text-muted-foreground py-1">
                  {item.status === 'in_progress' ? 'Generating content...' : 'Content not available'}
                </div>
              )}
            </div>

            {/* Content Type Badge */}
            <div className="text-xs font-medium text-muted-foreground bg-muted px-2 py-1 rounded">
              {item.app_name.charAt(0).toUpperCase() + item.app_name.slice(1)}
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  )
}