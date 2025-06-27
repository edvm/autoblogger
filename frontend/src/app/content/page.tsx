"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useAuth } from "@clerk/nextjs"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { ContentCard } from "@/components/ui/content-card"
import { ContentPreviewModal } from "@/components/ui/content-preview-modal"
import { createApiClient, type UserContentItem } from "@/lib/api"
import { 
  FileText, 
  Download, 
  RefreshCw, 
  Loader2,
  Search,
  Grid3X3,
  List,
  Plus,
  CheckSquare,
  Square,
  Trash2
} from "lucide-react"

export const dynamic = 'force-dynamic'

export default function ContentPage() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  
  const [content, setContent] = useState<UserContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [downloadingIds, setDownloadingIds] = useState<Set<number>>(new Set())
  
  // Enhanced UI state
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState("newest")
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set())
  const [previewItem, setPreviewItem] = useState<UserContentItem | null>(null)
  const [showBulkActions, setShowBulkActions] = useState(false)

  const loadUserContent = useCallback(async () => {
    try {
      setLoading(true)
      const data = await api.getUserContent(50, 0)
      setContent(data)
    } catch (error) {
      console.error("Failed to load user content:", error)
    } finally {
      setLoading(false)
    }
  }, [api])

  // Filter and sort content
  const filteredAndSortedContent = useMemo(() => {
    const filtered = content.filter(item => {
      const matchesSearch = item.topic.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter
      return matchesSearch && matchesStatus
    })

    // Sort the filtered content
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        case 'oldest':
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        case 'alphabetical':
          return a.topic.localeCompare(b.topic)
        case 'status':
          return a.status.localeCompare(b.status)
        default:
          return 0
      }
    })

    return filtered
  }, [content, searchQuery, statusFilter, sortBy])

  const handleItemSelect = (item: UserContentItem, selected: boolean) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev)
      if (selected) {
        newSet.add(item.id)
      } else {
        newSet.delete(item.id)
      }
      setShowBulkActions(newSet.size > 0)
      return newSet
    })
  }

  const handleSelectAll = () => {
    if (selectedItems.size === filteredAndSortedContent.length) {
      setSelectedItems(new Set())
      setShowBulkActions(false)
    } else {
      setSelectedItems(new Set(filteredAndSortedContent.map(item => item.id)))
      setShowBulkActions(true)
    }
  }

  const handleBulkDownload = async () => {
    const itemsToDownload = filteredAndSortedContent.filter(item => 
      selectedItems.has(item.id) && item.has_content
    )
    
    for (const item of itemsToDownload) {
      await handleDownload(item)
    }
    
    setSelectedItems(new Set())
    setShowBulkActions(false)
  }

  const getContentStats = () => {
    const total = content.length
    const completed = content.filter(item => item.status === 'completed').length
    const inProgress = content.filter(item => item.status === 'in_progress').length
    const failed = content.filter(item => item.status === 'failed').length
    
    return { total, completed, inProgress, failed }
  }

  const stats = getContentStats()

  useEffect(() => {
    loadUserContent()
  }, [loadUserContent])

  const handleDownload = async (item: UserContentItem) => {
    if (!item.has_content) return

    setDownloadingIds(prev => new Set(prev).add(item.id))
    
    try {
      const blob = await api.downloadContent(item.id)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      // Generate filename
      const sanitizedTopic = item.topic
        .replace(/[^a-zA-Z0-9\s\-_]/g, '')
        .replace(/\s+/g, '_')
        .toLowerCase()
      link.download = `${sanitizedTopic}_${item.id}.md`
      
      // Trigger download
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Download failed:", error)
      alert("Failed to download content. Please try again.")
    } finally {
      setDownloadingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(item.id)
        return newSet
      })
    }
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
    <div className="flex min-h-screen flex-col">
      <Navigation />
      
      <main className="flex-1 bg-muted/30">
        <div className="container py-6">
          <div className="space-y-6">
            {/* Header with Stats */}
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold text-foreground">Content Library</h1>
                <p className="text-muted-foreground mt-1">
                  Manage and organize your AI-generated content
                </p>
                
                {/* Quick Stats */}
                <div className="flex items-center space-x-6 mt-4">
                  <div className="text-sm">
                    <span className="font-medium text-foreground">{stats.total}</span>
                    <span className="text-muted-foreground ml-1">Total</span>
                  </div>
                  <div className="text-sm">
                    <span className="font-medium text-green-600">{stats.completed}</span>
                    <span className="text-muted-foreground ml-1">Completed</span>
                  </div>
                  {stats.inProgress > 0 && (
                    <div className="text-sm">
                      <span className="font-medium text-blue-600">{stats.inProgress}</span>
                      <span className="text-muted-foreground ml-1">In Progress</span>
                    </div>
                  )}
                  {stats.failed > 0 && (
                    <div className="text-sm">
                      <span className="font-medium text-red-600">{stats.failed}</span>
                      <span className="text-muted-foreground ml-1">Failed</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button onClick={loadUserContent} variant="outline" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button onClick={() => window.location.href = '/dashboard'} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Create New
                </Button>
              </div>
            </div>

            {/* Search and Filters */}
            <div className="bg-background rounded-xl border border-border p-4">
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
                <div className="flex flex-col sm:flex-row gap-3 flex-1">
                  {/* Search */}
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search content..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  
                  {/* Status Filter */}
                  <Select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="completed">Completed</option>
                    <option value="in_progress">In Progress</option>
                    <option value="failed">Failed</option>
                    <option value="pending">Pending</option>
                  </Select>
                  
                  {/* Sort */}
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="alphabetical">A-Z</option>
                    <option value="status">By Status</option>
                  </Select>
                </div>
                
                {/* View Mode Toggle */}
                <div className="flex items-center space-x-2">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid3X3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {/* Bulk Actions Bar */}
              {showBulkActions && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                  <div className="flex items-center space-x-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleSelectAll}
                    >
                      {selectedItems.size === filteredAndSortedContent.length ? (
                        <CheckSquare className="h-4 w-4 mr-2" />
                      ) : (
                        <Square className="h-4 w-4 mr-2" />
                      )}
                      {selectedItems.size === filteredAndSortedContent.length ? 'Deselect All' : 'Select All'}
                    </Button>
                    <span className="text-sm text-muted-foreground">
                      {selectedItems.size} item{selectedItems.size > 1 ? 's' : ''} selected
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleBulkDownload}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Selected
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Selected
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Content Grid/List */}
            {filteredAndSortedContent.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">
                    {content.length === 0 ? 'No content yet' : 'No matching content'}
                  </h3>
                  <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                    {content.length === 0 
                      ? "You haven't generated any content yet. Create your first blog article to get started!"
                      : "Try adjusting your search or filters to find what you're looking for."
                    }
                  </p>
                  {content.length === 0 && (
                    <Button onClick={() => window.location.href = '/dashboard'}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Your First Article
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              <div className={`grid gap-6 ${
                viewMode === 'grid' 
                  ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                  : 'grid-cols-1'
              }`}>
                {filteredAndSortedContent.map((item) => (
                  <ContentCard
                    key={item.id}
                    item={item}
                    onDownload={handleDownload}
                    onPreview={setPreviewItem}
                    isDownloading={downloadingIds.has(item.id)}
                    isSelected={selectedItems.has(item.id)}
                    onSelect={handleItemSelect}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
      
      {/* Preview Modal */}
      {previewItem && (
        <ContentPreviewModal
          isOpen={!!previewItem}
          onClose={() => setPreviewItem(null)}
          item={previewItem}
          onDownload={handleDownload}
          isDownloading={downloadingIds.has(previewItem.id)}
        />
      )}
    </div>
  )
}