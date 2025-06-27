"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Copy, Download, ExternalLink, Check } from "lucide-react"

interface MarkdownViewerProps {
  content: string
  title?: string
  sources?: string[]
  className?: string
}

export function MarkdownViewer({ content, title, sources, className = "" }: MarkdownViewerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Failed to copy content:", error)
    }
  }

  const handleDownload = () => {
    const sanitizedTitle = (title || 'article')
      .replace(/[^a-zA-Z0-9\s\-_]/g, '')
      .replace(/\s+/g, '_')
      .toLowerCase()
    
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${sanitizedTitle}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // Simple markdown-to-HTML converter for basic formatting
  const formatContent = (text: string) => {
    let html = text
    
    // Headers
    html = html.replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold text-foreground mt-8 mb-4 first:mt-0">$1</h1>')
    html = html.replace(/^## (.*$)/gim, '<h2 class="text-2xl font-semibold text-foreground mt-6 mb-3">$1</h2>')
    html = html.replace(/^### (.*$)/gim, '<h3 class="text-xl font-medium text-foreground mt-5 mb-2">$1</h3>')
    html = html.replace(/^#### (.*$)/gim, '<h4 class="text-lg font-medium text-foreground mt-4 mb-2">$1</h4>')
    
    // Bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-foreground">$1</strong>')
    html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
    
    // Lists
    html = html.replace(/^\* (.*$)/gim, '<li class="ml-4 text-foreground">• $1</li>')
    html = html.replace(/^- (.*$)/gim, '<li class="ml-4 text-foreground">• $1</li>')
    html = html.replace(/^\d+\. (.*$)/gim, '<li class="ml-4 text-foreground list-decimal">$1</li>')
    
    // Links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">$1</a>')
    
    // Line breaks
    html = html.replace(/\n\n/g, '</p><p class="text-foreground leading-relaxed mb-4">')
    html = html.replace(/\n/g, '<br>')
    
    // Wrap in paragraphs
    html = `<p class="text-foreground leading-relaxed mb-4">${html}</p>`
    
    return html
  }

  return (
    <div className={`bg-background border border-border rounded-xl shadow-sm animate-in fade-in-0 slide-in-from-bottom-4 duration-700 ${className}`}>
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/30">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {title && (
              <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>
            )}
            <p className="text-sm text-muted-foreground">
              Generated Article • {content.split(' ').length} words
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="flex items-center space-x-1 transition-all duration-200 hover:scale-105"
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              <span>{copied ? 'Copied!' : 'Copy'}</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              className="flex items-center space-x-1 transition-all duration-200 hover:scale-105"
            >
              <Download className="h-4 w-4" />
              <span>Download</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 overflow-y-auto max-h-[calc(100vh-300px)]">
        <div 
          className="prose prose-slate dark:prose-invert max-w-none"
          dangerouslySetInnerHTML={{ __html: formatContent(content) }}
        />
      </div>

      {/* Sources */}
      {sources && sources.length > 0 && (
        <div className="border-t border-border p-4 bg-muted/30">
          <h4 className="font-medium text-foreground mb-3">Sources Referenced:</h4>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {sources.map((source, index) => (
              <div key={index} className="flex items-center space-x-2">
                <ExternalLink className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                <a 
                  href={source} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 truncate"
                >
                  {source}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}