import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 font-accent",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-md hover:bg-primary/90 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 bg-gradient-to-br from-sage-green to-sage-green/80",
        destructive:
          "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 hover:shadow-md",
        outline:
          "border-2 border-primary bg-transparent text-primary shadow-sm hover:bg-primary hover:text-primary-foreground hover:shadow-md hover:-translate-y-0.5 active:translate-y-0",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 hover:shadow-md",
        ghost: "hover:bg-warm-gray hover:text-deep-forest",
        link: "text-primary underline-offset-4 hover:underline font-medium",
        warm: "bg-soft-coral text-white shadow-md hover:bg-soft-coral/90 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0",
        golden: "bg-golden-yellow text-deep-forest shadow-md hover:bg-golden-yellow/90 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0",
      },
      size: {
        default: "h-10 px-6 py-2",
        sm: "h-8 rounded-lg px-4 text-xs",
        lg: "h-12 rounded-xl px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }