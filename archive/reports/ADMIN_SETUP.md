# Admin Panel Setup Instructions

## ✅ Backend Setup (COMPLETED)

The following files have been created:

- ✅ `utils/auth/admin_check.py` - Admin authentication decorator
- ✅ `routes/admin_routes.py` - Flask API endpoints
- ✅ `src/webapp.py` - Integrated admin_bp Blueprint

## ✅ Frontend Setup (COMPLETED)

The following files have been created:

### Types & API
- ✅ `webapp/src/admin/types/admin.ts` - TypeScript types
- ✅ `webapp/src/admin/api/admin.ts` - API client

### Hooks
- ✅ `webapp/src/admin/hooks/useSSE.ts` - Server-Sent Events hook
- ✅ `webapp/src/admin/hooks/useAdminStats.ts` - Statistics hook
- ✅ `webapp/src/admin/hooks/useMetrics.ts` - Metrics hooks
- ✅ `webapp/src/admin/hooks/useLogs.ts` - Logs hooks

### Components & Pages
- ✅ `webapp/src/admin/components/AdminLayout.tsx` - Main layout with navigation
- ✅ `webapp/src/admin/components/StatCard.tsx` - Statistics card component
- ✅ `webapp/src/admin/pages/AdminDashboard.tsx` - Dashboard page
- ✅ `webapp/src/admin/pages/AdminMetrics.tsx` - Metrics page with charts
- ✅ `webapp/src/admin/pages/AdminLogs.tsx` - Logs viewer page
- ✅ `webapp/src/admin/pages/AdminConfig.tsx` - Configuration page

### Routing
- ✅ `webapp/src/admin/AdminRoutes.tsx` - React Router configuration
- ✅ `webapp/src/App.tsx` - Integrated admin routing

## 📦 Frontend Dependencies Installation

Run these commands to install required packages:

```bash
cd webapp

# Install TanStack Query (React Query v5)
npm install @tanstack/react-query

# Install Recharts for charts
npm install recharts

# Install date-fns for date formatting
npm install date-fns

# Install sonner for toast notifications (optional)
npm install sonner
```

## 🔧 Build & Test

```bash
# Build React app
cd webapp
npm run build

# Start Flask server (from project root)
cd ..
python src/webapp.py
```

## 🌐 Access Admin Panel

Once the server is running, access the admin panel at:

```
http://localhost:8001/admin/dashboard
```

Or if using Cloudflare tunnel:

```
https://your-cloudflare-url.com/admin/dashboard
```

## 🔐 Authentication

The admin panel uses existing Telegram WebApp authentication + admin check:

1. User must be authenticated via Telegram
2. User's telegram_id must be in the `admins` table with `is_active = TRUE`
3. Session is cached for performance

## 🎯 Available Admin Routes

- `/admin/dashboard` - System overview and statistics
- `/admin/metrics` - AI metrics and user analytics
- `/admin/logs` - Real-time log viewer
- `/admin/config` - System configuration

## 📊 API Endpoints

All endpoints are prefixed with `/admin/api/` and require admin authentication:

- `GET /admin/api/me` - Current admin info
- `GET /admin/api/stats` - System statistics
- `GET /admin/api/metrics/ai` - AI metrics
- `GET /admin/api/metrics/users` - User metrics
- `GET /admin/api/metrics/stream` - SSE real-time stream
- `GET /admin/api/logs/tail` - Get logs
- `GET /admin/api/logs/files` - List log files
- `GET /admin/api/config` - Get configuration
- `POST /admin/api/config` - Update configuration
- `GET /admin/api/health` - Health check (no auth)

## 🐛 Troubleshooting

### Frontend build errors

If you see import errors, make sure all dependencies are installed:

```bash
cd webapp
npm install
```

### Backend import errors

Make sure you're in the virtual environment:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Admin access denied

Check that your Telegram ID is in the admins table:

```sql
SELECT * FROM admins WHERE telegram_id = YOUR_TELEGRAM_ID;
```

If not, add yourself:

```sql
INSERT INTO admins (telegram_id, username, is_active) 
VALUES (YOUR_TELEGRAM_ID, 'your_username', TRUE);
```

## 📝 Next Steps

1. Install frontend dependencies
2. Build React app
3. Test admin panel access
4. Customize as needed

## 🎨 Customization

The admin panel uses:
- Tailwind CSS for styling
- Existing Card components from shadcn/ui
- Framer Motion for animations
- Recharts for data visualization

All styling follows the PulseAI design system (green accent, dark mode support).


