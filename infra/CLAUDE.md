# agent:infra — Infrastructure
> Carga solo este archivo. Para contexto cross-dominio: `mem_search "docker vps nginx"` en Engram.

## Dominio
Docker Compose, Nginx, VPS, GitHub Actions CI/CD, N8N workflows, executor.

## Archivos clave
- `docker-compose.vps.yml` — compose de producción (usar en VPS)
- `docker-compose.yml` — compose local/dev
- `nginx/nginx.conf` — reverse proxy + HSTS + CSP + rate limit
- `executor/executor.py` — servicio host:9001 para Claude Code remoto
- `n8n-workflows/*.json` — workflows de automatización
- `migrations/` — SQL migrations (Alembic las maneja desde backend)
- `.env` — secrets reales (NUNCA en git — solo `.env.example`)

## Servicios y puertos
| Servicio | Puerto | Health |
|---|---|---|
| postgres | 5432 | - |
| redis | 6379 | - |
| qdrant | 6333 | GET /healthz |
| ollama | 11434 | GET /api/tags |
| evolution | 8080 | - |
| n8n | 5678 | - |
| hermes-api | 8000 | GET /status |
| clawbot | 3003 | GET /health |
| frontend | 3000 | - |

## Reglas críticas
- `docker compose` (v2) — NUNCA `docker-compose`
- Red: `hermes_net` o `hermes_network`
- Containers con prefijo `hermes_`
- Solo Nginx expuesto al exterior (80/443) — todo lo demás en red interna
- Git en VPS: `git -C /home/mystic/hermes-os <cmd>`
- rsync: `-e "ssh -F /home/mystic/.ssh/config"` (alias `vps`, sin IPv6 raw)

## Deploy
Push a `main` → GitHub Actions → rsync → VPS → `docker compose up -d`
Notificación automática a CEO via Telegram al terminar.

## Nginx rate limits
- api: 30r/m
- auth: 5r/m  
- bots: 100r/m
