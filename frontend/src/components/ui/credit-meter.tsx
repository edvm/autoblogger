"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Coins, TrendingUp, AlertTriangle } from "lucide-react"

export interface CreditMeterProps extends React.HTMLAttributes<HTMLDivElement> {
  currentCredits: number
  totalCredits?: number
  estimatedArticles?: number
  showWarning?: boolean
  variant?: "default" | "compact" | "detailed"
}

const CreditMeter = React.forwardRef<HTMLDivElement, CreditMeterProps>(
  ({ 
    className, 
    currentCredits, 
    totalCredits, 
    estimatedArticles, 
    showWarning = false,
    variant = "default",
    ...props 
  }, ref) => {
    const percentage = totalCredits ? (currentCredits / totalCredits) * 100 : 0
    const isLow = percentage < 20
    const isMedium = percentage < 50

    const getGradientColor = () => {
      if (isLow) return "from-destructive to-warning"
      if (isMedium) return "from-warning to-golden-yellow"
      return "from-sage-green to-dusty-blue"
    }

    const getTextColor = () => {
      if (isLow) return "text-destructive"
      if (isMedium) return "text-warning"
      return "text-sage-green"
    }

    if (variant === "compact") {
      return (
        <div
          ref={ref}
          className={cn("flex items-center space-x-3", className)}
          {...props}
        >
          <div className="relative">
            <Coins className={cn("h-5 w-5", getTextColor())} />
            {showWarning && isLow && (
              <AlertTriangle className="absolute -top-1 -right-1 h-3 w-3 text-destructive animate-pulse" />
            )}
          </div>
          <div className="flex flex-col">
            <span className={cn("font-semibold text-sm", getTextColor())}>
              {currentCredits.toLocaleString()}
            </span>
            {estimatedArticles && (
              <span className="text-xs text-muted-foreground">
                ~{estimatedArticles} articles
              </span>
            )}
          </div>
        </div>
      )
    }

    if (variant === "detailed") {
      return (
        <div
          ref={ref}
          className={cn("space-y-4 p-6 rounded-2xl bg-warm-gray/20", className)}
          {...props}
        >
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Coins className={cn("h-6 w-6", getTextColor())} />
              <h3 className="font-accent font-semibold text-lg">Credits</h3>
            </div>
            {showWarning && isLow && (
              <div className="flex items-center space-x-1 text-destructive">
                <AlertTriangle className="h-4 w-4" />
                <span className="text-sm font-medium">Low Balance</span>
              </div>
            )}
          </div>

          {/* Credit Display */}
          <div className="text-center space-y-2">
            <div className={cn("text-3xl font-bold font-accent", getTextColor())}>
              {currentCredits.toLocaleString()}
            </div>
            {totalCredits && (
              <div className="text-sm text-muted-foreground">
                of {totalCredits.toLocaleString()} total
              </div>
            )}
          </div>

          {/* Progress Bar */}
          {totalCredits && (
            <div className="space-y-2">
              <div className="w-full bg-warm-gray rounded-full h-3 overflow-hidden">
                <div
                  className={cn(
                    "h-full bg-gradient-to-r transition-all duration-500 ease-out",
                    getGradientColor()
                  )}
                  style={{ width: `${Math.max(percentage, 2)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0</span>
                <span>{Math.round(percentage)}%</span>
                <span>{totalCredits.toLocaleString()}</span>
              </div>
            </div>
          )}

          {/* Estimated Usage */}
          {estimatedArticles && (
            <div className="flex items-center justify-center space-x-2 p-3 rounded-lg bg-warm-cream/50">
              <TrendingUp className="h-4 w-4 text-sage-green" />
              <span className="text-sm text-deep-forest">
                Estimated <strong>{estimatedArticles}</strong> articles remaining
              </span>
            </div>
          )}

          {/* Low balance warning */}
          {showWarning && isLow && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20">
              <p className="text-sm text-destructive text-center">
                You&apos;re running low on credits. Consider purchasing more to continue creating content.
              </p>
            </div>
          )}
        </div>
      )
    }

    // Default variant
    return (
      <div
        ref={ref}
        className={cn("flex items-center space-x-4 p-4 rounded-xl bg-warm-gray/20", className)}
        {...props}
      >
        {/* Icon */}
        <div className="relative">
          <div className={cn(
            "flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br",
            getGradientColor()
          )}>
            <Coins className="h-6 w-6 text-white" />
          </div>
          {showWarning && isLow && (
            <AlertTriangle className="absolute -top-1 -right-1 h-4 w-4 text-destructive animate-pulse" />
          )}
        </div>

        {/* Content */}
        <div className="flex-1 space-y-1">
          <div className="flex items-baseline space-x-2">
            <span className={cn("text-2xl font-bold font-accent", getTextColor())}>
              {currentCredits.toLocaleString()}
            </span>
            <span className="text-sm text-muted-foreground">credits</span>
          </div>
          
          {estimatedArticles && (
            <div className="flex items-center space-x-1 text-sm text-muted-foreground">
              <TrendingUp className="h-3 w-3" />
              <span>~{estimatedArticles} articles remaining</span>
            </div>
          )}

          {/* Progress bar for default variant */}
          {totalCredits && (
            <div className="w-full bg-warm-gray rounded-full h-2 mt-2">
              <div
                className={cn(
                  "h-full bg-gradient-to-r transition-all duration-500 ease-out rounded-full",
                  getGradientColor()
                )}
                style={{ width: `${Math.max(percentage, 2)}%` }}
              />
            </div>
          )}
        </div>
      </div>
    )
  }
)
CreditMeter.displayName = "CreditMeter"

export { CreditMeter }