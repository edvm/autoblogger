"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { type UserContentItem } from "@/lib/api"
import { 
  FileText, 
  Calendar, 
  Clock, 
  Eye, 
  Download, 
  ArrowRight,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Loader2,
  Plus
} from "lucide-react"

interface RecentArticlesProps {
  articles: UserContentItem[]
  onViewArticle?: (usageId: number) => void
  onDownloadArticle?: (usageId: number) => void
  onCreateNew?: () => void
  loading?: boolean
  className?: string
}

export function RecentArticles({ 
  articles, 
  onViewArticle, 
  onDownloadArticle,
  onCreateNew,
  loading = false,
  className = "" 
}: RecentArticlesProps) {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'in_progress':
      case 'pending':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
      case 'in_progress':
      case 'pending':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
      default:
        return 'bg-muted text-muted-foreground'
    }
  }

  const formatTimeAgo = (dateString: string) => {
    if (!mounted) return ''
    
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    if (diffInHours < 48) return 'Yesterday'
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`
    return date.toLocaleDateString()
  }

  const truncateTitle = (title: string, maxLength: number = 50) => {
    if (title.length <= maxLength) return title
    return title.substring(0, maxLength) + '...'
  }

  if (loading) {
    return (
      <Card className={`${className}`}>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-muted rounded-xl animate-pulse"></div>
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded w-32 animate-pulse"></div>
              <div className="h-3 bg-muted rounded w-48 animate-pulse"></div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-muted rounded-lg"></div>
            </div>
          ))}
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={`relative overflow-hidden border-0 bg-gradient-to-br from-slate-50 via-white to-violet-50 dark:from-slate-900 dark:via-slate-800 dark:to-violet-900/20 shadow-2xl ${className}`}>
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-4 right-4">
          <Sparkles className="h-12 w-12 text-violet-600" />
        </div>
        <div className="absolute bottom-4 left-4">
          <div className="grid grid-cols-4 gap-1">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="w-1 h-1 bg-violet-400 rounded-full opacity-20"></div>
            ))}
          </div>
        </div>
      </div>
      
      <CardHeader className="relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold bg-gradient-to-r from-violet-600 to-purple-600 bg-clip-text text-transparent">
                Recent Articles
              </CardTitle>
              <CardDescription className="text-muted-foreground font-medium">
                Your latest AI-generated content
              </CardDescription>
            </div>
          </div>
          {onCreateNew && (
            <Button 
              onClick={onCreateNew}
              size="sm"
              className="bg-gradient-to-r from-violet-600 to-purple-600 hover:opacity-90 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create New
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="relative z-10 space-y-4">
        {articles.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-gradient-to-r from-violet-100 to-purple-100 dark:from-violet-900/30 dark:to-purple-900/30 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-inner">
              <FileText className="h-10 w-10 text-violet-600" />
            </div>
            <h3 className="text-xl font-bold text-foreground mb-3">No articles yet</h3>
            <p className="text-muted-foreground mb-6 max-w-sm mx-auto leading-relaxed">
              Start creating amazing content with AI assistance and watch your ideas come to life
            </p>
            {onCreateNew && (
              <Button 
                onClick={onCreateNew}
                size="lg"
                className="bg-gradient-to-r from-violet-600 to-purple-600 hover:opacity-90 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 px-8"
              >
                <Sparkles className="h-5 w-5 mr-2" />
                Create Your First Article
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {articles.map((article) => (
              <div
                key={article.id}
                className="group flex items-center space-x-4 p-5 rounded-xl bg-white/60 dark:bg-white/5 border border-violet-100 dark:border-violet-800/30 hover:border-violet-300 hover:bg-violet-50/50 dark:hover:bg-violet-900/10 transition-all duration-300 hover:shadow-lg backdrop-blur-sm"
              >
                {/* Status Icon */}
                <div className="flex-shrink-0">
                  {getStatusIcon(article.status)}
                </div>
                
                {/* Article Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-semibold text-foreground group-hover:text-violet-700 dark:group-hover:text-violet-300 transition-colors duration-200">
                      {truncateTitle(article.topic)}
                    </h4>
                    <Badge 
                      variant="secondary" 
                      className={`text-xs ${getStatusColor(article.status)}`}
                    >
                      {article.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-3 w-3" />
                      <span>{formatTimeAgo(article.created_at)}</span>
                    </div>
                    {article.completed_at && (
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>Completed {formatTimeAgo(article.completed_at)}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <FileText className="h-3 w-3" />
                      <span className="capitalize">{article.app_name}</span>
                    </div>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {article.status === 'completed' && article.has_content && onViewArticle && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewArticle(article.id)}
                      className="border-violet-200 text-violet-700 hover:bg-violet-50 dark:border-violet-700 dark:text-violet-300 dark:hover:bg-violet-900/20 shadow-sm hover:shadow-md transition-all duration-200"
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                  )}
                  
                  {article.status === 'completed' && article.has_content && onDownloadArticle && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onDownloadArticle(article.id)}
                      className="border-blue-200 text-blue-700 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-300 dark:hover:bg-blue-900/20 shadow-sm hover:shadow-md transition-all duration-200"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Download
                    </Button>
                  )}
                  
                  {article.status === 'completed' && onViewArticle && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onViewArticle(article.id)}
                      className="text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 hover:bg-violet-100 dark:hover:bg-violet-900/20 transition-all duration-200"
                    >
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
            
            {articles.length >= 5 && (
              <div className="text-center pt-6">
                <Button 
                  variant="ghost" 
                  className="text-violet-600 hover:text-violet-700 dark:text-violet-400 dark:hover:text-violet-300 hover:bg-violet-100 dark:hover:bg-violet-900/20 transition-all duration-300 font-medium"
                >
                  View All Articles
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}