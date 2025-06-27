"use client"

import { useState, useEffect, useCallback, useMemo } from "react"
import { useAuth } from "@clerk/nextjs"
import { useRouter } from "next/navigation"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { createApiClient, type CreditBalance, type CreditTransaction, type UserContentItem } from "@/lib/api"
import { 
  CreditCard, 
  Plus, 
  Loader2, 
  Crown,
  Users,
  Check,
  Instagram,
  Sparkles,
  TrendingUp,
  Calendar,
  FileText,
  ExternalLink,
  ArrowRight
} from "lucide-react"

export const dynamic = 'force-dynamic'

interface Plan {
  id: string
  name: string
  credits: number
  price: number
  popular?: boolean
  icon: React.ComponentType<{ className?: string }>
  gradient: string
}

const plans: Plan[] = [
  {
    id: 'starter',
    name: 'Starter',
    credits: 100,
    price: 9.99,
    icon: Instagram,
    gradient: 'from-blue-500 to-blue-600'
  },
  {
    id: 'pro',
    name: 'Pro',
    credits: 500,
    price: 39.99,
    popular: true,
    icon: Crown,
    gradient: 'from-violet-500 to-purple-500'
  },
  {
    id: 'unlimited',
    name: 'Unlimited',
    credits: 2000,
    price: 99.99,
    icon: Users,
    gradient: 'from-emerald-500 to-emerald-600'
  }
]

export default function Credits() {
  const { getToken } = useAuth()
  const router = useRouter()
  const api = useMemo(() => createApiClient(getToken), [getToken])
  
  const [balance, setBalance] = useState<CreditBalance | null>(null)
  const [transactions, setTransactions] = useState<CreditTransaction[]>([])
  const [contentHistory, setContentHistory] = useState<UserContentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    try {
      const [balanceData, transactionsData, contentData] = await Promise.all([
        api.getCreditBalance(),
        api.getCreditTransactions(20, 0),
        api.getUserContent(20, 0)
      ])
      setBalance(balanceData)
      setTransactions(transactionsData)
      setContentHistory(contentData)
    } catch (error) {
      console.error("Failed to load data:", error)
    } finally {
      setLoading(false)
    }
  }, [api])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handlePurchase = async (planId: string) => {
    const plan = plans.find(p => p.id === planId)
    if (!plan) return

    setPurchasing(planId)
    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000))
      await api.purchaseCredits(plan.credits)
      await loadData()
    } catch (error) {
      console.error("Failed to purchase:", error)
    } finally {
      setPurchasing(null)
    }
  }

  const handleViewContent = (usageId: number) => {
    router.push(`/editor/${usageId}`)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col">
        <Navigation />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-violet-600" />
        </main>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col">
      <Navigation />
      
      <main className="flex-1 bg-gradient-to-br from-slate-50 via-white to-violet-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
        <div className="container py-12 max-w-6xl">
          
          {/* Hero Section with Balance */}
          <div className="text-center mb-12">
            <div className="relative overflow-hidden bg-gradient-to-r from-violet-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-2xl">
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-10">
                <div className="absolute top-4 right-6">
                  <Sparkles className="h-16 w-16" />
                </div>
                <div className="absolute bottom-4 left-6">
                  <div className="grid grid-cols-6 gap-1">
                    {Array.from({ length: 18 }).map((_, i) => (
                      <div key={i} className="w-1.5 h-1.5 bg-white rounded-full opacity-30"></div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="relative z-10 flex items-center justify-between max-w-4xl mx-auto">
                {/* Left side - Title and description */}
                <div className="text-left">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                      <CreditCard className="h-6 w-6 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold">Credits</h1>
                  </div>
                  <p className="text-white/80 max-w-md">
                    Fuel your creativity with AI-powered content generation
                  </p>
                </div>
                
                {/* Right side - Current Balance */}
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                  <div className="text-white/80 text-sm mb-1">Current Balance</div>
                  <div className="text-4xl font-bold text-white mb-1">
                    {balance?.credits?.toLocaleString() || '0'}
                  </div>
                  <div className="text-white/80 text-sm">credits available</div>
                </div>
              </div>
            </div>
          </div>

          {/* Plans Section */}
          <div className="mb-16">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-foreground mb-4">Choose Your Plan</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Simple pricing for creators at every level. All plans include unlimited content types and priority support.
              </p>
            </div>
            
            <div className="grid gap-8 md:grid-cols-3">
              {plans.map((plan) => {
                const Icon = plan.icon
                const isPurchasing = purchasing === plan.id
                
                return (
                  <Card 
                    key={plan.id}
                    className={`relative group transition-all duration-300 hover:shadow-2xl ${
                      plan.popular 
                        ? 'border-2 border-violet-200 bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 scale-105'
                        : 'border border-border hover:border-violet-200'
                    }`}
                  >
                    {plan.popular && (
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                        <Badge className="bg-gradient-to-r from-violet-600 to-purple-600 text-white px-6 py-2 text-sm font-semibold">
                          MOST POPULAR
                        </Badge>
                      </div>
                    )}
                    
                    <CardHeader className="text-center pb-4 pt-8">
                      <div className="flex items-center justify-center mb-6">
                        <div className={`w-20 h-20 bg-gradient-to-r ${plan.gradient} rounded-3xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                          <Icon className="h-10 w-10 text-white" />
                        </div>
                      </div>
                      
                      <CardTitle className="text-2xl font-bold text-foreground mb-2">
                        {plan.name}
                      </CardTitle>
                      
                      <div className="mb-6">
                        <div className="text-5xl font-bold text-foreground mb-2">
                          ${plan.price}
                        </div>
                        <div className="text-muted-foreground">
                          {plan.credits.toLocaleString()} credits
                        </div>
                        <div className="text-sm text-muted-foreground mt-1">
                          ${(plan.price / plan.credits * 100).toFixed(1)}¢ per credit
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent className="pt-0">
                      <Button 
                        onClick={() => handlePurchase(plan.id)}
                        disabled={isPurchasing}
                        className={`w-full py-4 text-lg font-semibold transition-all duration-300 ${
                          plan.popular
                            ? 'bg-gradient-to-r from-violet-600 to-purple-600 hover:opacity-90 text-white shadow-lg hover:shadow-xl hover:scale-105'
                            : 'bg-gradient-to-r from-gray-700 to-gray-800 hover:opacity-90 text-white shadow-lg hover:shadow-xl hover:scale-105'
                        }`}
                      >
                        {isPurchasing ? (
                          <>
                            <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          <>
                            <Plus className="h-5 w-5 mr-3" />
                            Get {plan.name}
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </div>

          {/* Credit History Section */}
          <div>
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-4">Credit History</h2>
              <p className="text-lg text-muted-foreground">
                Track where your credits were spent and access your created content.
              </p>
            </div>
            
            <Card className="border-0 shadow-xl bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm">
              <CardContent className="p-0">
                {transactions.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="w-20 h-20 bg-muted rounded-full flex items-center justify-center mx-auto mb-6">
                      <Calendar className="h-10 w-10 text-muted-foreground" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">No transactions yet</h3>
                    <p className="text-muted-foreground">
                      Your credit history will appear here once you start creating content.
                    </p>
                  </div>
                ) : (
                  <div className="divide-y divide-border">
                    {transactions.map((transaction, index) => {
                      // Find corresponding content for this transaction
                      const relatedContent = contentHistory.find(content => 
                        Math.abs(new Date(content.created_at).getTime() - new Date(transaction.created_at).getTime()) < 60000 // Within 1 minute
                      )
                      
                      return (
                        <div key={transaction.id} className="p-6 hover:bg-muted/30 transition-colors duration-200">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                                transaction.transaction_type === 'purchase' 
                                  ? 'bg-green-100 text-green-600 dark:bg-green-900/20' 
                                  : 'bg-red-100 text-red-600 dark:bg-red-900/20'
                              }`}>
                                {transaction.transaction_type === 'purchase' ? (
                                  <Plus className="h-6 w-6" />
                                ) : (
                                  <FileText className="h-6 w-6" />
                                )}
                              </div>
                              
                              <div className="flex-1">
                                <div className="flex items-center space-x-3">
                                  <h4 className="font-semibold text-foreground">
                                    {transaction.transaction_type === 'purchase' ? 'Credits Purchased' : 'Content Created'}
                                  </h4>
                                  {relatedContent && (
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => handleViewContent(relatedContent.id)}
                                      className="text-violet-600 border-violet-200 hover:bg-violet-50 dark:border-violet-700 dark:text-violet-400 dark:hover:bg-violet-900/20"
                                    >
                                      <ExternalLink className="h-3 w-3 mr-1" />
                                      View Content
                                    </Button>
                                  )}
                                </div>
                                
                                <div className="text-sm text-muted-foreground mt-1">
                                  {transaction.description || 'No description'}
                                  {relatedContent && (
                                    <span className="ml-2 text-violet-600 dark:text-violet-400">
                                      • {relatedContent.topic}
                                    </span>
                                  )}
                                </div>
                                
                                <div className="text-xs text-muted-foreground mt-1">
                                  {formatDate(transaction.created_at)} at {formatTime(transaction.created_at)}
                                </div>
                              </div>
                            </div>
                            
                            <div className="text-right">
                              <div className={`text-lg font-semibold ${
                                transaction.transaction_type === 'purchase' 
                                  ? 'text-green-600' 
                                  : 'text-red-600'
                              }`}>
                                {transaction.transaction_type === 'purchase' ? '+' : '-'}{Math.abs(transaction.amount)}
                              </div>
                              <div className="text-xs text-muted-foreground">credits</div>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}