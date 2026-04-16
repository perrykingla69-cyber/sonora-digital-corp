# Mission Control — Integration Guide

## Overview

Mission Control is a real-time monitoring dashboard for HERMES OS. It's located in `/apps/mission-control/` and provides a centralized view of:

- **System Status**: Docker services, API metrics, database connections
- **Real-time Logs**: Service logs streaming from VPS
- **Agent Status**: HERMES, MYSTIC, ClawBot, Claude Code activity
- **Task Progress**: Claude Code tasks with completion percentage
- **MCP Health**: GitHub, HuggingFace, OpenRouter, Qdrant, Engram status
- **Telegram Bridge**: Execute CLI commands directly from the dashboard

## Quick Setup

### 1. Install Dependencies

From project root:

```bash
cd apps/mission-control
npm install
```

### 2. Create Environment File

```bash
# Copy the example
cp .env.local.example .env.local

# Or create manually:
echo "NEXT_PUBLIC_API_URL=https://vps.hermes.local:8000" > .env.local
```

**Note**: If `NEXT_PUBLIC_API_URL` is unreachable, the dashboard automatically uses realistic mock data.

### 3. Run Locally

```bash
npm run dev
```

Opens at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm run start
```

## File Structure

```
apps/mission-control/
├── app/
│   ├── page.tsx           ← Main dashboard component (146 lines)
│   ├── layout.tsx         ← Next.js layout with metadata
│   └── globals.css        ← Global styles (design tokens)
├── components/
│   ├── Navbar.tsx         ← Top navigation bar
│   ├── StatusBoard.tsx    ← System metrics cards
│   ├── LogsViewer.tsx     ← Real-time log stream
│   ├── TasksPanel.tsx     ← Claude Code tasks
│   ├── AgentsMonitor.tsx  ← Agent status
│   ├── MCPsStatus.tsx     ← MCP server health
│   └── CrawbotBridge.tsx  ← Telegram command executor
├── lib/
│   ├── types.ts           ← TypeScript interfaces
│   ├── api.ts             ← API client with fallback
│   ├── mockdata.ts        ← Mock data generator
│   └── animations.ts      ← GSAP utilities
├── package.json           ← Dependencies
├── tsconfig.json          ← TypeScript config
├── tailwind.config.ts     ← Tailwind theme
├── next.config.ts         ← Next.js config
├── README.md              ← Full documentation
├── QUICK_START.md         ← Quick reference
└── ARCHITECTURE.md        ← Technical architecture
```

## API Integration

The dashboard connects to VPS API endpoints:

```
GET /api/v1/status           → SystemStatus (Docker, API, DB, Redis)
GET /api/v1/agents/status    → Agent[] (HERMES, MYSTIC, ClawBot, Claude Code)
GET /api/v1/mcps/status      → MCP[] (GitHub, HF, OpenRouter, Qdrant, Engram)
GET /api/v1/tasks            → Task[] (Claude Code tasks)
GET /api/v1/logs/stream      → EventSource SSE (real-time logs)
```

### Timeout & Fallback

- **Request timeout**: 5 seconds per API call
- **Failure behavior**: Falls back to mock data automatically
- **User notification**: None (uses mock data silently)
- **Console logging**: Warnings logged (dev only)

## Vercel Deployment

### 1. Add to GitHub

```bash
git add apps/mission-control
git commit -m "feat: add Mission Control dashboard"
git push origin main
```

### 2. Configure Vercel

File: `/vercel.json` (already created at repo root)

```json
{
  "buildCommand": "cd apps/mission-control && npm install && npm run build",
  "outputDirectory": "apps/mission-control/.next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@next_public_api_url"
  }
}
```

### 3. Add Environment Variables

In Vercel Dashboard → Project Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL = https://vps.hermes.local:8000
```

### 4. Deploy

```bash
vercel deploy --prod
```

Or auto-deploy: push to main → GitHub Actions → Vercel

## Docker Deployment (Optional)

### Build Image

```bash
docker build -t mission-control:latest apps/mission-control/
```

### Run Container

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://vps.hermes.local:8000 \
  mission-control:latest
```

### Docker Compose (in stack)

Add to `infra/docker-compose.yml`:

```yaml
mission-control:
  build:
    context: .
    dockerfile: apps/mission-control/Dockerfile
  ports:
    - "3001:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://hermes-api:8000
  networks:
    - hermes
  depends_on:
    - hermes-api
```

## Configuration

### Polling Interval

Edit `app/page.tsx`:

```typescript
const interval = setInterval(loadData, 30000) // Change 30000 to desired ms
```

### Colors & Styling

Edit `tailwind.config.ts`:

```typescript
colors: {
  primary: '#0F0F0F',
  accent: '#00D9FF',
  secondary: '#6D28D9',
}
```

### Custom Mock Data

Edit `lib/mockdata.ts` to change generated values.

## API Implementation (VPS)

If implementing backend endpoints, follow this contract:

### GET /api/v1/status

```typescript
interface SystemStatus {
  docker: {
    healthy: number
    total: number
    services: {
      name: string
      status: 'healthy' | 'unhealthy' | 'starting'
      uptime: number
      memory: number
      cpu: number
    }[]
  }
  api: {
    status: 'online' | 'offline' | 'degraded'
    responseTime: number
    requestsPerMinute: number
  }
  postgresql: {
    status: 'connected' | 'disconnected'
    connections: number
    maxConnections: number
    queryTime: number
  }
  redis: {
    status: 'connected' | 'disconnected'
    memory: number
    keys: number
  }
}
```

### GET /api/v1/logs/stream

Use Server-Sent Events (SSE):

```typescript
event: log
data: {"timestamp":"2026-04-16T...", "service":"hermes-api", "level":"info", "message":"..."}
```

Or fallback to polling:

```typescript
GET /api/v1/logs?limit=50&offset=0
Response: LogEntry[]
```

## Troubleshooting

### Dashboard shows only mock data

1. Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
2. Verify VPS is running: `make ps`
3. Test API endpoint: `curl https://vps.hermes.local:8000/api/v1/status`
4. Check browser console for errors (F12)

### Slow performance

1. Clear browser cache: `Ctrl+Shift+Delete`
2. Check network tab (DevTools) for slow API calls
3. Reduce polling interval if needed
4. Check VPS CPU/memory usage: `top`

### Logs not updating

1. Check if `/api/v1/logs/stream` exists
2. Enable browser support for EventSource (all modern browsers)
3. Dashboard falls back to polling if SSE unavailable

### Build fails

1. Delete `node_modules` and `.next`: `rm -rf node_modules .next`
2. Reinstall: `npm install`
3. Check TypeScript errors: `npm run type-check`

## Integration Checklist

- [ ] Dashboard created in `/apps/mission-control/`
- [ ] Dependencies installed: `npm install`
- [ ] Local dev tested: `npm run dev` → `http://localhost:3000`
- [ ] Environment variable configured: `.env.local`
- [ ] Mock data verified (dashboard should show even if API unavailable)
- [ ] vercel.json checked at repo root
- [ ] GitHub Actions configured for auto-deploy
- [ ] Vercel environment variables set
- [ ] VPS API endpoints documented
- [ ] Team notified of new dashboard URL

## Support

For issues or questions:

1. Check `README.md` in `/apps/mission-control/`
2. Review `ARCHITECTURE.md` for technical details
3. See `QUICK_START.md` for common commands
4. Check console logs (browser DevTools)

## Next Phase

Once API endpoints are implemented on VPS:

1. Test `/api/v1/status` → should return real Docker metrics
2. Test `/api/v1/agents/status` → should return real agent data
3. Test `/api/v1/logs/stream` → should stream real logs
4. Dashboard will auto-update without code changes

Dashboard design is production-ready. Just needs API backend implementation.
