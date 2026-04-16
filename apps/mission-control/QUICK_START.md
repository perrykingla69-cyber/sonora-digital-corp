# Mission Control — Quick Start

## 1. Install

```bash
cd apps/mission-control
npm install
```

## 2. Configure

Create `.env.local`:

```bash
echo "NEXT_PUBLIC_API_URL=https://vps.hermes.local:8000" > .env.local
```

(Optional — uses mock data by default)

## 3. Develop

```bash
npm run dev
```

Opens `http://localhost:3000`

## 4. Build & Deploy

### Local
```bash
npm run build
npm run start
```

### Vercel
```bash
git add .
git commit -m "chore: add Mission Control dashboard"
git push origin main
```

Auto-deploys via GitHub Actions.

## Features

- **Real-time System Status**: Docker (11 services), API metrics, DB connections, Redis
- **Live Logs**: Auto-scrolling service logs with level colors
- **Task Progress**: Claude Code tasks with % complete
- **Agent Monitor**: HERMES, MYSTIC, ClawBot, Claude Code status
- **MCP Health**: GitHub, HuggingFace, OpenRouter, Qdrant, Engram
- **Telegram Bridge**: Copy-paste bot commands from dashboard

## Mock Data

If VPS is unavailable, dashboard automatically uses realistic mock data:

- 10/11 Docker services healthy
- 1,250 API requests/min
- 28 PostgreSQL connections
- 50 recent logs
- 4 agent status cards

## Component Structure

```
app/
  page.tsx          ← Main dashboard grid
  globals.css       ← Design tokens
  layout.tsx        ← Metadata

components/
  Navbar.tsx        ← Clock + refresh
  StatusBoard.tsx   ← System metrics (4 cards)
  LogsViewer.tsx    ← Real-time logs
  TasksPanel.tsx    ← Claude Code tasks
  AgentsMonitor.tsx ← Agent status
  MCPsStatus.tsx    ← MCP health
  CrawbotBridge.tsx ← Telegram commands

lib/
  types.ts          ← TypeScript interfaces
  mockdata.ts       ← Fake data generator
  api.ts            ← API client + fallback
  animations.ts     ← GSAP utilities
```

## Colors

```css
--primary: #0F0F0F     /* Dark bg */
--accent: #00D9FF      /* Cyan highlights */
--secondary: #6D28D9   /* Purple gradients */
--light: #F5F5F5       /* Text */
--dark-bg: #1A1A1A     /* Cards */
```

## Troubleshooting

### "Port 3000 already in use"
```bash
npm run dev -- -p 3001
```

### "Cannot find module"
```bash
rm -rf node_modules package-lock.json
npm install
```

### "API unreachable"
- Dashboard uses mock data automatically
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify VPS running: `make ps`

## Performance Tips

- Clear browser cache: `Ctrl+Shift+Delete`
- Enable gzip: Nginx already configured
- Use Chrome DevTools → Performance tab to profile

## Next Steps

1. **Customize colors**: Edit `tailwind.config.ts`
2. **Add alerts**: Modify `StatusBoard.tsx` thresholds
3. **Enable WebSocket**: Replace SSE in `LogsViewer.tsx`
4. **Dark/Light theme**: Add toggle in `Navbar.tsx`
5. **Export logs**: Add CSV download button

See full docs in `README.md`
