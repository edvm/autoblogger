"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs"
import { ThemeToggle } from "./theme-toggle"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"
import { Sparkles, CreditCard, FileText } from "lucide-react"

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: Sparkles },
  { name: "Content", href: "/content", icon: FileText },
  { name: "Credits", href: "/credits", icon: CreditCard },
  // { name: "History", href: "/history", icon: History },
]

export function Navigation() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container">
        <div className="flex h-16 items-center justify-between">
          {/* Left side: Brand + Navigation */}
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-brand rounded-lg flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <span className="hidden font-bold text-lg text-foreground sm:inline-block">
                AutoBlogger
              </span>
            </Link>
            <SignedIn>
              <nav className="flex items-center space-x-6 text-sm font-medium">
                {navigation.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-muted",
                        isActive
                          ? "text-primary bg-primary/10 font-semibold"
                          : "text-muted-foreground hover:text-foreground"
                      )}
                    >
                      <Icon className="h-4 w-4" />
                      <span className="hidden sm:inline-block">{item.name}</span>
                    </Link>
                  )
                })}
              </nav>
            </SignedIn>
          </div>

          {/* Right side: Theme toggle + User actions */}
          <div className="flex items-center space-x-3">
            <ThemeToggle />
            <SignedOut>
              <SignInButton>
                <Button variant="outline" size="sm" className="border-primary/30 text-primary hover:bg-primary/10">
                  Sign In
                </Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton 
                afterSignOutUrl="/"
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8",
                    userButtonPopoverCard: "border-border",
                    userButtonPopoverActions: "text-foreground"
                  }
                }}
              />
            </SignedIn>
          </div>
        </div>
      </div>
    </header>
  )
}