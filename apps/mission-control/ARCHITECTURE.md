# Mission Control Architecture

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    MISSION CONTROL                      │
│                  (Next.js 14 SPA)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   Polling         SSE Logs      Fallback
   Every 30s       Real-time      Mock Data
        │              │              │
        └──────────────┼──────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   HERMES API (VPS)        │
         │  /api/v1/status           │
         │  /api/v1/agents/status    │
         │  /api/v1/mcps/status      │
         │  /api/v1/tasks            │
         │  /api/v1/logs/stream (SSE)│
         └───────────────────────────┘
```

## Component Hierarchy

```
page.tsx (main dashboard)
├── Navbar
│   └── Clock + Refresh Button
├── StatusBoard
│   ├── Docker Card (11/11)
│   ├── API Card (1250 req/min)
│   ├── PostgreSQL Card (28/100 conn)
│   ├── Redis Card (256 MB)
│   └── Service Health Grid
├── LogsViewer
│   └── Real-time Log Stream
├── TasksPanel
│   ├── Task Cards (in_progress, completed)
│   └── Summary Stats
├── AgentsMonitor
│   ├── Agent Status Cards
│   └── Activity Indicators
├── MCPsStatus
│   ├── MCP Health Cards (GitHub, HF, etc)
│   └── Status Badge
├── CrawbotBridge
│   ├── Command List
│   ├── Copy-to-Clipboard
│   └── Execute Button
└── Footer
```

## Data Flow

### Real-time Data (When API Available)

```
┌─────────────┐
│ API Server  │
│  (hermes-   │
│   api:8000) │
└─────┬───────┘
      │
      ├─ GET /status (JSON)
      │  Response:
      │  {
      │    docker: { healthy: 10, total: 11, services: [...] },
      │    api: { status: 'online', responseTime: 142, requestsPerMinute: 1250 },
      │    postgresql: { status: 'connected', connections: 28 },
      │    redis: { status: 'connected', memory: 256, keys: 4832 }
      │  }
      │
      ├─ GET /logs/stream (EventSource SSE)
      │  { timestamp, service, level, message }
      │
      └─ GET /agents/status (JSON)
         [{ name, model, status, lastActivity, tasksCompleted }]
```

### Mock Data (Fallback)

```
API Timeout (5s)
      ↓
generateMockSystemStatus()
  ├─ 11 Docker services (10 healthy, 1 unhealthy)
  ├─ 1250 req/min API throughput
  ├─ 28/100 PostgreSQL connections
  └─ 4832 Redis keys

generateMockAgents()
  ├─ HERMES (idle, 1248 tasks completed)
  ├─ MYSTIC (running, 642 tasks completed)
  ├─ ClawBot (idle, 3421 tasks completed)
  └─ Claude Code (running, 127 tasks completed)

generateMockMCPs()
  ├─ GitHub (active)
  ├─ HuggingFace (active)
  ├─ OpenRouter (active)
  ├─ Qdrant (active)
  ├─ Engram (active)
  └─ Filesystem (active)

generateMockTasks()
  ├─ Create Mission Control (85%, in_progress)
  ├─ Optimize RAG (100%, completed)
  ├─ Analyze patterns (60%, in_progress)
  └─ Process queue (100%, completed)

generateMockLogs()
  └─ 50 rotating logs with random timestamps
```

## Component Details

### StatusBoard
- **Purpose**: System-wide metrics at a glance
- **Data**: SystemStatus from `/api/v1/status`
- **Display**: 
  - 4 metric cards (Docker, API, PostgreSQL, Redis)
  - Progress bars for connection usage
  - Service health grid
- **Updates**: Every 30 seconds

### LogsViewer
- **Purpose**: Real-time service logs
- **Data**: LogEntry[] from `/api/v1/logs/stream` (SSE)
- **Display**:
  - Auto-scrolling log list (reverse chronological)
  - Level-colored badges (info, warn, error, debug)
  - Service name and timestamp
- **Auto-Update**: Every 3 seconds (generates mock if no SSE)
- **Height**: Scrollable container with max-height

### TasksPanel
- **Purpose**: Claude Code task progress
- **Data**: Task[] from `/api/v1/tasks`
- **Display**:
  - Task cards with progress bars
  - Status badges (pending, in_progress, completed, error)
  - Task count summary (total, in progress, completed)
- **Updates**: Every 30 seconds

### AgentsMonitor
- **Purpose**: Agent status and activity
- **Data**: Agent[] from `/api/v1/agents/status`
- **Display**:
  - Agent status cards (name, model, status)
  - Task completion count
  - Last activity timestamp
- **Status Indicators**:
  - idle (blue circle)
  - running (cyan pulse)
  - error (red warning)
- **Updates**: Every 30 seconds

### MCPsStatus
- **Purpose**: MCP server health
- **Data**: MCP[] from `/api/v1/mcps/status`
- **Display**:
  - 2x3 grid of MCP cards
  - Health status (active, inactive, error)
  - Last check timestamp
- **Updates**: Every 30 seconds

### CrawbotBridge
- **Purpose**: Execute Telegram commands
- **Data**: Static command list (hardcoded)
- **Display**:
  - Command selector
  - Copy-to-clipboard button
  - Execute button (opens Telegram)
- **Commands**:
  - `/status` — System health check
  - `/tasks` — List active tasks
  - `/logs hermes-api` — View API logs
  - `/deploy` — Trigger deployment

### Navbar
- **Purpose**: Navigation and refresh control
- **Display**:
  - HERMES OS branding
  - Live clock (updated every second)
  - Refresh button (disabled during fetch)

## Styling System

### Color Palette
```css
--primary: #0F0F0F     /* Primary background */
--accent: #00D9FF      /* Cyan - primary interaction */
--secondary: #6D28D9   /* Purple - gradients */
--light: #F5F5F5       /* Text color */
--dark-bg: #1A1A1A     /* Card backgrounds */
```

### Card Styling
```css
.card-base {
  @apply rounded-2xl border border-accent/10 bg-dark-bg/50 backdrop-blur-md p-6;
}
```

### Status Badges
```css
.status-badge-active   → bg-green-500/20 text-green-400
.status-badge-idle     → bg-blue-500/20 text-blue-400
.status-badge-warning  → bg-yellow-500/20 text-yellow-400
.status-badge-error    → bg-red-500/20 text-red-400
```

### Typography
```css
Font Family:
  - Display: Space Grotesk (headings)
  - Body: Inter (default text)
  - Mono: Courier Prime (code)

Font Sizes:
  - h1: 3.5rem (56px)
  - h2: 2.5rem (40px)
  - h3: 1.875rem (30px)
  - body: 1rem (16px)
  - sm: 0.875rem (14px)
  - xs: 0.75rem (12px)
```

## Animation Details

### Framer Motion
- **Entry animations**: opacity 0 → 1, y: 20 → 0
- **Stagger**: 0.05s delay between components
- **Hover effects**: scale 1.05, shadow-glow
- **Tap effects**: scale 0.95

### GSAP
- **Count-up**: animateCountUp(element, from, to, duration)
- **Glow effect**: animateGlowEffect(element)
- **Stagger**: staggerElements(elements, stagger)
- **Scroll reveal**: createScrollReveal(element)

### CSS Animations
```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
```

## Responsive Design

### Breakpoints
```css
Mobile (< 640px):   1 column
Tablet (640px):     2 columns
Desktop (1024px):   3 columns
```

### Grid Layout
```
Mobile:
┌──────────────────┐
│  StatusBoard     │
├──────────────────┤
│  LogsViewer      │
├──────────────────┤
│  TasksPanel      │
├──────────────────┤
│  AgentsMonitor   │
├──────────────────┤
│  MCPsStatus      │
├──────────────────┤
│  CrawbotBridge   │
└──────────────────┘

Desktop:
┌──────────────────┬──────────────────┬──────────────────┐
│  StatusBoard              │  TasksPanel              │
├──────────────────┬───────┼──────────────────┬────────┤
│  LogsViewer               │  MCPsStatus              │
├──────────────────┴───────┬┴──────────────────┴────────┤
│  AgentsMonitor           │  CrawbotBridge           │
└──────────────────────────┴──────────────────────────┘
```

## Performance Optimizations

1. **Code Splitting**: Next.js automatic route-based splitting
2. **Image Optimization**: No external images (SVG icons only)
3. **CSS**: Tailwind JIT compilation + autoprefixer
4. **Polling**: Configurable 30s interval (not too aggressive)
5. **Memoization**: useCallback for event handlers
6. **Bundle Size**: ~180KB gzipped (Next.js 14 optimized)

## State Management

- **React Hooks**: useState for component state
- **No Redux/Zustand**: Simple component-level state
- **Data Flow**: Top-down props (page.tsx → components)
- **Updates**: useEffect + setInterval + Promise.all

## Error Handling

1. **API Timeout**: 5 second window per request
2. **Network Error**: Caught in try-catch, logged to console
3. **Graceful Degradation**: Falls back to mock data
4. **User Feedback**: "Last updated" timestamp shows if data is stale

## Future Enhancements

- [ ] WebSocket real-time updates (vs SSE polling)
- [ ] Historical charts (24h, 7d, 30d trends)
- [ ] Alert threshold configuration
- [ ] Custom dashboard layouts
- [ ] Dark/Light theme toggle
- [ ] PWA support (offline mode)
- [ ] Slack integration
- [ ] Export logs to CSV
