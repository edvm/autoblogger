"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { cva, type VariantProps } from "class-variance-authority"

const avatarVariants = cva(
  "relative inline-flex items-center justify-center rounded-full transition-all duration-300",
  {
    variants: {
      state: {
        idle: "animate-gentle-pulse",
        thinking: "animate-pulse bg-gradient-to-br from-sage-green to-dusty-blue",
        working: "animate-spin bg-gradient-to-br from-soft-coral to-golden-yellow",
        celebrating: "animate-bounce bg-gradient-to-br from-golden-yellow to-sage-green",
        sleeping: "opacity-60 bg-gradient-to-br from-warm-gray to-dusty-blue/50",
      },
      size: {
        sm: "h-8 w-8",
        default: "h-12 w-12",
        lg: "h-16 w-16",
        xl: "h-24 w-24",
      },
    },
    defaultVariants: {
      state: "idle",
      size: "default",
    },
  }
)

export interface AIAssistantAvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {
  message?: string
}

const AIAssistantAvatar = React.forwardRef<HTMLDivElement, AIAssistantAvatarProps>(
  ({ className, state, size, message, ...props }, ref) => {
    return (
      <div className="flex flex-col items-center space-y-2">
        <div
          ref={ref}
          className={cn(avatarVariants({ state, size, className }))}
          {...props}
        >
          {/* Abstract geometric AI representation */}
          <div className="relative h-full w-full rounded-full bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm">
            {/* Inner circles for visual appeal */}
            <div className="absolute inset-2 rounded-full bg-gradient-to-br from-white/30 to-transparent" />
            <div className="absolute inset-4 rounded-full bg-gradient-to-br from-white/40 to-transparent" />
            
            {/* Central "brain" pattern */}
            <div className="absolute inset-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/90 shadow-lg" />
            
            {/* Orbital elements for AI thinking */}
            {state === "thinking" && (
              <>
                <div className="absolute inset-1 animate-spin rounded-full border-2 border-transparent border-t-white/50" />
                <div className="absolute inset-2 animate-spin rounded-full border border-transparent border-r-white/30" style={{ animationDirection: "reverse" }} />
              </>
            )}
            
            {/* Working indicators */}
            {state === "working" && (
              <div className="absolute inset-0 rounded-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
            )}
            
            {/* Celebration sparkles */}
            {state === "celebrating" && (
              <>
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-golden-yellow animate-ping" />
                <div className="absolute -bottom-1 -left-1 h-1.5 w-1.5 rounded-full bg-soft-coral animate-ping" style={{ animationDelay: "0.5s" }} />
                <div className="absolute top-0 left-1/2 h-1 w-1 rounded-full bg-sage-green animate-ping" style={{ animationDelay: "0.3s" }} />
              </>
            )}
          </div>
        </div>
        
        {/* Optional message display */}
        {message && (
          <div className="max-w-xs text-center">
            <p className="text-xs text-muted-foreground font-medium animate-fade-in">
              {message}
            </p>
          </div>
        )}
      </div>
    )
  }
)
AIAssistantAvatar.displayName = "AIAssistantAvatar"

export { AIAssistantAvatar, avatarVariants }