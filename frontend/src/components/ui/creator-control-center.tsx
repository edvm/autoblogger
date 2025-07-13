"use client"

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { type CreditBalance } from "@/lib/api"
import { 
  Sparkles, 
  Wand2,
  Zap,
  FileText,
  Instagram,
  Video,
  Mail,
  TrendingUp,
  TrendingDown,
  Shield,
  Star,
  Plus,
  ArrowRight,
  Clock,
  Brain,
  CheckCircle,
  AlertTriangle,
  Loader2
} from "lucide-react"

interface CreatorControlCenterProps {
  balance: CreditBalance | null
  onCreateContent: (data: ContentCreationData) => void
  onPurchaseCredits: () => void
  isGenerating?: boolean
  className?: string
}

export interface ContentCreationData {
  mode: 'wizard' | 'quick'
  contentType: 'blog_article' | 'social_post' | 'video_script' | 'email_content'
  topic: string
  credits: number
}

interface ContentType {
  id: 'blog_article' | 'social_post' | 'video_script' | 'email_content'
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  credits: number
  time: string
  gradient: string
  available: boolean
  comingSoon?: boolean
}

const contentTypes: ContentType[] = [
  {
    id: 'blog_article',
    name: 'Blog Article',
    description: 'SEO-optimized long-form content',
    icon: FileText,
    credits: 10,
    time: '5 min',
    gradient: 'from-blue-500 to-blue-600',
    available: true
  },
  {
    id: 'social_post',
    name: 'Social Post',
    description: 'Viral captions + hashtags',
    icon: Instagram,
    credits: 5,
    time: '2 min',
    gradient: 'from-pink-500 to-rose-500',
    available: false,
    comingSoon: true
  },
  {
    id: 'video_script',
    name: 'Video Script',
    description: 'YouTube/TikTok scripts',
    icon: Video,
    credits: 8,
    time: '3 min',
    gradient: 'from-red-500 to-red-600',
    available: false,
    comingSoon: true
  },
  {
    id: 'email_content',
    name: 'Email Content',
    description: 'Newsletter & campaigns',
    icon: Mail,
    credits: 6,
    time: '3 min',
    gradient: 'from-green-500 to-green-600',
    available: false,
    comingSoon: true
  }
]

export function CreatorControlCenter({ 
  balance, 
  onCreateContent, 
  onPurchaseCredits,
  isGenerating = false,
  className = "" 
}: CreatorControlCenterProps) {
  const [mode, setMode] = useState<'wizard' | 'quick'>('quick')
  const [selectedType, setSelectedType] = useState<ContentType>(contentTypes[0])
  const [topic, setTopic] = useState('')
  const [animatedBalance, setAnimatedBalance] = useState(0)
  const [mounted, setMounted] = useState(false)
  
  const currentCredits = balance?.credits || 0
  const canAfford = currentCredits >= selectedType.credits
  const remainingCredits = currentCredits - selectedType.credits

  useEffect(() => {
    setMounted(true)
    const timer = setTimeout(() => {
      setAnimatedBalance(currentCredits)
    }, 100)
    return () => clearTimeout(timer)
  }, [currentCredits])

  // Calculate credit status for visual feedback
  const getCreditStatus = () => {
    if (currentCredits >= 500) return { 
      status: 'excellent', 
      color: 'text-green-600', 
      bg: 'bg-green-50 dark:bg-green-900/20',
      icon: CheckCircle 
    }
    if (currentCredits >= 200) return { 
      status: 'good', 
      color: 'text-blue-600', 
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      icon: Shield 
    }
    if (currentCredits >= 50) return { 
      status: 'fair', 
      color: 'text-yellow-600', 
      bg: 'bg-yellow-50 dark:bg-yellow-900/20',
      icon: AlertTriangle 
    }
    return { 
      status: 'low', 
      color: 'text-red-600', 
      bg: 'bg-red-50 dark:bg-red-900/20',
      icon: AlertTriangle 
    }
  }

  const creditStatus = getCreditStatus()
  const StatusIcon = creditStatus.icon

  // Generate random trend for demo (in real app, this would come from API)
  const recentTrend = useMemo(() => Math.random() > 0.5 ? 'up' : 'down', [])
  const trendPercent = useMemo(() => Math.floor(Math.random() * 25) + 5, [])

  const handleCreate = async () => {
    if (!topic.trim() || !canAfford || isGenerating) return

    const data: ContentCreationData = {
      mode,
      contentType: selectedType.id,
      topic: topic.trim(),
      credits: selectedType.credits
    }

    await onCreateContent(data)
  }

  const getCreateButtonText = () => {
    if (isGenerating) return 'Creating...'
    if (!topic.trim()) return 'Enter a topic'
    if (!canAfford) return 'Not enough credits'
    if (mode === 'wizard') return 'Start Wizard'
    return `Create ${selectedType.name}`
  }

  const getCreateButtonIcon = () => {
    if (isGenerating) return Loader2
    if (mode === 'wizard') return Wand2
    return selectedType.icon
  }

  const CreateButtonIcon = getCreateButtonIcon()

  if (!mounted) {
    return (
      <Card className={`border-2 border-muted ${className}`}>
        <CardContent className="p-8">
          <div className="animate-pulse space-y-6">
            <div className="h-20 bg-muted rounded-2xl"></div>
            <div className="h-32 bg-muted rounded-xl"></div>
            <div className="h-16 bg-muted rounded-xl"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={`relative overflow-hidden border-0 bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 shadow-2xl ${className}`}>
      <CardContent className="p-0">
        
        {/* Credit Status Bar */}
        <div className="relative bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 text-white p-6">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-2 right-4">
              <Sparkles className="h-16 w-16" />
            </div>
            <div className="absolute bottom-2 left-4">
              <div className="grid grid-cols-6 gap-1">
                {Array.from({ length: 18 }).map((_, i) => (
                  <div key={i} className="w-1.5 h-1.5 bg-white rounded-full opacity-30"></div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div>
                  <div className="text-white/80 text-sm">Creator Control Center</div>
                  <div className="text-white font-semibold">{balance?.email || 'Creator'}</div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-white/80 text-xs">Status</div>
                  <div className="flex items-center space-x-1">
                    <StatusIcon className="h-3 w-3 text-white" />
                    <span className="text-white text-sm font-medium capitalize">{creditStatus.status}</span>
                  </div>
                </div>
                <Button 
                  onClick={onPurchaseCredits}
                  size="lg"
                  className="bg-white/20 hover:bg-white/30 text-white backdrop-blur-sm border-white/30"
                >
                  <Plus className="h-3 w-3 mr-1" />
                  Add Credits
                </Button>
              </div>
            </div>
            
            {/* Balance Display */}
            <div className="flex items-baseline space-x-4">
              <div className="text-4xl font-bold text-white">
                {animatedBalance.toLocaleString()}
              </div>
              <div className="text-white/80 text-sm">credits</div>
              <div className="flex items-center space-x-1 text-white/70 text-sm">
                {recentTrend === 'up' ? (
                  <TrendingUp className="h-4 w-4 text-green-300" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-300" />
                )}
                <span>{trendPercent}% vs last month</span>
              </div>
            </div>
          </div>
        </div>

        {/* Creation Hub */}
        <div className="p-6 space-y-6">
          
          {/* Mode Toggle */}
          <div className="flex items-center justify-center">
            <div className="bg-muted rounded-xl p-1 flex space-x-1">
              <Button
                variant={mode === 'quick' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setMode('quick')}
                className={`flex items-center space-x-2 ${
                  mode === 'quick' 
                    ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-md' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Zap className="h-4 w-4" />
                <span>Quick Create</span>
              </Button>
              <Button
                variant={mode === 'wizard' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setMode('wizard')}
                className={`flex items-center space-x-2 ${
                  mode === 'wizard' 
                    ? 'bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-md' 
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Wand2 className="h-4 w-4" />
                <span>Smart Wizard</span>
              </Button>
            </div>
          </div>

          {/* Content Type Selector - Only for Quick Mode */}
          {mode === 'quick' && (
            <div className="space-y-3">
              <div className="text-sm font-medium text-foreground">Choose content type:</div>
              <div className="grid grid-cols-2 gap-3">
                {contentTypes.map((type) => {
                  const Icon = type.icon
                  const isSelected = selectedType.id === type.id
                  const isAffordable = currentCredits >= type.credits
                  
                  return (
                    <Button
                      key={type.id}
                      variant="ghost"
                      onClick={() => type.available && setSelectedType(type)}
                      disabled={!type.available || !isAffordable}
                      className={`relative h-auto p-4 justify-start space-x-3 transition-all duration-200 ${
                        isSelected 
                          ? 'bg-violet-50 border-2 border-violet-200 text-violet-700 dark:bg-violet-900/20 dark:border-violet-700' 
                          : 'border-2 border-transparent hover:border-violet-100 hover:bg-violet-50/50'
                      } ${
                        !type.available || !isAffordable ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      <div className={`w-10 h-10 bg-gradient-to-r ${type.gradient} rounded-lg flex items-center justify-center ${
                        !type.available ? 'grayscale' : ''
                      }`}>
                        <Icon className="h-5 w-5 text-white" />
                      </div>
                      <div className="flex-1 text-left">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-sm">{type.name}</span>
                          {type.comingSoon && (
                            <Badge variant="secondary" className="text-xs bg-amber-100 text-amber-800">
                              Soon
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground">{type.description}</div>
                        <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
                          <span className="font-medium">{type.credits} credits</span>
                          <span>•</span>
                          <span>{type.time}</span>
                        </div>
                      </div>
                      {isSelected && (
                        <div className="absolute top-2 right-2">
                          <CheckCircle className="h-4 w-4 text-violet-600" />
                        </div>
                      )}
                    </Button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Topic Input */}
          <div className="space-y-3">
            <div className="text-sm font-medium text-foreground">
              {mode === 'wizard' ? "What would you like to create?" : `What's your ${selectedType.name.toLowerCase()} about?`}
            </div>
            <Input
              autoFocus
              placeholder={
                mode === 'wizard' 
                  ? "e.g., 'I want to create content about sustainable living'"
                  : `e.g., '${selectedType.id === 'blog_article' ? 'Best productivity tips for remote workers' : selectedType.id === 'social_post' ? 'Motivational Monday post about goal setting' : selectedType.id === 'video_script' ? 'How to start a morning routine' : 'Weekly newsletter about industry trends'}'`
              }
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={isGenerating}
              className="text-base p-4 border-2 border-muted focus:border-violet-300 transition-colors"
            />
          </div>

          {/* Cost Preview & Action */}
          <div className="flex items-center justify-between p-4 bg-muted/30 rounded-xl">
            <div className="space-y-1">
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-muted-foreground">Cost:</span>
                <span className="font-medium text-foreground">
                  {mode === 'wizard' ? '10-15' : selectedType.credits} credits
                </span>
                {mode === 'quick' && (
                  <>
                    <span className="text-muted-foreground">•</span>
                    <div className="flex items-center space-x-1">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-muted-foreground">{selectedType.time}</span>
                    </div>
                  </>
                )}
              </div>
              {canAfford && topic.trim() && (
                <div className="text-xs text-muted-foreground">
                  {remainingCredits} credits remaining after creation
                </div>
              )}
              {!canAfford && (
                <div className="text-xs text-red-600 dark:text-red-400">
                  Need {selectedType.credits - currentCredits} more credits
                </div>
              )}
            </div>
            
            <Button
              onClick={handleCreate}
              disabled={!topic.trim() || !canAfford || isGenerating}
              size="lg"
              className={`font-semibold transition-all duration-300 ${
                canAfford && topic.trim()
                  ? 'bg-gradient-to-r from-violet-600 to-purple-600 hover:opacity-90 text-white shadow-lg hover:shadow-xl scale-100 hover:scale-105'
                  : 'bg-muted text-muted-foreground cursor-not-allowed'
              }`}
            >
              <CreateButtonIcon className={`h-4 w-4 mr-2 ${isGenerating ? 'animate-spin' : ''}`} />
              {getCreateButtonText()}
              {canAfford && topic.trim() && !isGenerating && (
                <ArrowRight className="h-4 w-4 ml-2" />
              )}
            </Button>
          </div>

          {/* Quick Stats */}
          {mode === 'quick' && (
            <div className="grid grid-cols-3 gap-4 pt-2">
              <div className="text-center">
                <div className="text-lg font-bold text-foreground">
                  {Math.floor(currentCredits / selectedType.credits)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {selectedType.name}s possible
                </div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-foreground">
                  {Math.floor(currentCredits / 15)}
                </div>
                <div className="text-xs text-muted-foreground">
                  Days at avg. rate
                </div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-foreground">
                  <Star className="h-4 w-4 inline text-amber-500" />
                </div>
                <div className="text-xs text-muted-foreground">
                  Premium member
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}