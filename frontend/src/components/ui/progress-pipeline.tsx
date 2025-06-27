"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Search, Edit3, CheckCircle, Clock } from "lucide-react"

export interface PipelineStage {
  id: string
  name: string
  friendlyName: string
  icon: React.ElementType
  status: "pending" | "in_progress" | "completed" | "error"
  message?: string
  duration?: number
}

export interface ProgressPipelineProps extends React.HTMLAttributes<HTMLDivElement> {
  stages: PipelineStage[]
  currentStage?: string
}

const ProgressPipeline = React.forwardRef<HTMLDivElement, ProgressPipelineProps>(
  ({ className, stages, currentStage, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("w-full space-y-6", className)}
        {...props}
      >
        {/* Pipeline Header */}
        <div className="text-center space-y-2">
          <h3 className="font-accent font-semibold text-lg text-deep-forest">
            Creating Your Article
          </h3>
          <p className="text-sm text-muted-foreground">
            Our AI assistants are working together to craft your perfect blog post
          </p>
        </div>

        {/* Pipeline Stages */}
        <div className="relative">
          {/* Connecting Line */}
          <div className="absolute left-8 top-12 bottom-0 w-0.5 bg-warm-gray" />
          
          <div className="space-y-8">
            {stages.map((stage, index) => {
              const Icon = stage.icon
              const isActive = stage.id === currentStage
              const isCompleted = stage.status === "completed"
              const isInProgress = stage.status === "in_progress"
              const hasError = stage.status === "error"
              
              return (
                <div key={stage.id} className="relative flex items-start space-x-4">
                  {/* Stage Icon */}
                  <div
                    className={cn(
                      "relative z-10 flex h-16 w-16 items-center justify-center rounded-full border-4 transition-all duration-300",
                      {
                        "border-sage-green bg-sage-green text-white shadow-lg": isCompleted,
                        "border-soft-coral bg-soft-coral text-white shadow-lg animate-pulse": isInProgress,
                        "border-warm-gray bg-warm-gray/50 text-muted-foreground": stage.status === "pending",
                        "border-destructive bg-destructive text-destructive-foreground": hasError,
                      }
                    )}
                  >
                    <Icon className="h-6 w-6" />
                    
                    {/* Active indicator */}
                    {isInProgress && (
                      <div className="absolute -inset-1 rounded-full border-2 border-soft-coral animate-ping" />
                    )}
                    
                    {/* Completion checkmark */}
                    {isCompleted && (
                      <div className="absolute -top-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full bg-success text-white">
                        <CheckCircle className="h-4 w-4" />
                      </div>
                    )}
                  </div>

                  {/* Stage Content */}
                  <div className="flex-1 min-w-0 pb-8">
                    <div
                      className={cn(
                        "rounded-xl border-2 p-6 transition-all duration-300",
                        {
                          "border-sage-green bg-sage-green/5 shadow-md": isCompleted,
                          "border-soft-coral bg-soft-coral/5 shadow-lg animate-pulse": isInProgress,
                          "border-warm-gray bg-warm-gray/20": stage.status === "pending",
                          "border-destructive bg-destructive/5": hasError,
                        }
                      )}
                    >
                      {/* Stage Header */}
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4
                            className={cn(
                              "font-accent font-semibold text-base",
                              {
                                "text-sage-green": isCompleted,
                                "text-soft-coral": isInProgress,
                                "text-muted-foreground": stage.status === "pending",
                                "text-destructive": hasError,
                              }
                            )}
                          >
                            {stage.friendlyName}
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            {stage.name}
                          </p>
                        </div>
                        
                        {/* Status indicator */}
                        <div className="flex items-center space-x-2">
                          {stage.duration && isCompleted && (
                            <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              <span>{stage.duration}s</span>
                            </div>
                          )}
                          
                          <div
                            className={cn(
                              "px-2 py-1 rounded-full text-xs font-medium",
                              {
                                "bg-success text-success-foreground": isCompleted,
                                "bg-soft-coral text-white": isInProgress,
                                "bg-warm-gray text-muted-foreground": stage.status === "pending",
                                "bg-destructive text-destructive-foreground": hasError,
                              }
                            )}
                          >
                            {isCompleted && "Complete"}
                            {isInProgress && "Working..."}
                            {stage.status === "pending" && "Waiting"}
                            {hasError && "Error"}
                          </div>
                        </div>
                      </div>

                      {/* Stage Message */}
                      {stage.message && (
                        <div className="mt-3 p-3 rounded-lg bg-warm-cream/50">
                          <p className="text-sm text-deep-forest">
                            {stage.message}
                          </p>
                        </div>
                      )}
                      
                      {/* Progress bar for active stage */}
                      {isInProgress && (
                        <div className="mt-4">
                          <div className="w-full bg-warm-gray rounded-full h-2">
                            <div 
                              className="bg-soft-coral h-2 rounded-full animate-pulse"
                              style={{ width: "60%" }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Pipeline Footer */}
        <div className="text-center p-4 rounded-xl bg-warm-gray/20">
          <p className="text-xs text-muted-foreground">
            Each assistant specializes in their area of expertise to create the best possible content for you
          </p>
        </div>
      </div>
    )
  }
)
ProgressPipeline.displayName = "ProgressPipeline"

// Default pipeline stages
export const defaultPipelineStages: PipelineStage[] = [
  {
    id: "research",
    name: "Research Assistant",
    friendlyName: "Exploring the Topic",
    icon: Search,
    status: "pending",
    message: "Gathering information and finding reliable sources...",
  },
  {
    id: "writing",
    name: "Writing Assistant", 
    friendlyName: "Crafting Your Content",
    icon: Edit3,
    status: "pending",
    message: "Creating engaging content based on research findings...",
  },
  {
    id: "editing",
    name: "Editing Assistant",
    friendlyName: "Polishing Your Article", 
    icon: CheckCircle,
    status: "pending",
    message: "Refining and perfecting the final article...",
  },
]

export { ProgressPipeline }