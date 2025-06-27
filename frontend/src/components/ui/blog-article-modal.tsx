"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { SimpleProgressLoader } from "@/components/ui/simple-progress-loader"
import { type BloggerRequest } from "@/lib/api"
import { 
  FileText,
  Settings,
  Zap,
  Sparkles,
  Loader2,
  ArrowRight,
  ArrowLeft,
  X,
  Target,
  Clock,
  CreditCard,
  CheckCircle,
  Wand2,
  Eye,
  ExternalLink,
  PartyPopper
} from "lucide-react"

interface BlogArticleModalProps {
  isOpen: boolean
  onClose: () => void
  onGenerate: (data: BloggerRequest, mode: 'simple' | 'expert') => void
  isGenerating: boolean
  credits: number
  generationResponse?: { final_content?: string; sources?: string[]; status?: string } | null
  onTransitionToEditor: () => void
  initialTopic?: string
}

export function BlogArticleModal({ 
  isOpen, 
  onClose, 
  onGenerate, 
  isGenerating, 
  credits,
  generationResponse,
  onTransitionToEditor,
  initialTopic = ""
}: BlogArticleModalProps) {
  const [step, setStep] = useState<'mode' | 'create' | 'generating' | 'success' | 'transitioning'>('mode')
  const [mode, setMode] = useState<'simple' | 'expert'>('simple')
  const [generationStartTime, setGenerationStartTime] = useState<number | null>(null)
  const [internalStepIndex, setInternalStepIndex] = useState(0)
  
  // Simple mode state
  const [simpleTopic, setSimpleTopic] = useState(initialTopic)
  
  // Expert mode state
  const [formData, setFormData] = useState<BloggerRequest>({
    topic: initialTopic,
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

  // Update form data when initialTopic changes
  useEffect(() => {
    setSimpleTopic(initialTopic)
    setFormData(prev => ({ ...prev, topic: initialTopic }))
  }, [initialTopic])
  
  const [includeDomains, setIncludeDomains] = useState("")
  const [excludeDomains, setExcludeDomains] = useState("")

  // Handle generation state transitions
  useEffect(() => {
    if (isGenerating && step !== 'generating') {
      setStep('generating')
      setGenerationStartTime(Date.now())
      setInternalStepIndex(0)
    } else if (!isGenerating && generationResponse && step === 'generating') {
      // Generation completed, show success state
      setInternalStepIndex(3) // Complete all steps
      setTimeout(() => {
        setStep('success')
      }, 500) // Small delay for smooth transition
    }
  }, [isGenerating, generationResponse, step])

  // Simulate progress steps during generation
  useEffect(() => {
    if (!isGenerating || step !== 'generating') return

    // Progressive timeouts for more realistic progress
    const step1Timer = setTimeout(() => {
      setInternalStepIndex(1) // Research phase
    }, 5000) // After 5 seconds

    const step2Timer = setTimeout(() => {
      setInternalStepIndex(2) // Writing phase  
    }, 45000) // After 45 seconds

    const step3Timer = setTimeout(() => {
      setInternalStepIndex(3) // Editing phase
    }, 90000) // After 1.5 minutes

    return () => {
      clearTimeout(step1Timer)
      clearTimeout(step2Timer)
      clearTimeout(step3Timer)
    }
  }, [isGenerating, step])

  const handleInputChange = (field: keyof BloggerRequest, value: string | number | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleGenerate = () => {
    if (mode === 'simple') {
      const simpleRequest: BloggerRequest = {
        topic: simpleTopic.trim(),
        search_depth: "basic",
        search_topic: "general",
        time_range: "week",
        days: 7,
        max_results: 3,
        include_domains: [],
        exclude_domains: [],
        include_answer: false,
        include_raw_content: false,
        include_images: true,
        timeout: 60
      }
      onGenerate(simpleRequest, 'simple')
    } else {
      const expertRequest = {
        ...formData,
        topic: formData.topic.trim(),
        include_domains: includeDomains.trim() ? includeDomains.split(',').map(d => d.trim()).filter(d => d) : [],
        exclude_domains: excludeDomains.trim() ? excludeDomains.split(',').map(d => d.trim()).filter(d => d) : []
      }
      onGenerate(expertRequest, 'expert')
    }
  }

  const canProceed = () => {
    if (step === 'mode') return true
    if (mode === 'simple') return simpleTopic.trim() !== ''
    return formData.topic.trim() !== ''
  }

  const resetModal = () => {
    setStep('mode')
    setMode('simple')
    setSimpleTopic('')
    setGenerationStartTime(null)
    setInternalStepIndex(0)
    setFormData({
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
    setIncludeDomains("")
    setExcludeDomains("")
  }

  const handleTransitionToEditor = () => {
    setStep('transitioning')
    setTimeout(() => {
      onTransitionToEditor()
      resetModal()
    }, 800) // Smooth transition timing
  }

  const handleClose = () => {
    // Don't allow closing during generation, success, or transition states
    if (!isGenerating && step !== 'generating' && step !== 'success' && step !== 'transitioning') {
      resetModal()
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-3xl modal-shadow-enhanced w-full max-w-4xl max-h-[95vh] overflow-hidden modal-border-enhanced modal-glow animate-in fade-in-0 zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-violet-600 to-purple-600 p-6 text-white relative overflow-hidden">
          {/* Background pattern for depth */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center ring-1 ring-white/20">
                  <FileText className="h-6 w-6 text-white drop-shadow-sm" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white drop-shadow-sm">Create Blog Article</h2>
                  <p className="text-violet-100 drop-shadow-sm">AI-powered content generation</p>
                </div>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleClose}
                disabled={isGenerating}
                className="text-white hover:bg-white/20 h-10 w-10 p-0 ring-1 ring-white/20 hover:ring-white/30 transition-all"
              >
                <X className="h-5 w-5 drop-shadow-sm" />
              </Button>
            </div>
            
            {/* Step indicator */}
            <div className="flex items-center space-x-1 sm:space-x-2 overflow-x-auto py-2 scrollbar-hide">
              <div className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-2 rounded-full transition-all duration-300 backdrop-blur-sm ${
                step === 'mode' ? 'bg-white/30 text-white ring-1 ring-white/20' : 'bg-white/10 text-white/80 hover:bg-white/15'
              }`}>
                <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold drop-shadow-sm">
                  1
                </div>
                <span className="text-xs sm:text-sm font-medium whitespace-nowrap drop-shadow-sm hidden xs:inline">Choose Mode</span>
                <span className="text-xs font-medium whitespace-nowrap drop-shadow-sm xs:hidden">Mode</span>
              </div>
            <ArrowRight className={`h-3 w-3 sm:h-4 sm:w-4 transition-colors drop-shadow-sm ${
              ['create', 'generating', 'success', 'transitioning'].includes(step) ? 'text-white' : 'text-white/60'
            }`} />
            <div className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-2 rounded-full transition-all duration-300 backdrop-blur-sm ${
              step === 'create' ? 'bg-white/30 text-white ring-1 ring-white/20' : 'bg-white/10 text-white/80 hover:bg-white/15'
            }`}>
              <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold drop-shadow-sm">
                2
              </div>
              <span className="text-xs sm:text-sm font-medium whitespace-nowrap drop-shadow-sm hidden xs:inline">Create Content</span>
              <span className="text-xs font-medium whitespace-nowrap drop-shadow-sm xs:hidden">Create</span>
            </div>
            <ArrowRight className={`h-3 w-3 sm:h-4 sm:w-4 transition-colors drop-shadow-sm ${
              ['generating', 'success', 'transitioning'].includes(step) ? 'text-white' : 'text-white/60'
            }`} />
            <div className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-2 rounded-full transition-all duration-300 backdrop-blur-sm ${
              step === 'generating' ? 'bg-white/30 text-white ring-1 ring-white/20' : 'bg-white/10 text-white/80 hover:bg-white/15'
            }`}>
              <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold drop-shadow-sm">
                {step === 'generating' ? <Loader2 className="h-2 w-2 sm:h-3 sm:w-3 animate-spin" /> : '3'}
              </div>
              <span className="text-xs sm:text-sm font-medium whitespace-nowrap drop-shadow-sm hidden xs:inline">Generating</span>
              <span className="text-xs font-medium whitespace-nowrap drop-shadow-sm xs:hidden">Gen</span>
            </div>
            <ArrowRight className={`h-3 w-3 sm:h-4 sm:w-4 transition-colors drop-shadow-sm ${
              ['success', 'transitioning'].includes(step) ? 'text-white' : 'text-white/60'
            }`} />
            <div className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-3 py-1 sm:py-2 rounded-full transition-all duration-300 backdrop-blur-sm ${
              ['success', 'transitioning'].includes(step) ? 'bg-white/30 text-white ring-1 ring-white/20' : 'bg-white/10 text-white/80 hover:bg-white/15'
            }`}>
              <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold drop-shadow-sm mt-0.5">
                {['success', 'transitioning'].includes(step) ? <CheckCircle className="h-2 w-2 sm:h-3 sm:w-3" /> : '4'}
              </div>
              <span className="text-xs sm:text-sm font-medium whitespace-nowrap drop-shadow-sm hidden xs:inline">Complete</span>
              <span className="text-xs font-medium whitespace-nowrap drop-shadow-sm xs:hidden">Done</span>
            </div>
            </div>
            
            {/* Credits display */}
            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-2">
                <CreditCard className="h-4 w-4 text-white/90 drop-shadow-sm" />
                <span className="text-sm text-white/90 drop-shadow-sm">Available Credits: </span>
                <span className="font-semibold text-white drop-shadow-sm">{credits}</span>
              </div>
              <div className="text-sm text-white/90 drop-shadow-sm">
                Cost: <span className="font-semibold text-white drop-shadow-sm">10 credits</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[calc(95vh-200px)]">
          {/* Step 1: Mode Selection */}
          {step === 'mode' && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  How would you like to create your article?
                </h3>
                <p className="text-muted-foreground text-lg">
                  Choose the approach that works best for you
                </p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                {/* Simple Mode */}
                <Card 
                  className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                    mode === 'simple' 
                      ? 'ring-2 ring-violet-500 bg-violet-50 dark:bg-violet-900/20' 
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => setMode('simple')}
                >
                  <CardHeader>
                    <div className="flex items-center space-x-3 mb-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        mode === 'simple' 
                          ? 'bg-violet-500 text-white' 
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        <Zap className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">Quick Create</CardTitle>
                        <CardDescription>Fast and easy article generation</CardDescription>
                      </div>
                    </div>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Target className="h-4 w-4" />
                        <span>Perfect for most topics</span>
                      </div>
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>~5 minutes generation time</span>
                      </div>
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Sparkles className="h-4 w-4" />
                        <span>AI-optimized settings</span>
                      </div>
                    </div>
                  </CardHeader>
                </Card>

                {/* Expert Mode */}
                <Card 
                  className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                    mode === 'expert' 
                      ? 'ring-2 ring-violet-500 bg-violet-50 dark:bg-violet-900/20' 
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => setMode('expert')}
                >
                  <CardHeader>
                    <div className="flex items-center space-x-3 mb-4">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                        mode === 'expert' 
                          ? 'bg-violet-500 text-white' 
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        <Settings className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">Expert Mode</CardTitle>
                        <CardDescription>Full control over generation</CardDescription>
                      </div>
                    </div>
                    
                    <div className="space-y-3 text-sm">
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Settings className="h-4 w-4" />
                        <span>Advanced customization</span>
                      </div>
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Target className="h-4 w-4" />
                        <span>Specific domain control</span>
                      </div>
                      <div className="flex items-center space-x-2 text-muted-foreground">
                        <Sparkles className="h-4 w-4" />
                        <span>Professional results</span>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </div>
            </div>
          )}

          {/* Step 2: Content Creation */}
          {step === 'create' && (
            <div className="space-y-6">
              {/* Mode indicator */}
              <div className="flex items-center justify-center mb-6">
                <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
                  mode === 'simple' 
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200'
                    : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200'
                }`}>
                  {mode === 'simple' ? <Zap className="h-4 w-4" /> : <Settings className="h-4 w-4" />}
                  <span className="font-medium">
                    {mode === 'simple' ? 'Quick Create Mode' : 'Expert Mode'}
                  </span>
                </div>
              </div>

              {/* Simple Mode Form */}
              {mode === 'simple' && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                      What&apos;s your article about?
                    </h3>
                    <p className="text-muted-foreground">
                      Just tell us your topic and we&apos;ll handle the rest
                    </p>
                  </div>
                  
                  <div className="space-y-4 max-w-2xl mx-auto">
                    <div className="space-y-2">
                      <Input
                        placeholder="e.g., 'Best productivity tips for remote workers' or 'How to start a small business'"
                        value={simpleTopic}
                        onChange={(e) => setSimpleTopic(e.target.value)}
                        disabled={isGenerating}
                        className="text-lg p-4 h-14"
                      />
                    </div>
                    
                    <div className="bg-muted/30 rounded-lg p-4">
                      <h4 className="font-medium text-sm text-foreground mb-2">What we&apos;ll include:</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm text-muted-foreground">
                        <div>• SEO-optimized content</div>
                        <div>• Recent research data</div>
                        <div>• Professional structure</div>
                        <div>• Relevant images</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Expert Mode Form */}
              {mode === 'expert' && (
                <div className="space-y-6">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                      Customize your article generation
                    </h3>
                    <p className="text-muted-foreground">
                      Fine-tune every aspect of the content creation process
                    </p>
                  </div>
                  
                  <div className="space-y-6 max-w-4xl mx-auto">
                    {/* Basic Fields */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="expert-topic" className="text-base font-medium">Article Topic *</Label>
                        <Input
                          id="expert-topic"
                          placeholder="Enter your article topic..."
                          value={formData.topic}
                          onChange={(e) => handleInputChange('topic', e.target.value)}
                          disabled={isGenerating}
                          className="text-lg p-4"
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
                    
                    {/* Advanced Options */}
                    <div className="border-t pt-6">
                      <h4 className="font-medium text-foreground mb-4">Advanced Options</h4>
                      <div className="space-y-4">
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
                  </div>
                </div>
              )}

              {/* Generation Progress - Now handled in Step 3 */}
            </div>
          )}

          {/* Step 3: Generation Progress */}
          {step === 'generating' && (
            <div className="space-y-6 text-center">
              <div className="flex items-center justify-center mb-8">
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-r from-violet-500 to-purple-500 rounded-full flex items-center justify-center shadow-lg">
                    <Wand2 className="h-12 w-12 text-white animate-spin" />
                  </div>
                  {/* Pulsing rings */}
                  <div className="absolute inset-0 rounded-full bg-violet-400/30 animate-ping" style={{ animationDuration: '2s' }} />
                  <div className="absolute inset-2 rounded-full bg-purple-400/20 animate-ping" style={{ animationDuration: '1.5s', animationDelay: '0.5s' }} />
                </div>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  Creating Your Article
                </h3>
                <p className="text-muted-foreground text-lg mb-6">
                  Our AI agents are researching, writing, and polishing your content
                </p>
              </div>

              {/* Simplified Progress Loader */}
              <SimpleProgressLoader
                currentStepIndex={internalStepIndex}
                totalSteps={3} // Research, Writing, Editing
                isActive={isGenerating}
                topic={mode === 'simple' ? simpleTopic : formData.topic}
              />
            </div>
          )}

          {/* Step 4: Success State */}
          {step === 'success' && (
            <div className="space-y-6 text-center">
              {/* Success Animation */}
              <div className="flex items-center justify-center mb-8">
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center animate-bounce shadow-lg">
                    <CheckCircle className="h-12 w-12 text-white drop-shadow-sm" />
                  </div>
                  {/* Celebration particles with staggered animations */}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <PartyPopper className="h-6 w-6 text-yellow-500 absolute -top-2 -left-2 animate-ping" style={{ animationDelay: '0s', animationDuration: '2s' }} />
                    <Sparkles className="h-4 w-4 text-blue-500 absolute -bottom-1 -right-2 animate-pulse" style={{ animationDelay: '0.5s', animationDuration: '1.5s' }} />
                    <Sparkles className="h-5 w-5 text-pink-500 absolute -top-1 right-0 animate-ping" style={{ animationDelay: '1s', animationDuration: '2.5s' }} />
                    <Sparkles className="h-3 w-3 text-purple-500 absolute bottom-0 -left-1 animate-pulse" style={{ animationDelay: '1.5s', animationDuration: '1.8s' }} />
                    <PartyPopper className="h-4 w-4 text-orange-500 absolute top-1 -right-3 animate-ping" style={{ animationDelay: '2s', animationDuration: '2.2s' }} />
                  </div>
                  {/* Ripple effect */}
                  <div className="absolute inset-0 rounded-full bg-green-500/20 animate-ping" style={{ animationDelay: '0.3s', animationDuration: '3s' }} />
                </div>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-green-600 mb-2">
                  Article Created Successfully!
                </h3>
                <p className="text-muted-foreground text-lg mb-6">
                  Your AI-generated content is ready for review and editing
                </p>
              </div>

              {/* Article Preview */}
              {generationResponse && (
                <div className="bg-background border border-border rounded-xl p-6 text-left">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold text-foreground">Content Preview</h4>
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>~{Math.ceil((generationResponse.final_content?.length || 0) / 100)} words</span>
                    </div>
                  </div>
                  <div className="max-h-48 overflow-y-auto bg-muted/30 rounded-lg p-4">
                    <p className="text-sm text-foreground leading-relaxed">
                      {generationResponse.final_content?.substring(0, 500)}
                      {(generationResponse.final_content?.length || 0) > 500 && '...'}
                    </p>
                  </div>
                </div>
              )}

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-green-600">
                    {generationResponse?.sources?.length || 0}
                  </div>
                  <div className="text-sm text-green-700 dark:text-green-300">Sources Used</div>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-600">
                    {Math.ceil(((Date.now() - (generationStartTime || Date.now())) / 1000) / 60)}m
                  </div>
                  <div className="text-sm text-blue-700 dark:text-blue-300">Generation Time</div>
                </div>
              </div>
            </div>
          )}

          {/* Step 5: Transition State */}
          {step === 'transitioning' && (
            <div className="space-y-6 text-center">
              <div className="flex items-center justify-center mb-8">
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center shadow-lg">
                    <ExternalLink className="h-12 w-12 text-white animate-pulse" />
                  </div>
                  {/* Transition rings */}
                  <div className="absolute inset-0 rounded-full bg-blue-400/30 animate-ping" style={{ animationDuration: '1.8s' }} />
                  <div className="absolute inset-3 rounded-full bg-indigo-400/20 animate-ping" style={{ animationDuration: '1.3s', animationDelay: '0.3s' }} />
                </div>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-foreground mb-2">
                  Opening Editor
                </h3>
                <p className="text-muted-foreground text-lg">
                  Taking you to the editor to review and refine your content
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-muted/30 p-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {step === 'create' && !isGenerating && (
              <Button 
                variant="outline" 
                onClick={() => setStep('mode')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back</span>
              </Button>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {/* Cancel button - only show in initial states */}
            {['mode', 'create'].includes(step) && !isGenerating && (
              <Button 
                variant="ghost" 
                onClick={handleClose}
                className="text-muted-foreground hover:text-foreground"
              >
                Cancel
              </Button>
            )}
            
            {/* Mode selection step */}
            {step === 'mode' && (
              <Button 
                onClick={() => setStep('create')}
                className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white px-8"
              >
                <span>Continue</span>
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
            
            {/* Create step */}
            {step === 'create' && (
              <Button 
                onClick={handleGenerate}
                disabled={isGenerating || !canProceed() || credits < 10}
                className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white px-8"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Article
                  </>
                )}
              </Button>
            )}

            {/* Generating step - no actions needed */}
            {step === 'generating' && (
              <div className="flex items-center space-x-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Please wait while we create your content...</span>
              </div>
            )}

            {/* Success step */}
            {step === 'success' && (
              <>
                <Button 
                  variant="outline"
                  onClick={() => {
                    if (generationResponse?.final_content) {
                      navigator.clipboard.writeText(generationResponse.final_content)
                    }
                  }}
                  className="flex items-center space-x-2"
                >
                  <FileText className="h-4 w-4" />
                  <span>Copy Content</span>
                </Button>
                <Button 
                  onClick={handleTransitionToEditor}
                  className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-8"
                >
                  <Eye className="h-4 w-4 mr-2" />
                  <span>Open in Editor</span>
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </>
            )}

            {/* Transitioning step */}
            {step === 'transitioning' && (
              <div className="flex items-center space-x-2 text-muted-foreground">
                <ExternalLink className="h-4 w-4 animate-pulse" />
                <span>Opening editor...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}