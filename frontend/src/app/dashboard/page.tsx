"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useAuth } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ContentWizard } from "@/components/ui/content-wizard"
import { BlogArticleModal } from "@/components/ui/blog-article-modal"
import { ProgressPipelineEnhanced, defaultPipelineSteps } from "@/components/ui/progress-pipeline-enhanced"
import { RecentArticles } from "@/components/ui/recent-articles"
import { CreatorControlCenter, type ContentCreationData } from "@/components/ui/creator-control-center"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { createApiClient, type User, type CreditBalance, type BloggerResponse, type BloggerRequest, type UserContentItem, type CreditTransaction } from "@/lib/api"
import { 
  Sparkles, 
  CreditCard, 
  Loader2, 
  RefreshCw, 
  Wand2, 
  Settings, 
  Instagram,
  Twitter,
  FileText,
  Video,
  Target,
  Zap,
  Crown,
  ArrowRight
} from "lucide-react"

export const dynamic = 'force-dynamic'

export default function Dashboard() {
  const { getToken } = useAuth()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  const router = useRouter()
  
  const [user, setUser] = useState<User | null>(null)
  const [credits, setCredits] = useState<CreditBalance | null>(null)
  const [transactions, setTransactions] = useState<CreditTransaction[]>([])
  const [recentArticles, setRecentArticles] = useState<UserContentItem[]>([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [currentGeneration, setCurrentGeneration] = useState<BloggerResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [articlesLoading, setArticlesLoading] = useState(true)
  const [showWizard, setShowWizard] = useState(false)
  const [wizardTopic, setWizardTopic] = useState('')
  const [showBlogModal, setShowBlogModal] = useState(false)
  const [blogModalTopic, setBlogModalTopic] = useState('')
  const [pipelineSteps] = useState(defaultPipelineSteps)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [blogCreationMode, setBlogCreationMode] = useState<'none' | 'simple' | 'expert'>('none')
  const [simpleTopic, setSimpleTopic] = useState('')
  
  // Quick action templates
  const quickActions = [
    {
      id: 'blog_article',
      title: 'Blog Article',
      description: 'SEO-optimized long-form content',
      icon: FileText,
      credits: 10,
      time: '5 min',
      gradient: 'from-violet-500 to-purple-500',
      available: true
    },
    {
      id: 'instagram_post',
      title: 'Instagram Post',
      description: 'Viral captions + hashtags',
      icon: Instagram,
      credits: 5,
      time: '2 min',
      gradient: 'from-pink-500 to-rose-500',
      available: false,
      comingSoon: true
    },
    {
      id: 'twitter_thread',
      title: 'Twitter Thread',
      description: 'Engaging thread content',
      icon: Twitter,
      credits: 5,
      time: '2 min',
      gradient: 'from-blue-500 to-cyan-500',
      available: false,
      comingSoon: true
    },
    {
      id: 'video_script',
      title: 'Video Script',
      description: 'YouTube/TikTok scripts',
      icon: Video,
      credits: 8,
      time: '3 min',
      gradient: 'from-red-500 to-pink-500',
      available: false,
      comingSoon: true
    }
  ]
  
  // Form state (keeping for advanced mode)
  const [formData, setFormData] = useState<BloggerRequest>({
    topic: "",
    search_depth: "basic",
    search_topic: "general",
    time_range: "month",
    days: 7,
    max_results: 5,
    include_domains: [],
    exclude_domains: [],
    include_answer: false,
    include_raw_content: false,
    include_images: false,
    timeout: 60
  })
  
  const [includeDomains, setIncludeDomains] = useState("")
  const [excludeDomains, setExcludeDomains] = useState("")

  const loadUserData = useCallback(async () => {
    try {
      const [userData, creditsData] = await Promise.all([
        api.getCurrentUser(),
        api.getCreditBalance()
      ])
      setUser(userData)
      setCredits(creditsData)
    } catch (error) {
      console.error("Failed to load user data:", error)
    } finally {
      setLoading(false)
    }
  }, [api])

  const loadRecentArticles = useCallback(async () => {
    try {
      const [articlesData, transactionsData] = await Promise.all([
        api.getUserContent(5, 0, 'blogger'),
        api.getCreditTransactions(10, 0)
      ])
      setRecentArticles(articlesData)
      setTransactions(transactionsData)
    } catch (error) {
      console.error("Failed to load recent articles:", error)
    } finally {
      setArticlesLoading(false)
    }
  }, [api])

  const handlePurchaseCredits = async (packageId: string) => {
    // Handle package purchase - this would integrate with payment processor
    console.log('Purchase package:', packageId)
    // After successful purchase, reload user data
    await loadUserData()
  }

  const handleViewArticle = (usageId: number) => {
    router.push(`/editor/${usageId}`)
  }

  const handleDownloadArticle = async (usageId: number) => {
    try {
      const blob = await api.downloadContent(usageId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `article-${usageId}.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download article:', error)
    }
  }

  const handleCreateContent = async (data: ContentCreationData) => {
    if (data.mode === 'wizard') {
      setWizardTopic(data.topic)
      setShowWizard(true)
      return
    }
    
    // Handle quick create mode - open BlogArticleModal with pre-filled topic
    setBlogModalTopic(data.topic)
    setShowBlogModal(true)
  }

  const checkGenerationStatus = useCallback(async () => {
    if (!currentGeneration) return
    
    try {
      const updated = await api.getBloggerUsageStatus(currentGeneration.usage_id)
      setCurrentGeneration(updated)
      
      if (updated.status === "completed" || updated.status === "failed") {
        setIsGenerating(false)
        setCurrentStepIndex(pipelineSteps.length) // Complete all steps
        await loadUserData() // Refresh credits
        
        // Modal will handle the completion flow - no auto-redirect here
      } else if (updated.status === "in_progress") {
        // Simulate step progression for better UX
        const elapsed = Date.now() - (updated.started_at ? new Date(updated.started_at).getTime() : Date.now())
        const elapsedSeconds = elapsed / 1000
        
        if (elapsedSeconds > 30 && currentStepIndex < 1) {
          setCurrentStepIndex(1)
        } else if (elapsedSeconds > 90 && currentStepIndex < 2) {
          setCurrentStepIndex(2)
        }
      }
    } catch (error) {
      console.error("Failed to check status:", error)
    }
  }, [api, currentGeneration, loadUserData, currentStepIndex, pipelineSteps.length, router])

  useEffect(() => {
    loadUserData()
    loadRecentArticles()
  }, [loadUserData, loadRecentArticles])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (currentGeneration && currentGeneration.status === "pending") {
      interval = setInterval(checkGenerationStatus, 3000)
    }
    return () => clearInterval(interval)
  }, [currentGeneration, checkGenerationStatus])

  const handleWizardComplete = async (wizardData: { topic: string }) => {
    setShowWizard(false)
    setWizardTopic('')
    setIsGenerating(true)
    setCurrentStepIndex(0)
    
    try {
      const requestData: BloggerRequest = {
        topic: wizardData.topic,
        search_depth: "advanced",
        search_topic: "general", 
        time_range: "month",
        days: 7,
        max_results: 5,
        include_domains: [],
        exclude_domains: [],
        include_answer: true,
        include_raw_content: false,
        include_images: true,
        timeout: 120
      }
      
      const response = await api.generateBlogPost(requestData)
      setCurrentGeneration(response)
    } catch (error) {
      console.error("Failed to generate content:", error)
      setIsGenerating(false)
    }
  }

  const handleQuickAction = async (actionType: string, topic: string) => {
    if (!topic.trim()) return

    setIsGenerating(true)
    setCurrentStepIndex(0)
    
    try {
      const requestData: BloggerRequest = {
        topic: topic.trim(),
        search_depth: "basic",
        search_topic: "general",
        time_range: "week",
        days: 7,
        max_results: 3,
        include_domains: [],
        exclude_domains: [],
        include_answer: false,
        include_raw_content: false,
        include_images: actionType === 'blog_article',
        timeout: 60
      }
      
      const response = await api.generateBlogPost(requestData)
      setCurrentGeneration(response)
    } catch (error) {
      console.error("Failed to generate content:", error)
      setIsGenerating(false)
    }
  }

  const handleBlogModalGenerate = async (data: BloggerRequest) => {
    // Don't close modal immediately - let it handle the generation flow
    setIsGenerating(true)
    setCurrentStepIndex(0)
    
    try {
      const response = await api.generateBlogPost(data)
      setCurrentGeneration(response)
      // Modal will handle the success state and transition
    } catch (error) {
      console.error("Failed to generate blog:", error)
      setIsGenerating(false)
      setShowBlogModal(false) // Close on error
    }
  }

  const handleModalTransitionToEditor = () => {
    setShowBlogModal(false)
    if (currentGeneration) {
      router.push(`/editor/${currentGeneration.usage_id}`)
    }
  }

  const handleGenerateBlog = async () => {
    if (!formData.topic.trim()) return

    setIsGenerating(true)
    setCurrentStepIndex(0)
    
    try {
      const requestData = {
        ...formData,
        topic: formData.topic.trim(),
        include_domains: includeDomains.trim() ? includeDomains.split(',').map(d => d.trim()).filter(d => d) : undefined,
        exclude_domains: excludeDomains.trim() ? excludeDomains.split(',').map(d => d.trim()).filter(d => d) : undefined
      }
      
      // Remove undefined values
      Object.keys(requestData).forEach(key => {
        if (requestData[key as keyof BloggerRequest] === undefined) {
          delete requestData[key as keyof BloggerRequest]
        }
      })
      
      const response = await api.generateBlogPost(requestData)
      setCurrentGeneration(response)
    } catch (error) {
      console.error("Failed to generate blog:", error)
      setIsGenerating(false)
    }
  }
  
  const handleInputChange = (field: keyof BloggerRequest, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
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
      
      {/* Wizard Modal */}
      {showWizard && (
        <ContentWizard 
          onComplete={handleWizardComplete}
          onCancel={() => {
            setShowWizard(false)
            setWizardTopic('')
          }}
          initialTopic={wizardTopic}
        />
      )}
      
      {/* Blog Article Modal */}
      {showBlogModal && (
        <BlogArticleModal
          isOpen={showBlogModal}
          onClose={() => {
            setShowBlogModal(false)
            setBlogModalTopic('')
          }}
          onGenerate={handleBlogModalGenerate}
          isGenerating={isGenerating}
          credits={credits?.credits || 0}
          generationResponse={currentGeneration}
          onTransitionToEditor={handleModalTransitionToEditor}
          initialTopic={blogModalTopic}
        />
      )}
      
      <main className={`flex-1 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 min-h-screen transition-all duration-200 ${showBlogModal ? 'blur-sm' : ''}`}>

        <div className="container py-8 max-w-7xl">

          {/* Hero Header */}
          <div className="mb-8">
            <div className="flex space-x-3 mb-4">
              <div className="w-16 h-16 bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 rounded-3xl flex items-center justify-center shadow-2xl">
                <Sparkles className="h-8 w-8 text-white" />
              </div>
              <div className="text-left">
                <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Dashboard
                </h1>
                <p className="text-lg text-muted-foreground">
                  Welcome back, {user?.first_name || user?.username || "Creator"}!
                </p>
              </div>
            </div>
          </div>


          {/* Creator Control Center - Unified Component */}
          <div className="mb-8">
            <CreatorControlCenter
              balance={credits}
              onCreateContent={handleCreateContent}
              onPurchaseCredits={() => router.push('/credits')}
              isGenerating={isGenerating}
            />
          </div>
          {/* Recent Articles */}
          <div className="mb-8">
            <RecentArticles
              articles={recentArticles}
              onViewArticle={handleViewArticle}
              onDownloadArticle={handleDownloadArticle}
              onCreateNew={() => setShowBlogModal(true)}
              loading={articlesLoading}
            />
          </div>

          {/* Main Dashboard Grid */}
          <div className="grid gap-8 lg:grid-cols-2 xl:grid-cols-3 mb-8">

            {/* Package Recommendations */}
            {/* <div className="xl:col-span-2">
              <PackageRecommendations
                balance={credits}
                transactions={transactions}
                onPackageSelect={handlePurchaseCredits}
              />
            </div> */}
            
          </div>

          {/* Quick Creation Options */}

          {/* Blog Article Creation Flow */}
          {blogCreationMode !== 'none' && (
            <Card className="mb-8 border-2 border-violet-200 bg-violet-50/50 dark:bg-violet-900/10">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-violet-500 to-purple-500 rounded-xl flex items-center justify-center">
                      <FileText className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-xl text-foreground">Create Blog Article</CardTitle>
                      <CardDescription className="text-base text-muted-foreground">
                        Generate SEO-optimized long-form content
                      </CardDescription>
                    </div>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => {
                      setBlogCreationMode('none')
                      setSimpleTopic('')
                      setFormData(prev => ({ ...prev, topic: '' }))
                    }}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    ✕
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Mode Selection */}
                {blogCreationMode === 'simple' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center space-x-4 mb-6">
                      <Button
                        variant={blogCreationMode === 'simple' ? 'default' : 'outline'}
                        onClick={() => setBlogCreationMode('simple')}
                        className="flex-1 bg-gradient-brand text-white"
                      >
                        <Zap className="mr-2 h-4 w-4" />
                        Quick Create
                      </Button>
                      <Button
                        variant={blogCreationMode === 'expert' ? 'default' : 'outline'}
                        onClick={() => setBlogCreationMode('expert')}
                        className="flex-1"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Expert Mode
                      </Button>
                    </div>
                    
                    {/* Simple Mode Form */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="simple-topic" className="text-lg font-semibold">
                          What&apos;s your blog article about? *
                        </Label>
                        <Input
                          id="simple-topic"
                          placeholder="e.g., 'Best productivity tips for remote workers' or 'How to start a small business'"
                          value={simpleTopic}
                          onChange={(e) => setSimpleTopic(e.target.value)}
                          disabled={isGenerating}
                          className="text-lg p-4"
                        />
                      </div>
                      
                      <div className="flex items-center justify-between pt-4">
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium text-violet-600">10 credits</span> • ~5 minutes
                        </div>
                        <Button
                          onClick={() => {
                            if (simpleTopic.trim()) {
                              handleQuickAction('blog_article', simpleTopic.trim())
                              setBlogCreationMode('none')
                              setSimpleTopic('')
                            }
                          }}
                          disabled={isGenerating || !simpleTopic.trim() || (credits?.credits || 0) < 10}
                          size="lg"
                          className="bg-gradient-brand hover:opacity-90 text-white px-8"
                        >
                          {isGenerating ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <Sparkles className="h-4 w-4 mr-2" />
                              Create Article
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Expert Mode Selection Button */}
                {blogCreationMode === 'expert' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center space-x-4 mb-6">
                      <Button
                        variant={blogCreationMode === 'simple' ? 'default' : 'outline'}
                        onClick={() => setBlogCreationMode('simple')}
                        className="flex-1"
                      >
                        <Zap className="mr-2 h-4 w-4" />
                        Quick Create
                      </Button>
                      <Button
                        variant={blogCreationMode === 'expert' ? 'default' : 'outline'}
                        onClick={() => setBlogCreationMode('expert')}
                        className="flex-1 bg-gradient-brand text-white"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Expert Mode
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Expert Mode - Integrated Advanced Form */}
          {blogCreationMode === 'expert' && (
            <Card className="mb-8 border border-violet-200 bg-white dark:bg-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-violet-700 dark:text-violet-300">
                  <Settings className="h-5 w-5" />
                  <span>Expert Blog Generation</span>
                </CardTitle>
                <CardDescription className="text-muted-foreground">
                  Fine-tune every aspect of your content generation process
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Basic Fields */}
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="topic">Blog Topic *</Label>
                    <Input
                      id="topic"
                      placeholder="Enter your blog topic..."
                      value={formData.topic}
                      onChange={(e) => handleInputChange('topic', e.target.value)}
                      disabled={isGenerating}
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="search_depth">Search Depth</Label>
                      <Select
                        id="search_depth"
                        value={formData.search_depth}
                        onChange={(e) => handleInputChange('search_depth', e.target.value)}
                        disabled={isGenerating}
                      >
                        <option value="basic">Basic</option>
                        <option value="advanced">Advanced</option>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="search_topic">Search Topic</Label>
                      <Select
                        id="search_topic"
                        value={formData.search_topic}
                        onChange={(e) => handleInputChange('search_topic', e.target.value)}
                        disabled={isGenerating}
                      >
                        <option value="general">General</option>
                        <option value="news">News</option>
                        <option value="finance">Finance</option>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="time_range">Time Range</Label>
                      <Select
                        id="time_range"
                        value={formData.time_range}
                        onChange={(e) => handleInputChange('time_range', e.target.value)}
                        disabled={isGenerating}
                      >
                        <option value="day">Day</option>
                        <option value="week">Week</option>
                        <option value="month">Month</option>
                        <option value="year">Year</option>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="max_results">Max Results</Label>
                      <Input
                        id="max_results"
                        type="number"
                        min="1"
                        max="20"
                        value={formData.max_results}
                        onChange={(e) => handleInputChange('max_results', parseInt(e.target.value) || 5)}
                        disabled={isGenerating}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="timeout">Timeout (seconds)</Label>
                      <Input
                        id="timeout"
                        type="number"
                        min="30"
                        max="300"
                        value={formData.timeout}
                        onChange={(e) => handleInputChange('timeout', parseInt(e.target.value) || 60)}
                        disabled={isGenerating}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Advanced Options Toggle */}
                <div className="border-t pt-4">
                  <div className="space-y-4 border rounded-lg p-4 bg-muted/20">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="include_domains">Include Domains</Label>
                        <Textarea
                          id="include_domains"
                          placeholder="example.com, site.org (comma-separated)"
                          value={includeDomains}
                          onChange={(e) => setIncludeDomains(e.target.value)}
                          disabled={isGenerating}
                          rows={3}
                        />
                        <p className="text-xs text-muted-foreground">
                          Limit search to specific domains (comma-separated)
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="exclude_domains">Exclude Domains</Label>
                        <Textarea
                          id="exclude_domains"
                          placeholder="spam.com, ads.net (comma-separated)"
                          value={excludeDomains}
                          onChange={(e) => setExcludeDomains(e.target.value)}
                          disabled={isGenerating}
                          rows={3}
                        />
                        <p className="text-xs text-muted-foreground">
                          Exclude specific domains from search (comma-separated)
                        </p>
                      </div>
                    </div>
                    
                    <div className="space-y-3">
                      <Label>Search Options</Label>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="include_answer"
                            checked={formData.include_answer}
                            onChange={(e) => handleInputChange('include_answer', e.target.checked)}
                            disabled={isGenerating}
                          />
                          <Label htmlFor="include_answer" className="text-sm font-normal">
                            Include direct answers
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="include_raw_content"
                            checked={formData.include_raw_content}
                            onChange={(e) => handleInputChange('include_raw_content', e.target.checked)}
                            disabled={isGenerating}
                          />
                          <Label htmlFor="include_raw_content" className="text-sm font-normal">
                            Include raw content
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id="include_images"
                            checked={formData.include_images}
                            onChange={(e) => handleInputChange('include_images', e.target.checked)}
                            disabled={isGenerating}
                          />
                          <Label htmlFor="include_images" className="text-sm font-normal">
                            Include images
                          </Label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Generate Button */}
                <div className="flex justify-between items-center">
                  <div>
                    {(credits?.credits || 0) < 10 && (
                      <p className="text-sm text-destructive">
                        Insufficient credits. You need 10 credits to generate a blog post.
                      </p>
                    )}
                  </div>
                  <Button
                    onClick={() => {
                      handleGenerateBlog()
                      setBlogCreationMode('none')
                    }}
                    disabled={isGenerating || !formData.topic.trim() || (credits?.credits || 0) < 10}
                    size="lg"
                    className="bg-gradient-brand hover:opacity-90 text-white px-8"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Generate Expert Article
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Generation Progress */}
          {isGenerating && (
            <div className="mb-8">
              <ProgressPipelineEnhanced
                steps={pipelineSteps}
                currentStepIndex={currentStepIndex}
                isActive={isGenerating}
              />
            </div>
          )}

          {/* Current Generation Results */}
          {currentGeneration && !isGenerating && (
            <Card className="mb-8 border-2 border-success/30 bg-success/5">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-success">
                  <Sparkles className="h-5 w-5" />
                  <span>Content Generated Successfully!</span>
                </CardTitle>
                <CardDescription className="text-success/80">
                  Your AI-generated content is ready to use
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {currentGeneration.error_message && (
                  <div className="p-4 bg-destructive/10 border border-destructive/30 rounded-md">
                    <p className="text-destructive">
                      {currentGeneration.error_message}
                    </p>
                  </div>
                )}

                {currentGeneration.final_content && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-lg text-success">
                        Your Generated Content:
                      </h4>
                      <Button 
                        onClick={() => navigator.clipboard.writeText(currentGeneration.final_content || '')}
                        variant="outline"
                        size="sm"
                        className="border-success/30 text-success hover:bg-success/10"
                      >
                        Copy to Clipboard
                      </Button>
                    </div>
                    <div className="max-h-96 overflow-y-auto p-6 bg-background rounded-xl border-2 border-success/20">
                      <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                        {currentGeneration.final_content}
                      </pre>
                    </div>
                  </div>
                )}

                {currentGeneration.sources && currentGeneration.sources.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-success">Sources Used:</h4>
                    <div className="grid gap-2">
                      {currentGeneration.sources.map((source, index) => (
                        <div key={index} className="p-3 bg-background rounded-lg border border-success/20">
                          <a 
                            href={source} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-info hover:text-info/80 text-sm break-all transition-colors"
                          >
                            {source}
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
          {/* Generation Progress */}
          {isGenerating && (
            <div className="mb-8">
              <ProgressPipelineEnhanced
                steps={pipelineSteps}
                currentStepIndex={currentStepIndex}
                isActive={isGenerating}
              />
            </div>
          )}

          {/* Current Generation Results */}
          {currentGeneration && !isGenerating && (
            <Card className="mb-8 border-2 border-green-200 bg-green-50/50 dark:bg-green-900/10">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 text-green-700 dark:text-green-300">
                  <Sparkles className="h-5 w-5" />
                  <span>Content Generated Successfully!</span>
                </CardTitle>
                <CardDescription className="text-green-600 dark:text-green-400">
                  Your AI-generated content is ready to use
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {currentGeneration.error_message && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-md dark:bg-red-900/20 dark:border-red-800">
                    <p className="text-red-700 dark:text-red-300">
                      {currentGeneration.error_message}
                    </p>
                  </div>
                )}

                {currentGeneration.final_content && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-lg text-green-700 dark:text-green-300">
                        Your Generated Content:
                      </h4>
                      <Button 
                        onClick={() => navigator.clipboard.writeText(currentGeneration.final_content || '')}
                        variant="outline"
                        size="sm"
                        className="border-green-300 text-green-700 hover:bg-green-50 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-900/20"
                      >
                        Copy to Clipboard
                      </Button>
                    </div>
                    <div className="max-h-96 overflow-y-auto p-6 bg-white rounded-xl border-2 border-green-200 dark:bg-slate-800 dark:border-green-700">
                      <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground">
                        {currentGeneration.final_content}
                      </pre>
                    </div>
                  </div>
                )}

                {currentGeneration.sources && currentGeneration.sources.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold text-green-700 dark:text-green-300">Sources Used:</h4>
                    <div className="grid gap-2">
                      {currentGeneration.sources.map((source, index) => (
                        <div key={index} className="p-3 bg-white rounded-lg border border-green-200 dark:bg-slate-800 dark:border-green-700">
                          <a 
                            href={source} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 text-sm break-all transition-colors dark:text-blue-400 dark:hover:text-blue-300"
                          >
                            {source}
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}