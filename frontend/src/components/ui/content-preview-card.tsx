"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardFooter, CardHeader } from "./card"
import { Button } from "./button"
import { Badge } from "./badge"
import { 
  Eye, 
  Download, 
  Share2, 
  Edit3, 
  Calendar, 
  Clock, 
  FileText,
  BookOpen,
  Bookmark,
  BookmarkCheck
} from "lucide-react"

export interface ContentPreview {
  id: string
  title: string
  excerpt: string
  topic: string
  status: "draft" | "completed" | "processing" | "error"
  createdAt: Date
  readingTime: number
  wordCount: number
  thumbnail?: string
  tags?: string[]
  isFavorite?: boolean
}

export interface ContentPreviewCardProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'content'> {
  content: ContentPreview
  onView?: (id: string) => void
  onEdit?: (id: string) => void
  onDownload?: (id: string) => void
  onShare?: (id: string) => void
  onToggleFavorite?: (id: string) => void
}

const ContentPreviewCard = React.forwardRef<HTMLDivElement, ContentPreviewCardProps>(
  ({ className, content, onView, onEdit, onDownload, onShare, onToggleFavorite, ...props }, ref) => {
    const getStatusColor = (status: ContentPreview["status"]) => {
      switch (status) {
        case "completed":
          return "bg-success text-success-foreground"
        case "processing":
          return "bg-soft-coral text-white"
        case "draft":
          return "bg-dusty-blue text-white"
        case "error":
          return "bg-destructive text-destructive-foreground"
        default:
          return "bg-warm-gray text-muted-foreground"
      }
    }

    const getStatusText = (status: ContentPreview["status"]) => {
      switch (status) {
        case "completed":
          return "Ready"
        case "processing":
          return "Creating..."
        case "draft":
          return "Draft"
        case "error":
          return "Error"
        default:
          return "Unknown"
      }
    }

    const formatDate = (date: Date) => {
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }).format(date)
    }

    return (
      <Card
        ref={ref}
        className={cn(
          "group cursor-pointer overflow-hidden bg-gradient-to-br from-warm-cream/50 to-white/80",
          className
        )}
        {...props}
      >
        {/* Thumbnail/Visual Header */}
        <div className="relative h-32 bg-gradient-to-br from-sage-green/20 to-dusty-blue/20 overflow-hidden">
          {content.thumbnail ? (
            <img
              src={content.thumbnail}
              alt={content.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-2">
                <BookOpen className="h-8 w-8 mx-auto text-sage-green/60" />
                <p className="text-xs text-muted-foreground font-medium">
                  {content.topic}
                </p>
              </div>
            </div>
          )}
          
          {/* Status badge */}
          <div className="absolute top-3 right-3">
            <Badge className={cn("text-xs font-medium", getStatusColor(content.status))}>
              {getStatusText(content.status)}
            </Badge>
          </div>
          
          {/* Favorite toggle */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleFavorite?.(content.id)
            }}
            className="absolute top-3 left-3 p-1.5 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/30 transition-colors"
          >
            {content.isFavorite ? (
              <BookmarkCheck className="h-4 w-4 text-golden-yellow" />
            ) : (
              <Bookmark className="h-4 w-4 text-white/70" />
            )}
          </button>
        </div>

        <CardHeader className="pb-4">
          <div className="space-y-3">
            <h3 className="font-accent font-semibold text-lg leading-tight line-clamp-2 group-hover:text-sage-green transition-colors">
              {content.title}
            </h3>
            <p className="text-sm text-muted-foreground line-clamp-3">
              {content.excerpt}
            </p>
          </div>
        </CardHeader>

        <CardContent className="pt-0 pb-4">
          {/* Tags */}
          {content.tags && content.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-4">
              {content.tags.slice(0, 3).map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="text-xs bg-warm-gray/50 text-muted-foreground hover:bg-sage-green/20"
                >
                  {tag}
                </Badge>
              ))}
              {content.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs bg-warm-gray/50 text-muted-foreground">
                  +{content.tags.length - 3}
                </Badge>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1">
                <Calendar className="h-3 w-3" />
                <span>{formatDate(content.createdAt)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="h-3 w-3" />
                <span>{content.readingTime} min read</span>
              </div>
            </div>
            <div className="flex items-center space-x-1">
              <FileText className="h-3 w-3" />
              <span>{content.wordCount.toLocaleString()} words</span>
            </div>
          </div>
        </CardContent>

        <CardFooter className="pt-0">
          <div className="flex items-center justify-between w-full">
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onView?.(content.id)
              }}
              className="flex items-center space-x-1"
            >
              <Eye className="h-3 w-3" />
              <span>View</span>
            </Button>

            <div className="flex items-center space-x-1">
              {content.status === "completed" && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onEdit?.(content.id)
                    }}
                  >
                    <Edit3 className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDownload?.(content.id)
                    }}
                  >
                    <Download className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onShare?.(content.id)
                    }}
                  >
                    <Share2 className="h-3 w-3" />
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardFooter>
      </Card>
    )
  }
)
ContentPreviewCard.displayName = "ContentPreviewCard"

export { ContentPreviewCard }