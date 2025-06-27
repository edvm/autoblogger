"use client"

import { useState, useEffect } from "react"
import { 
  Sparkles, 
  Clock,
  Loader2
} from "lucide-react"

interface SimpleProgressLoaderProps {
  currentStepIndex: number
  totalSteps: number
  isActive: boolean
  topic?: string
}

// Discord-style funny loading messages
const LOADING_MESSAGES = [
  // AI & Tech Humor
  "🤖 Teaching robots the art of storytelling...",
  "🎭 Convincing AI that grammar matters...",
  "🔮 Consulting the algorithm oracle...",
  "⚡ Charging creativity batteries...",
  "🎪 Training digital monkeys to type Shakespeare...",
  "🧠 Downloading thoughts from the cloud...",
  "💫 Calibrating the inspiration detector...",
  
  // Creative Process Humor
  "🎨 Mixing words in the idea blender...",
  "📚 Borrowing inspiration from the internet...",
  "✨ Sprinkling magic dust on your topic...",
  "🎯 Aiming creativity cannons...",
  "🎲 Rolling the dice of inspiration...",
  "🎪 Juggling adjectives and verbs...",
  "🍳 Cooking up fresh ideas...",
  
  // Silly & Unexpected
  "🦄 Unicorns are reviewing your content...",
  "🍕 Feeding ideas to hungry algorithms...",
  "🚀 Launching words into cyberspace...",
  "🎸 Tuning the creative frequencies...",
  "🎭 Rehearsing with the word theater troupe...",
  "🔥 Igniting the writing engines...",
  "🎨 Painting with digital brushstrokes...",
  
  // Whimsical Process
  "🌟 Collecting stardust for your story...",
  "🎪 Assembling the content circus...",
  "🧙‍♂️ Casting spell-check enchantments...",
  "🎢 Taking your ideas on a rollercoaster...",
  "🎯 Bullseye! Targeting the perfect words...",
  "🎭 Directing the narrative symphony...",
  "🚂 All aboard the content express..."
]

export function SimpleProgressLoader({ 
  currentStepIndex, 
  totalSteps, 
  isActive, 
  topic 
}: SimpleProgressLoaderProps) {
  const [currentMessage, setCurrentMessage] = useState(LOADING_MESSAGES[0])
  const [messageIndex, setMessageIndex] = useState(0)

  // Calculate progress percentage
  const progress = totalSteps > 0 ? Math.min((currentStepIndex / totalSteps) * 100, 95) : 0

  // Message rotation effect
  useEffect(() => {
    if (!isActive) return

    const interval = setInterval(() => {
      setMessageIndex(prev => {
        const nextIndex = (prev + 1) % LOADING_MESSAGES.length
        setCurrentMessage(LOADING_MESSAGES[nextIndex])
        return nextIndex
      })
    }, 3500) // Change message every 3.5 seconds

    return () => clearInterval(interval)
  }, [isActive])

  // Initialize with random message on mount
  useEffect(() => {
    const randomIndex = Math.floor(Math.random() * LOADING_MESSAGES.length)
    setMessageIndex(randomIndex)
    setCurrentMessage(LOADING_MESSAGES[randomIndex])
  }, [])

  if (!isActive) return null

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Animated Message */}
      <div className="text-center" role="status" aria-live="polite">
        <div className="min-h-[60px] flex items-center justify-center">
          <p 
            className="text-lg text-muted-foreground font-medium animate-fade-in transition-all duration-500"
            aria-label={`Loading status: ${currentMessage}`}
          >
            {currentMessage}
          </p>
        </div>
      </div>

      {/* Topic Reminder */}
      {topic && (
        <div className="bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-xl p-4 text-center">
          <h4 className="font-medium text-violet-800 dark:text-violet-200 mb-1">
            Creating content for:
          </h4>
          <p className="text-violet-700 dark:text-violet-300 font-medium">
            "{topic}"
          </p>
        </div>
      )}

      {/* Progress Bar */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-violet-500 animate-pulse" />
            <span className="text-sm font-medium text-foreground">
              Progress
            </span>
          </div>
          <span className="text-sm text-muted-foreground font-medium">
            {Math.round(progress)}%
          </span>
        </div>
        
        <div className="w-full bg-muted rounded-full h-3 overflow-hidden" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin={0} aria-valuemax={100}>
          <div 
            className="bg-gradient-to-r from-violet-500 to-purple-500 h-3 rounded-full transition-all duration-1000 ease-out shadow-sm"
            style={{ width: `${progress}%` }}
          >
            <div className="h-full w-full bg-gradient-to-r from-white/20 to-transparent rounded-full" />
          </div>
        </div>
      </div>

      {/* Estimated Time */}
      <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
        <Clock className="h-4 w-4" />
        <span>Estimated time: 3-5 minutes</span>
      </div>
    </div>
  )
}

