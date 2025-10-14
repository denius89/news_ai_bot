# PulseAI WebApp

Modern React-based web application for managing PulseAI notifications with a clean, Telegram-inspired UI.

## Features

- 📱 **Mobile-first design** - Optimized for mobile devices
- 🌙 **Dark theme support** - Automatic dark/light mode switching
- ⚡ **Real-time updates** - Live notification status updates
- 🎨 **Modern UI** - Built with shadcn/ui and Tailwind CSS
- 📊 **TypeScript** - Full type safety throughout the application

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible UI components
- **Lucide React** - Beautiful icon library
- **React Router** - Client-side routing

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- PulseAI backend running on localhost:8001

### Installation

```bash
# Install dependencies
npm install

# Configure environment (optional for dev)
# Create .env file in webapp/ directory with:
# VITE_CLOUDFLARE_TUNNEL_URL=https://your-subdomain.trycloudflare.com
# или
# CLOUDFLARE_TUNNEL_URL=https://your-subdomain.trycloudflare.com

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

**Note:** Environment variables are optional in development mode. The app will use relative API paths through Vite proxy.

### Building for Production

```bash
# Build the application
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── api/                    # API client functions
│   └── notifications.ts    # Notification API calls
├── components/             # Reusable UI components
│   ├── ui/                 # shadcn/ui components
│   └── BottomNavigation.tsx
├── features/               # Feature-based organization
│   └── notifications/      # Notification feature
│       ├── components/     # Feature-specific components
│       └── NotificationsPage.tsx
├── lib/                    # Utility functions
│   └── utils.ts           # Common utilities
├── routes.tsx             # Application routing
├── App.tsx                # Main app component
└── main.tsx               # Application entry point
```

## API Integration

The app connects to the PulseAI backend API:

- `GET /api/user_notifications` - Fetch user notifications
- `POST /api/user_notifications/mark_read` - Mark notification as read

## Development

### Code Style

- **TypeScript strict mode** - No `any` types allowed
- **Functional components** - Use React hooks
- **Tailwind CSS** - Utility-first styling
- **clsx** - Conditional class names

### Key Features

1. **Optimistic Updates** - UI updates immediately, rolls back on error
2. **Error Handling** - Comprehensive error states and retry mechanisms
3. **Loading States** - Skeleton loaders and loading indicators
4. **Responsive Design** - Works on all screen sizes
5. **Accessibility** - ARIA labels and keyboard navigation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT License - see LICENSE file for details
