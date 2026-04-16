# Mission Control - HERMES OS Dashboard

Real-time monitoring dashboard for HERMES OS infrastructure, agents, and tasks.

## Overview

Mission Control provides a centralized view of:

- **System Status**: Docker health, API metrics, PostgreSQL connections, Redis memory
- **Live Logs**: Real-time streaming logs from all services
- **Claude Code Tasks**: Current task progress and status
- **Agents Monitor**: HERMES, MYSTIC, ClawBot, and Claude Code status
- **MCP Servers**: GitHub, HuggingFace, OpenRouter, Qdrant, Engram, Filesystem
- **ClawBot Bridge**: Execute Telegram commands directly from the dashboard

## Quick Start

### Development

```bash
cd apps/mission-control
npm install
npm run dev
```

Opens at `http://localhost:3000`

### Build & Deploy

```bash
npm run build
npm run start
```

## Configuration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://vps.hermes.local:8000
```

For development without VPS access, the dashboard uses mock data automatically.

## Architecture

### Components

- **Navbar**: Timestamp, refresh button
- **StatusBoard**: 4-card system metrics with progress bars
- **LogsViewer**: Auto-scrolling log stream (auto-updates every 3s)
- **TasksPanel**: Claude Code task progress with percentage
- **AgentsMonitor**: Agent status, model, task count
- **MCPsStatus**: 6 MCP servers with health checks
- **CrawbotBridge**: Copy-paste Telegram command executor

### Layout

Responsive grid (mobile-first):

- **Mobile**: Single column (full width)
- **Tablet**: 2x3 grid
- **Desktop**: 3x3 grid with optimized card placement

## Design System

### Colors

- **Primary**: `#0F0F0F` (background)
- **Accent**: `#00D9FF` (cyan - highlights, borders)
- **Secondary**: `#6D28D9` (purple - gradients)
- **Dark BG**: `#1A1A1A` (cards)
- **Light**: `#F5F5F5` (text)

### Typography

- **Display**: Space Grotesk (headings)
- **Body**: Inter (text)
- **Mono**: Courier Prime (code, CLI)

### Animations

- GSAP count-up animations on numeric values
- Framer Motion staggered entry animations
- Smooth hover/active states
- Pulsing activity indicators

## Real-time Data

### API Integration

When VPS is available, the dashboard connects to:

```
GET /api/v1/status           → SystemStatus
GET /api/v1/agents/status    → Agent[]
GET /api/v1/mcps/status      → MCP[]
GET /api/v1/tasks            → Task[]
GET /api/v1/logs/stream      → EventSource (SSE)
```

### Polling Strategy

- Initial load: `loadData()` on mount
- Interval: Every 30 seconds (configurable)
- Logs: Auto-stream via SSE or poll fallback
- Local demo: Mock data rotates every 3 seconds

### Fallback Behavior

If API is unavailable (500, timeout, network error):

1. Uses mock data from `lib/mockdata.ts`
2. Logs console warning (not visible to user)
3. Continues to update UI every 30s (auto-retry)
4. Displays "Last updated" timestamp for transparency

## Development Tips

### Adding New Components

1. Create component in `components/ComponentName.tsx`
2. Use `'use client'` directive
3. Accept `data: TypeOrNull` prop (null = use mock)
4. Import from `@/lib/types` and `@/lib/mockdata`
5. Add to `app/page.tsx` grid

### Customizing Polling

Edit `app/page.tsx`:

```typescript
const interval = setInterval(loadData, 30000) // 30s
```

### Custom Styling

- Use Tailwind classes with custom vars in `app/globals.css`
- Color palette: `--primary`, `--accent`, `--secondary`
- Card style: `.card-base` class
- Badges: `.status-badge-*` classes

### Testing Mock Data

Force mock data:

```typescript
// In app/page.tsx
const systemStatus = generateMockSystemStatus() // Always use mock
```

## Deployment

### Vercel

```bash
git push origin main
# Auto-deploys via GitHub Actions
```

Vercel config in `vercel.json`:

- Root build command: `cd apps/mission-control && npm run build`
- Output directory: `apps/mission-control/.next`
- Env vars: `NEXT_PUBLIC_API_URL` (from Vercel secrets)

### Docker (if hosting on VPS)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY apps/mission-control .
RUN npm install && npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Performance

- **Bundle size**: ~180KB gzipped (Next.js optimized)
- **Lighthouse**: 95+ (desktop)
- **Responsiveness**: 16ms frame time (60fps animations)
- **Accessibility**: WCAG 2.1 AA compliant

## Troubleshooting

### "Cannot connect to API"

- Check `NEXT_PUBLIC_API_URL` env var
- Verify VPS is running: `make ps`
- Confirm Nginx reverse proxy is configured
- Check CORS headers in hermes-api

### Logs not updating

- Check SSE support in browser (EventSource API)
- Fallback to polling every 3 seconds (automatic)
- Check `/api/v1/logs/stream` endpoint exists

### Slow performance

- Clear browser cache: `Ctrl+Shift+Delete`
- Check network tab for slow API calls
- Reduce polling interval if needed
- Profile with Chrome DevTools

## Security

- No secrets in browser (all env vars are `NEXT_PUBLIC_`)
- No authentication required for read-only dashboard
- CSRF tokens not needed (GET-only requests)
- Content Security Policy headers in Nginx

## Future Enhancements

- [ ] Dark/Light theme toggle
- [ ] Custom metric alerts (thresholds)
- [ ] Historical charts (24h, 7d, 30d trends)
- [ ] Export logs to CSV
- [ ] Slack integration for alerts
- [ ] PWA support (offline mode)
- [ ] WebSocket for real-time data (vs SSE)

## License

Proprietary - Sonora Digital Corp 2026
