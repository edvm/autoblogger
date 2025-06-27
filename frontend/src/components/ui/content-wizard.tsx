"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { 
  ShoppingCart, 
  TrendingUp, 
  Crown, 
  Target, 
  Calendar,
  Instagram,
  Twitter,
  Youtube,
  FileText,
  Mail,
  Video,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  DollarSign,
  Heart,
  Users,
  Zap,
  CheckCircle
} from "lucide-react"

interface WizardStep {
  id: string
  title: string
  description: string
}

interface ContentGoal {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  examples: string[]
  platforms: string[]
}

interface ContentType {
  id: string
  title: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  creditCost: number
  estimatedTime: string
}

const contentGoals: ContentGoal[] = [
  {
    id: "sell_product",
    title: "Sell a Product",
    description: "Create content that converts browsers into buyers",
    icon: ShoppingCart,
    examples: ["Product launch posts", "Sales emails", "Landing page copy"],
    platforms: ["Instagram", "Facebook", "Email", "Website"]
  },
  {
    id: "go_viral",
    title: "Go Viral",
    description: "Create engaging content designed for maximum reach",
    icon: TrendingUp,
    examples: ["Trending topic posts", "Viral hooks", "Story-driven content"],
    platforms: ["TikTok", "Instagram", "Twitter", "YouTube"]
  },
  {
    id: "build_authority",
    title: "Build Authority",
    description: "Establish yourself as an expert in your niche",
    icon: Crown,
    examples: ["Thought leadership articles", "Expert insights", "Educational content"],
    platforms: ["LinkedIn", "Medium", "Blog", "Newsletter"]
  },
  {
    id: "drive_traffic",
    title: "Drive Traffic",
    description: "Create SEO-optimized content that ranks and converts",
    icon: Target,
    examples: ["SEO blog posts", "How-to guides", "Comparison articles"],
    platforms: ["Blog", "Website", "Google", "Pinterest"]
  },
  {
    id: "regular_content",
    title: "Regular Content",
    description: "Consistent content for ongoing audience engagement",
    icon: Calendar,
    examples: ["Daily posts", "Weekly newsletters", "Content series"],
    platforms: ["All platforms", "Content calendar", "Automation"]
  }
]

const contentTypes: ContentType[] = [
  {
    id: "instagram_post",
    title: "Instagram Post",
    description: "Captions, hashtags, and story content",
    icon: Instagram,
    creditCost: 5,
    estimatedTime: "2 mins"
  },
  {
    id: "twitter_thread",
    title: "Twitter Thread",
    description: "Engaging threads that spark conversation",
    icon: Twitter,
    creditCost: 5,
    estimatedTime: "2 mins"
  },
  {
    id: "video_script",
    title: "Video Script",
    description: "YouTube, TikTok, and Reel scripts",
    icon: Video,
    creditCost: 8,
    estimatedTime: "3 mins"
  },
  {
    id: "blog_article",
    title: "Blog Article",
    description: "Long-form, SEO-optimized articles",
    icon: FileText,
    creditCost: 10,
    estimatedTime: "5 mins"
  },
  {
    id: "email_newsletter",
    title: "Email Newsletter",
    description: "Engaging email content that converts",
    icon: Mail,
    creditCost: 6,
    estimatedTime: "3 mins"
  },
  {
    id: "youtube_description",
    title: "YouTube Description",
    description: "SEO-optimized video descriptions",
    icon: Youtube,
    creditCost: 4,
    estimatedTime: "2 mins"
  }
]

interface ContentWizardProps {
  onComplete: (data: any) => void
  onCancel: () => void
  initialTopic?: string
}

export function ContentWizard({ onComplete, onCancel, initialTopic = "" }: ContentWizardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null)
  const [selectedContentType, setSelectedContentType] = useState<string | null>(null)
  const [contentTopic, setContentTopic] = useState(initialTopic)
  const [additionalContext, setAdditionalContext] = useState("")
  const [targetAudience, setTargetAudience] = useState("")

  const steps: WizardStep[] = [
    {
      id: "goal",
      title: "What's Your Goal?",
      description: "Tell us what you want to achieve with your content"
    },
    {
      id: "content_type",
      title: "Content Type",
      description: "What type of content do you want to create?"
    },
    {
      id: "details",
      title: "Content Details",
      description: "Give us the details to create amazing content"
    },
    {
      id: "review",
      title: "Review & Generate",
      description: "Review your choices and generate your content"
    }
  ]

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 0: return selectedGoal !== null
      case 1: return selectedContentType !== null
      case 2: return contentTopic.trim() !== ""
      default: return true
    }
  }

  const handleComplete = () => {
    const wizardData = {
      goal: selectedGoal,
      contentType: selectedContentType,
      topic: contentTopic,
      additionalContext,
      targetAudience,
      isWizardFlow: true
    }
    onComplete(wizardData)
  }

  const selectedGoalData = contentGoals.find(g => g.id === selectedGoal)
  const selectedContentTypeData = contentTypes.find(c => c.id === selectedContentType)

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-3xl modal-shadow-enhanced w-full max-w-4xl max-h-[90vh] overflow-hidden modal-border-enhanced modal-glow">
        {/* Header */}
        <div className="bg-gradient-brand p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">Content Creation Wizard</h2>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={onCancel}
              className="text-white hover:bg-white/20"
            >
              ✕
            </Button>
          </div>
          
          {/* Progress bar */}
          <div className="flex items-center space-x-2">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index <= currentStep 
                    ? 'bg-white text-primary' 
                    : 'bg-white/30 text-white/70'
                }`}>
                  {index < currentStep ? <CheckCircle className="h-4 w-4" /> : index + 1}
                </div>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-1 mx-2 rounded ${
                    index < currentStep ? 'bg-white' : 'bg-white/30'
                  }`} />
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-4">
            <h3 className="text-xl font-semibold">{steps[currentStep].title}</h3>
            <p className="text-violet-100">{steps[currentStep].description}</p>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[60vh]">
          {/* Step 1: Goal Selection */}
          {currentStep === 0 && (
            <div className="grid gap-4 md:grid-cols-2">
              {contentGoals.map((goal) => {
                const Icon = goal.icon
                return (
                  <Card 
                    key={goal.id}
                    className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                      selectedGoal === goal.id 
                        ? 'ring-2 ring-violet-500 bg-violet-50 dark:bg-violet-900/20' 
                        : 'hover:bg-gray-50 dark:hover:bg-slate-800'
                    }`}
                    onClick={() => setSelectedGoal(goal.id)}
                  >
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <div className={`p-3 rounded-xl ${
                          selectedGoal === goal.id 
                            ? 'bg-violet-500 text-white' 
                            : 'bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300'
                        }`}>
                          <Icon className="h-6 w-6" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{goal.title}</CardTitle>
                          <CardDescription>{goal.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Examples:</p>
                          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                            {goal.examples.map((example, idx) => (
                              <li key={idx}>• {example}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Best for:</p>
                          <div className="flex flex-wrap gap-1">
                            {goal.platforms.map((platform, idx) => (
                              <span 
                                key={idx}
                                className="px-2 py-1 bg-gray-100 dark:bg-slate-700 text-xs rounded-full text-gray-600 dark:text-gray-300"
                              >
                                {platform}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}

          {/* Step 2: Content Type Selection */}
          {currentStep === 1 && (
            <div>
              {selectedGoalData && (
                <div className="mb-6 p-4 bg-violet-50 dark:bg-violet-900/20 rounded-xl">
                  <div className="flex items-center space-x-2 mb-2">
                    <selectedGoalData.icon className="h-5 w-5 text-violet-600" />
                    <span className="font-semibold text-violet-800 dark:text-violet-200">
                      Goal: {selectedGoalData.title}
                    </span>
                  </div>
                  <p className="text-sm text-violet-700 dark:text-violet-300">
                    {selectedGoalData.description}
                  </p>
                </div>
              )}
              
              <div className="grid gap-4 md:grid-cols-2">
                {contentTypes.map((type) => {
                  const Icon = type.icon
                  return (
                    <Card 
                      key={type.id}
                      className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                        selectedContentType === type.id 
                          ? 'ring-2 ring-violet-500 bg-violet-50 dark:bg-violet-900/20' 
                          : 'hover:bg-gray-50 dark:hover:bg-slate-800'
                      }`}
                      onClick={() => setSelectedContentType(type.id)}
                    >
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-3 rounded-xl ${
                              selectedContentType === type.id 
                                ? 'bg-violet-500 text-white' 
                                : 'bg-gray-100 dark:bg-slate-700 text-gray-600 dark:text-gray-300'
                            }`}>
                              <Icon className="h-6 w-6" />
                            </div>
                            <div>
                              <CardTitle className="text-lg">{type.title}</CardTitle>
                              <CardDescription>{type.description}</CardDescription>
                            </div>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between text-sm">
                          <span className="flex items-center space-x-1 text-green-600">
                            <Zap className="h-4 w-4" />
                            <span>{type.estimatedTime}</span>
                          </span>
                          <span className="flex items-center space-x-1 text-violet-600">
                            <span>{type.creditCost} credits</span>
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </div>
          )}

          {/* Step 3: Content Details */}
          {currentStep === 2 && (
            <div className="space-y-6">
              {selectedGoalData && selectedContentTypeData && (
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="p-4 bg-violet-50 dark:bg-violet-900/20 rounded-xl">
                    <div className="flex items-center space-x-2 mb-2">
                      <selectedGoalData.icon className="h-5 w-5 text-violet-600" />
                      <span className="font-semibold text-violet-800 dark:text-violet-200">
                        {selectedGoalData.title}
                      </span>
                    </div>
                  </div>
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
                    <div className="flex items-center space-x-2 mb-2">
                      <selectedContentTypeData.icon className="h-5 w-5 text-blue-600" />
                      <span className="font-semibold text-blue-800 dark:text-blue-200">
                        {selectedContentTypeData.title}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-4">
                <div>
                  <Label htmlFor="topic" className="text-lg font-semibold">
                    What's your topic? <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="topic"
                    placeholder="e.g., 'How to start a dropshipping business' or 'Best productivity tips for entrepreneurs'"
                    value={contentTopic}
                    onChange={(e) => setContentTopic(e.target.value)}
                    className="mt-2 text-lg p-4"
                  />
                </div>

                <div>
                  <Label htmlFor="audience" className="text-lg font-semibold">
                    Who's your target audience?
                  </Label>
                  <Input
                    id="audience"
                    placeholder="e.g., 'Small business owners', 'Fitness enthusiasts', 'Tech entrepreneurs'"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    className="mt-2 text-lg p-4"
                  />
                </div>

                <div>
                  <Label htmlFor="context" className="text-lg font-semibold">
                    Additional context or requirements
                  </Label>
                  <Textarea
                    id="context"
                    placeholder="Any specific points to cover, tone preferences, or special requirements..."
                    value={additionalContext}
                    onChange={(e) => setAdditionalContext(e.target.value)}
                    rows={4}
                    className="mt-2"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Review */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <Sparkles className="h-16 w-16 text-violet-500 mx-auto mb-4" />
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Ready to Create Amazing Content!
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Review your selections and we'll generate your content in minutes.
                </p>
              </div>

              <div className="grid gap-4">
                <Card className="border-violet-200 bg-violet-50 dark:bg-violet-900/20">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-3 mb-3">
                      {selectedGoalData && <selectedGoalData.icon className="h-6 w-6 text-violet-600" />}
                      <h4 className="font-semibold text-lg">Goal: {selectedGoalData?.title}</h4>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300">{selectedGoalData?.description}</p>
                  </CardContent>
                </Card>

                <Card className="border-blue-200 bg-blue-50 dark:bg-blue-900/20">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {selectedContentTypeData && <selectedContentTypeData.icon className="h-6 w-6 text-blue-600" />}
                        <h4 className="font-semibold text-lg">Content: {selectedContentTypeData?.title}</h4>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-blue-600 font-medium">
                          {selectedContentTypeData?.creditCost} credits
                        </p>
                        <p className="text-xs text-gray-500">
                          ~{selectedContentTypeData?.estimatedTime}
                        </p>
                      </div>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300">{selectedContentTypeData?.description}</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-6">
                    <h4 className="font-semibold text-lg mb-3">Content Details</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="font-medium">Topic:</span>
                        <p className="text-gray-600 dark:text-gray-300">{contentTopic}</p>
                      </div>
                      {targetAudience && (
                        <div>
                          <span className="font-medium">Audience:</span>
                          <p className="text-gray-600 dark:text-gray-300">{targetAudience}</p>
                        </div>
                      )}
                      {additionalContext && (
                        <div>
                          <span className="font-medium">Additional Context:</span>
                          <p className="text-gray-600 dark:text-gray-300">{additionalContext}</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t bg-gray-50 dark:bg-slate-800 p-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {currentStep > 0 && (
              <Button 
                variant="outline" 
                onClick={prevStep}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back</span>
              </Button>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              onClick={onCancel}
              className="text-gray-600 hover:text-gray-800"
            >
              Cancel
            </Button>
            
            {currentStep < steps.length - 1 ? (
              <Button 
                onClick={nextStep}
                disabled={!canProceed()}
                className="bg-gradient-to-r from-violet-600 to-pink-600 hover:from-violet-700 hover:to-pink-700 text-white flex items-center space-x-2"
              >
                <span>Continue</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button 
                onClick={handleComplete}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white flex items-center space-x-2 px-8"
              >
                <Sparkles className="h-4 w-4" />
                <span>Generate Content</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}