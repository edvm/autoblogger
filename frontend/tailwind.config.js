/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Warm design system colors
        "sage-green": "hsl(var(--sage-green))",
        "warm-cream": "hsl(var(--warm-cream))",
        "soft-coral": "hsl(var(--soft-coral))",
        "dusty-blue": "hsl(var(--dusty-blue))",
        "warm-gray": "hsl(var(--warm-gray))",
        "deep-forest": "hsl(var(--deep-forest))",
        "golden-yellow": "hsl(var(--golden-yellow))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        info: "hsl(var(--info))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "calc(var(--radius) + 4px)",
        "2xl": "calc(var(--radius) + 8px)",
      },
      fontFamily: {
        sans: ["var(--font-inter)"],
        accent: ["var(--font-plus-jakarta-sans)", "ui-sans-serif", "system-ui"],
      },
      animation: {
        "gentle-pulse": "gentle-pulse 2s ease-in-out infinite",
        "warm-glow": "warm-glow 3s ease-in-out infinite",
      },
      keyframes: {
        "gentle-pulse": {
          "0%, 100%": { opacity: 1 },
          "50%": { opacity: 0.8 },
        },
        "warm-glow": {
          "0%, 100%": { 
            "box-shadow": "0 0 20px hsl(var(--sage-green) / 0.3)" 
          },
          "50%": { 
            "box-shadow": "0 0 40px hsl(var(--sage-green) / 0.5)" 
          },
        },
      },
    },
  },
  plugins: [],
}

