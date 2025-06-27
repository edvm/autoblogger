import Link from "next/link"
import { SignedIn, SignedOut } from "@clerk/nextjs"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AIAssistantAvatar } from "@/components/ui/ai-assistant-avatar"
import { Search, Edit3, CheckCircle, Heart, Users, Sparkles, Instagram, Twitter, Youtube, TrendingUp, DollarSign, Target, Zap, Play, Star, ArrowRight } from "lucide-react"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navigation />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative w-full py-12 md:py-20 lg:py-28 bg-gradient-warm">
          <div className="container relative">
            {/* Animated background elements */}
            <div className="absolute top-20 left-20 w-72 h-72 opacity-20 rounded-full blur-3xl animate-gentle-pulse" style={{ background: 'var(--gradient-brand)' }} />
            <div className="absolute bottom-20 right-20 w-96 h-96 opacity-20 rounded-full blur-3xl animate-gentle-pulse" style={{ background: 'var(--gradient-platform)', animationDelay: '2s' }} />
            
            <div className="flex flex-col items-center space-y-10 text-center relative z-10">
              {/* Social proof banner */}
              <div className="flex items-center space-x-4 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm px-6 py-3 rounded-full border border-primary/20">
                <div className="flex -space-x-2">
                  <Instagram className="h-5 w-5" style={{ color: 'hsl(var(--autoblogger-rose))' }} />
                  <Twitter className="h-5 w-5" style={{ color: 'hsl(var(--autoblogger-blue))' }} />
                  <Youtube className="h-5 w-5" style={{ color: 'hsl(var(--autoblogger-rose))' }} />
                </div>
                <span className="text-sm font-medium text-foreground">Trusted by 50K+ <i>synthetic</i> creators</span>
                <div className="flex items-center space-x-1" style={{ color: 'hsl(var(--warning))' }}>
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                  <Star className="h-4 w-4 fill-current" />
                </div>
              </div>

              <div className="space-y-8 max-w-5xl">
                <h1 className="font-bold text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-foreground leading-tight">
                  Create Content That
                  <span className="bg-gradient-brand bg-clip-text text-transparent block mt-2">
                    Sells & Goes Viral
                  </span>
                </h1>
                <p className="mx-auto max-w-[800px] text-xl md:text-2xl text-muted-foreground leading-relaxed">
                  From Instagram posts that drive sales to YouTube scripts that get millions of views, 
                  <span className="font-semibold text-foreground"> AI-powered content creation for modern creators.</span>
                </p>
              </div>
              
              {/* Platform showcase */}
              <div className="flex flex-wrap items-center justify-center gap-6 mb-8">
                <div className="flex items-center space-x-2 text-white px-4 py-2 rounded-full text-sm font-medium" style={{ background: 'linear-gradient(135deg, hsl(var(--autoblogger-rose)), hsl(var(--autoblogger-pink)))' }}>
                  <Instagram className="h-4 w-4" />
                  <span>Instagram Posts</span>
                </div>
                <div className="flex items-center space-x-2 text-white px-4 py-2 rounded-full text-sm font-medium" style={{ background: 'linear-gradient(135deg, hsl(var(--autoblogger-blue)), hsl(var(--autoblogger-cyan)))' }}>
                  <Twitter className="h-4 w-4" />
                  <span>Twitter Threads</span>
                </div>
                <div className="flex items-center space-x-2 text-white px-4 py-2 rounded-full text-sm font-medium" style={{ background: 'linear-gradient(135deg, hsl(var(--autoblogger-rose)), hsl(var(--autoblogger-pink)))' }}>
                  <Youtube className="h-4 w-4" />
                  <span>Video Scripts</span>
                </div>
                <div className="flex items-center space-x-2 text-white px-4 py-2 rounded-full text-sm font-medium bg-gradient-brand">
                  <Edit3 className="h-4 w-4" />
                  <span>Blog Articles</span>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-6 items-center">
                <SignedOut>
                  <Button size="lg" className="bg-gradient-brand hover:opacity-90 text-white px-8 py-4 text-lg font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 group">
                    <Link href="/sign-up" className="flex items-center">
                      <Zap className="mr-2 h-5 w-5 group-hover:animate-bounce" />
                      Start Creating Free
                      <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" className="border-2 border-primary text-primary hover:bg-primary/10 px-6 py-4">
                    <Link href="/sign-in">Sign In</Link>
                  </Button>
                </SignedOut>
                <SignedIn>
                  <Button size="lg" className="bg-gradient-brand hover:opacity-90 text-white px-8 py-4 text-lg font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 group">
                    <Link href="/dashboard" className="flex items-center">
                      <Sparkles className="mr-2 h-5 w-5 group-hover:animate-spin" />
                      Create Content Now
                      <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                  </Button>
                </SignedIn>
              </div>

              {/* Results showcase */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 max-w-4xl">
                <div className="bg-white/60 dark:bg-card/60 backdrop-blur-sm p-6 rounded-2xl border border-primary/20">
                  <div className="flex items-center justify-center w-12 h-12 bg-gradient-success rounded-xl mb-4 mx-auto">
                    <TrendingUp className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="font-bold text-2xl text-foreground mb-2">500K+</h3>
                  <p className="text-muted-foreground">Posts generated monthly</p>
                </div>
                <div className="bg-white/60 dark:bg-card/60 backdrop-blur-sm p-6 rounded-2xl border border-primary/20">
                  <div className="flex items-center justify-center w-12 h-12 bg-gradient-platform rounded-xl mb-4 mx-auto">
                    <DollarSign className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="font-bold text-2xl text-foreground mb-2">$2M+</h3>
                  <p className="text-muted-foreground">Revenue generated for creators</p>
                </div>
                <div className="bg-white/60 dark:bg-card/60 backdrop-blur-sm p-6 rounded-2xl border border-primary/20">
                  <div className="flex items-center justify-center w-12 h-12 bg-gradient-brand rounded-xl mb-4 mx-auto">
                    <Target className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="font-bold text-2xl text-foreground mb-2">300%</h3>
                  <p className="text-muted-foreground">Average engagement boost</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Creator Success Stories */}
        <section className="w-full py-16 md:py-24 bg-gradient-creator">
          <div className="container">
            <div className="text-center space-y-6 mb-16">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground">
                Built for Creator Success
              </h2>
              <p className="mx-auto max-w-[800px] text-xl text-muted-foreground">
                From Instagram influencers to YouTube stars, creators are using AutoBlogger to scale their content and grow their revenue.
              </p>
            </div>
            
            <div className="grid gap-8 lg:grid-cols-3 lg:gap-12 mb-16">
              <Card className="group hover:shadow-2xl transition-all duration-500 border border-primary/10 bg-gradient-to-br from-pink-50/50 to-rose-50/50 dark:from-pink-900/10 dark:to-rose-900/10">
                <CardHeader className="text-center p-8">
                  <div className="mx-auto w-20 h-20 rounded-3xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300" style={{ background: 'linear-gradient(135deg, hsl(var(--autoblogger-rose)), hsl(var(--autoblogger-pink)))' }}>
                    <Instagram className="h-10 w-10 text-white" />
                  </div>
                  <CardTitle className="text-2xl mb-4 text-foreground">Instagram Creators</CardTitle>
                  <CardDescription className="text-lg leading-relaxed text-muted-foreground">
                    Generate viral captions, story content, and product posts that convert followers into customers. Perfect for influencers and brands.
                  </CardDescription>
                  <div className="mt-6 p-4 bg-white/90 dark:bg-card/90 rounded-xl border border-primary/10">
                    <p className="text-sm font-semibold" style={{ color: 'hsl(var(--autoblogger-pink))' }}>"Increased my sales by 400% in 3 months"</p>
                    <p className="text-xs text-muted-foreground mt-1">- Sarah K, Fashion Influencer</p>
                  </div>
                </CardHeader>
              </Card>
              
              <Card className="group hover:shadow-2xl transition-all duration-500 border border-primary/10 bg-gradient-to-br from-blue-50/50 to-cyan-50/50 dark:from-blue-900/10 dark:to-cyan-900/10">
                <CardHeader className="text-center p-8">
                  <div className="mx-auto w-20 h-20 rounded-3xl bg-gradient-platform flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <Youtube className="h-10 w-10 text-white" />
                  </div>
                  <CardTitle className="text-2xl mb-4 text-foreground">YouTubers</CardTitle>
                  <CardDescription className="text-lg leading-relaxed text-muted-foreground">
                    Create compelling video scripts, descriptions, and thumbnails copy that boost views and subscriber growth.
                  </CardDescription>
                  <div className="mt-6 p-4 bg-white/90 dark:bg-card/90 rounded-xl border border-primary/10">
                    <p className="text-sm font-semibold" style={{ color: 'hsl(var(--autoblogger-blue))' }}>"From 10K to 500K subscribers in 8 months"</p>
                    <p className="text-xs text-muted-foreground mt-1">- Mike R, Tech YouTuber</p>
                  </div>
                </CardHeader>
              </Card>
              
              <Card className="group hover:shadow-2xl transition-all duration-500 border border-primary/10 bg-gradient-to-br from-violet-50/50 to-purple-50/50 dark:from-violet-900/10 dark:to-purple-900/10">
                <CardHeader className="text-center p-8">
                  <div className="mx-auto w-20 h-20 rounded-3xl bg-gradient-brand flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                    <DollarSign className="h-10 w-10 text-white" />
                  </div>
                  <CardTitle className="text-2xl mb-4 text-foreground">E-commerce</CardTitle>
                  <CardDescription className="text-lg leading-relaxed text-muted-foreground">
                    Product descriptions, email campaigns, and sales copy that convert browsers into buyers across all platforms.
                  </CardDescription>
                  <div className="mt-6 p-4 bg-white/90 dark:bg-card/90 rounded-xl border border-primary/10">
                    <p className="text-sm font-semibold text-primary">"$100K in sales from one product launch"</p>
                    <p className="text-xs text-muted-foreground mt-1">- Lisa M, E-commerce Brand</p>
                  </div>
                </CardHeader>
              </Card>
            </div>

            {/* Demo video section */}
            <div className="text-center">
              <div className="inline-flex items-center space-x-4 bg-gradient-brand p-1 rounded-2xl">
                <Button size="lg" className="bg-white text-primary hover:bg-muted px-8 py-4 rounded-xl font-semibold">
                  <Play className="mr-2 h-5 w-5" />
                  Watch 2-Min Demo
                </Button>
                <span className="text-white font-medium pr-6">See how creators make $10K+ monthly</span>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works - Creator Focused */}
        <section className="w-full py-16 md:py-24 bg-background">
          <div className="container">
            <div className="text-center space-y-6 mb-20">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground">
                From Idea to Viral in Minutes
              </h2>
              <p className="max-w-[800px] mx-auto text-xl text-muted-foreground leading-relaxed">
                Our AI workflow creates platform-optimized content that's designed to engage, convert, and scale your creator business.
              </p>
            </div>
            
            <div className="grid gap-12 lg:grid-cols-3 mb-16">
              {/* Step 1 */}
              <div className="text-center group">
                <div className="relative mb-8">
                  <div className="w-32 h-32 mx-auto rounded-full bg-gradient-brand flex items-center justify-center shadow-2xl group-hover:scale-110 transition-all duration-500">
                    <Target className="h-16 w-16 text-white" />
                  </div>
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-success rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">1</span>
                  </div>
                  {/* Connecting line for desktop */}
                  <div className="hidden lg:block absolute top-16 left-full w-24 h-0.5 bg-gradient-to-r from-violet-300 to-blue-300" style={{ transform: 'translateX(-50%)' }} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground">Choose Your Goal</h3>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  Tell us what you want to achieve: Drive sales, go viral, build authority, or grow your audience. We optimize for your specific goal.
                </p>
              </div>

              {/* Step 2 */}
              <div className="text-center group">
                <div className="relative mb-8">
                  <div className="w-32 h-32 mx-auto rounded-full bg-gradient-platform flex items-center justify-center shadow-2xl group-hover:scale-110 transition-all duration-500">
                    <Zap className="h-16 w-16 text-white" />
                  </div>
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-success rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">2</span>
                  </div>
                  {/* Connecting line for desktop */}
                  <div className="hidden lg:block absolute top-16 left-full w-24 h-0.5 bg-gradient-to-r from-blue-300 to-pink-300" style={{ transform: 'translateX(-50%)' }} />
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground">AI Creates Magic</h3>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  Watch as our AI researches trends, writes engaging content, and optimizes for each platform's algorithm - all in real-time.
                </p>
              </div>

              {/* Step 3 */}
              <div className="text-center group">
                <div className="relative mb-8">
                  <div className="w-32 h-32 mx-auto rounded-full bg-gradient-success flex items-center justify-center shadow-2xl group-hover:scale-110 transition-all duration-500">
                    <TrendingUp className="h-16 w-16 text-white" />
                  </div>
                  <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-success rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">3</span>
                  </div>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-foreground">Publish & Profit</h3>
                <p className="text-lg text-muted-foreground leading-relaxed">
                  Get content formatted for Instagram, Twitter, YouTube, and blogs. Copy, paste, post, and watch your engagement soar.
                </p>
              </div>
            </div>

            {/* Final CTA */}
            <div className="text-center">
              <div className="inline-block p-8 bg-gradient-brand rounded-3xl shadow-2xl">
                <h3 className="text-2xl font-bold text-white mb-4">Ready to 10x Your Content Game?</h3>
                <p className="text-white/80 text-lg mb-6">Join 50,000+ creators already using AutoBlogger</p>
                <SignedOut>
                  <Button size="lg" className="bg-white text-primary hover:bg-muted px-10 py-4 text-lg font-bold shadow-xl">
                    <Link href="/sign-up">Start Free Trial - No Credit Card</Link>
                  </Button>
                </SignedOut>
                <SignedIn>
                  <Button size="lg" className="bg-white text-primary hover:bg-muted px-10 py-4 text-lg font-bold shadow-xl">
                    <Link href="/dashboard">Create Your First Viral Post</Link>
                  </Button>
                </SignedIn>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-t from-muted/30 to-background border-t border-border">
        <div className="container py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Brand */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-brand rounded-lg flex items-center justify-center">
                  <Sparkles className="h-4 w-4 text-white" />
                </div>
                <span className="font-bold text-lg text-foreground">AutoBlogger</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Your AI-powered content creation platform. Turning ideas into viral content that drives results.
              </p>
            </div>

            {/* Links */}
            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Resources</h4>
              <nav className="flex flex-col space-y-2">
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  How It Works
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Creator Tips
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Help Center
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  API Documentation
                </Link>
              </nav>
            </div>

            {/* Legal */}
            <div className="space-y-4">
              <h4 className="font-semibold text-foreground">Legal</h4>
              <nav className="flex flex-col space-y-2">
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Terms of Service
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Privacy Policy
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Cookie Policy
                </Link>
                <Link className="text-sm text-muted-foreground hover:text-primary transition-colors" href="#">
                  Creator Agreement
                </Link>
              </nav>
            </div>
          </div>

          <div className="border-t border-border mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between">
            <p className="text-xs text-muted-foreground">
              © 2024 AutoBlogger. Made with ❤️ for creators everywhere.
            </p>
            <div className="flex items-center space-x-4 mt-4 sm:mt-0">
              <span className="text-xs text-muted-foreground">Powered by AI, driven by creativity</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
