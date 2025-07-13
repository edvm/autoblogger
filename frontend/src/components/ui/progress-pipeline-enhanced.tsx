"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { 
  Search, 
  Edit3, 
  CheckCircle, 
  Clock, 
  Sparkles,
  Loader2
} from "lucide-react"

interface PipelineStep {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  estimatedTime: number // in seconds
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  result?: string
}

interface ProgressPipelineProps {
  steps: PipelineStep[]
  currentStepIndex: number
  isActive: boolean
}

export function ProgressPipelineEnhanced({ 
  steps, 
  currentStepIndex, 
  isActive
}: ProgressPipelineProps) {
  const [timeElapsed, setTimeElapsed] = useState<{ [key: string]: number }>({})
  const [currentStepStartTime, setCurrentStepStartTime] = useState<number | null>(null)

  useEffect(() => {
    if (!isActive) return

    const interval = setInterval(() => {
      const now = Date.now()
      if (currentStepStartTime && currentStepIndex < steps.length) {
        const currentStep = steps[currentStepIndex]
        const elapsed = Math.floor((now - currentStepStartTime) / 1000)
        setTimeElapsed(prev => ({
          ...prev,
          [currentStep.id]: elapsed
        }))
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [isActive, currentStepIndex, currentStepStartTime, steps])

  useEffect(() => {
    if (isActive && currentStepIndex < steps.length) {
      setCurrentStepStartTime(Date.now())
    }
  }, [currentStepIndex, isActive, steps.length])

  const getStepStatus = (index: number) => {
    if (index < currentStepIndex) return 'completed'
    if (index === currentStepIndex && isActive) return 'in_progress'
    return 'pending'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-success bg-success/10'
      case 'in_progress':
        return 'text-info bg-info/10'
      case 'error':
        return 'text-destructive bg-destructive/10'
      default:
        return 'text-muted-foreground bg-muted'
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  const getCurrentStepProgress = () => {
    if (!isActive || currentStepIndex >= steps.length) return 0
    const currentStep = steps[currentStepIndex]
    const elapsed = timeElapsed[currentStep.id] || 0
    const estimated = currentStep.estimatedTime
    return Math.min((elapsed / estimated) * 100, 95)
  }

  const totalProgress = isActive && currentStepIndex < steps.length
    ? ((currentStepIndex / steps.length) * 100) + (getCurrentStepProgress() / steps.length)
    : (currentStepIndex / steps.length) * 100

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Overall Progress */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-foreground">
            AI Content Generation Pipeline
          </h3>
          <span className="text-sm text-muted-foreground">
            {Math.round(totalProgress)}% Complete
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-3">
          <div 
            className="bg-gradient-brand h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${totalProgress}%` }}
          />
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-6">
        {steps.map((step, index) => {
          const Icon = step.icon
          const status = getStepStatus(index)
          const elapsed = timeElapsed[step.id] || 0
          const estimated = step.estimatedTime
          const getProgressPercent = () => {
            if (status === 'completed') return 100
            if (status !== 'in_progress') return 0
            
            // More realistic progress curve - starts fast, then slows down
            const rawProgress = (elapsed / estimated) * 100
            if (rawProgress <= 20) return rawProgress * 2 // Quick start (0-40%)
            if (rawProgress <= 60) return 40 + (rawProgress - 20) * 1.25 // Steady middle (40-90%)
            return Math.min(90 + (rawProgress - 60) * 0.25, 95) // Slow finish (90-95%)
          }
          
          const progressPercent = getProgressPercent()

          return (
            <Card 
              key={step.id}
              className={`transition-all duration-500 ${
                status === 'in_progress' 
                  ? 'ring-2 ring-info shadow-lg scale-[1.02]' 
                  : status === 'completed'
                  ? 'ring-2 ring-success shadow-md'
                  : status === 'pending' && isActive
                  ? 'shadow-sm ring-1 ring-muted-foreground/20 hover:shadow-md transform transition-all duration-300'
                  : 'shadow-sm'
              }`}
            >
              <CardContent className="p-6 sm:p-8">
                <div className="flex items-start space-x-5">
                  {/* Step Icon & Number */}
                  <div className="flex-shrink-0 pt-1">
                    <div className={`relative w-16 h-16 rounded-2xl flex items-center justify-center ${getStatusColor(status)} ${
                      status === 'pending' && isActive ? 'animate-pulse' : ''
                    }`}>
                      {status === 'completed' ? (
                        <CheckCircle className="h-8 w-8" />
                      ) : status === 'in_progress' ? (
                        <div className="relative">
                          <Icon className="h-8 w-8" />
                          <div className="absolute -inset-1">
                            <div className="w-full h-full border-2 border-blue-400 rounded-2xl animate-pulse" />
                          </div>
                        </div>
                      ) : (
                        <Icon className={`h-8 w-8 ${status === 'pending' && isActive ? 'text-muted-foreground/70' : ''}`} />
                      )}
                      
                      {/* Step Number Badge */}
                      <div className="absolute -top-2 -right-2 w-7 h-7 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs font-bold shadow-sm">
                        {index + 1}
                      </div>
                    </div>
                  </div>

                  {/* Step Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-3">
                      <h4 className="text-xl font-semibold text-foreground leading-tight">
                        {step.title}
                      </h4>
                      
                      {/* Status & Timing */}
                      <div className="flex items-center space-x-3 text-sm">
                        {status === 'in_progress' && (
                          <div className="flex items-center space-x-1">
                            <Loader2 className="h-4 w-4 animate-spin text-info" />
                            <span className="text-info font-medium">Working...</span>
                          </div>
                        )}
                        
                        {status === 'completed' && (
                          <div className="flex items-center space-x-1 text-success">
                            <CheckCircle className="h-4 w-4" />
                            <span className="font-medium">Complete</span>
                          </div>
                        )}

                        <div className="flex items-center space-x-1 text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span>
                            {status === 'in_progress' || status === 'completed' 
                              ? formatTime(elapsed)
                              : `~${formatTime(estimated)}`
                            }
                          </span>
                        </div>
                      </div>
                    </div>

                    <p className={`mb-4 text-base leading-relaxed ${
                      status === 'pending' && isActive 
                        ? 'text-muted-foreground/60' 
                        : 'text-muted-foreground'
                    }`}>
                      {step.description}
                    </p>

                    {/* Progress Bar for Current Step */}
                    {status === 'in_progress' && (
                      <div className="mb-3">
                        <div className="w-full bg-muted rounded-full h-2">
                          <div 
                            className="bg-gradient-to-r from-info to-primary h-2 rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${progressPercent}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground mt-1">
                          <span>Processing...</span>
                          <span>{Math.round(progressPercent)}%</span>
                        </div>
                      </div>
                    )}

                    {/* Step Result */}
                    {step.result && status === 'completed' && (
                      <div className="mt-3 p-3 bg-success/10 rounded-lg border-l-4 border-success">
                        <p className="text-sm text-success">
                          <span className="font-medium">Result:</span> {step.result}
                        </p>
                      </div>
                    )}

                    {/* Simulated AI Insights */}
                    {status === 'in_progress' && (
                      <div className="mt-3 p-3 bg-info/10 rounded-lg">
                        <div className="flex items-center space-x-2 text-info">
                          <Sparkles className="h-4 w-4 animate-pulse" />
                          <span className="text-sm font-medium">
                            {index === 0 && "Analyzing trending topics and gathering relevant data..."}
                            {index === 1 && "Crafting engaging content with optimal structure..."}
                            {index === 2 && "Fine-tuning tone and ensuring quality standards..."}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Next up indicator for pending steps during active generation */}
                    {status === 'pending' && isActive && index === currentStepIndex + 1 && (
                      <div className="mt-3 p-3 bg-muted/50 rounded-lg border-l-2 border-muted-foreground/30">
                        <div className="flex items-center space-x-2 text-muted-foreground">
                          <Clock className="h-4 w-4" />
                          <span className="text-sm font-medium">Coming up next</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Connection Line */}
                  {index < steps.length - 1 && (
                    <div className="absolute left-8 mt-24 w-0.5 h-12 bg-gradient-to-b from-border via-border/50 to-border opacity-60" />
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Final Status */}
      {currentStepIndex >= steps.length && (
        <Card className="mt-6 border-success bg-success/10">
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center space-x-3 mb-3">
              <div className="w-16 h-16 bg-success rounded-full flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-success-foreground" />
              </div>
            </div>
            <h3 className="text-xl font-bold text-success mb-2">
              Content Generation Complete!
            </h3>
            <p className="text-success/80">
              Your AI-generated content is ready. Time to share it with the world!
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Default steps configuration
export const defaultPipelineSteps: PipelineStep[] = [
  {
    id: 'research',
    title: 'Research & Discovery',
    description: 'AI is researching your topic, analyzing trends, and gathering relevant information from trusted sources.',
    icon: Search,
    estimatedTime: 45,
    status: 'pending'
  },
  {
    id: 'writing',
    title: 'Content Creation',
    description: 'AI is crafting your content with engaging structure, compelling hooks, and optimized formatting.',
    icon: Edit3,
    estimatedTime: 60,
    status: 'pending'
  },
  {
    id: 'editing',
    title: 'Review & Polish',
    description: 'AI is reviewing, fact-checking, and perfecting your content for maximum impact.',
    icon: CheckCircle,
    estimatedTime: 30,
    status: 'pending'
  }
]