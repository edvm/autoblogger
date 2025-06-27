# AutoBlogger Frontend

A professional Next.js frontend application for the AutoBlogger AI-powered blog generation platform.

## Features

- **Modern Design**: Clean, professional interface inspired by Microsoft and Apple design systems
- **Dark/Light Mode**: Toggle between dark and light themes
- **Responsive**: Works seamlessly on desktop, tablet, and mobile devices
- **Authentication**: Secure authentication powered by Clerk
- **Real-time Updates**: Live status updates for blog generation process
- **Credit Management**: Built-in credit system for usage tracking
- **TypeScript**: Full TypeScript support for better development experience

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Authentication**: Clerk
- **UI Components**: Custom components with Radix UI primitives
- **Icons**: Lucide React
- **Theme**: next-themes for dark/light mode

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- A running AutoBlogger backend API (see `../backend/`)
- Clerk account for authentication

### Environment Setup

1. Copy the environment template:
   ```bash
   cp .env.template .env.local
   ```

2. Fill in your environment variables:
   ```env
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here
   CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
src/
├── app/                 # Next.js App Router pages
│   ├── dashboard/       # Protected dashboard page
│   ├── credits/         # Credit management page
│   ├── history/         # Usage history page
│   ├── sign-in/         # Clerk sign-in page
│   ├── sign-up/         # Clerk sign-up page
│   ├── layout.tsx       # Root layout with providers
│   └── page.tsx         # Landing page
├── components/          # Reusable UI components
│   ├── ui/              # Base UI components
│   ├── navigation.tsx   # Main navigation component
│   ├── theme-provider.tsx
│   └── theme-toggle.tsx
├── lib/                 # Utility functions and API client
│   ├── api.ts           # API client with Clerk integration
│   └── utils.ts         # Utility functions
└── middleware.ts        # Clerk authentication middleware
```

## API Integration

The frontend integrates with the AutoBlogger backend API through a TypeScript client that handles:

- **Authentication**: Automatic Clerk JWT token injection
- **Error Handling**: Comprehensive error handling and reporting
- **Type Safety**: Full TypeScript interfaces for all API responses
- **Real-time Updates**: Polling for blog generation status updates

## Design System

The application uses a custom design system built on Tailwind CSS with:

- **Color Palette**: Professional color scheme with dark/light mode support
- **Typography**: Clean, readable font hierarchy
- **Components**: Consistent spacing, borders, and shadows
- **Responsive Design**: Mobile-first approach with breakpoint-based layouts
- **Accessibility**: WCAG-compliant color contrast and keyboard navigation

## Authentication

Clerk provides secure authentication with features:

- **Email/Password**: Traditional email and password authentication
- **Social Login**: Support for Google, GitHub, and other providers
- **User Management**: Built-in user profile management
- **Session Management**: Secure session handling and token refresh
- **Protection**: Automatic route protection for authenticated pages

## Contributing

1. Follow the existing code style and conventions
2. Use TypeScript for all new code
3. Ensure responsive design for all new components
4. Test authentication flows thoroughly
5. Maintain accessibility standards

## License

This project is part of the AutoBlogger platform.
