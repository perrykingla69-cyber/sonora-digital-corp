# 🔗 Integración — Sonora Landing con HERMES

Guía para integrar el landing con el stack existente de Sonora Digital Corp.

## Arquitectura general

```
Landing (Next.js 14)
    ↓
API HERMES (/api/v1)
    ↓
PostgreSQL RLS + Redis
    ↓
LLMs: OpenRouter (Gemini, GLM-Z1)
```

## 1. Endpoint de Demo

Cuando un usuario hace click en "Solicita Demo", debe crear un request en la DB.

### 1.1 Crear tabla en PostgreSQL

```sql
-- En /home/mystic/hermes-os/infra/migrations/003_demo_requests.sql

CREATE TABLE demo_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT now(),
  email VARCHAR(255) NOT NULL,
  name VARCHAR(255),
  phone VARCHAR(20),
  company VARCHAR(255),
  niche VARCHAR(50),
  message TEXT,
  status VARCHAR(20) DEFAULT 'pending', -- pending, scheduled, completed
  tenant_id UUID REFERENCES tenants(id),
  notes TEXT
);

CREATE INDEX idx_demo_requests_email ON demo_requests(email);
CREATE INDEX idx_demo_requests_status ON demo_requests(status);
```

### 1.2 Endpoint API

En `/home/mystic/hermes-os/apps/api/app/routes/demo.py`:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])

class DemoRequest(BaseModel):
    email: EmailStr
    name: str
    phone: str | None = None
    company: str
    niche: str | None = None
    message: str | None = None

@router.post("/request")
async def submit_demo_request(req: DemoRequest, db: AsyncSession = Depends(get_db)):
    """Envía solicitud de demo desde landing"""
    
    # Guardar en DB
    demo = DemoRequest_Model(**req.dict())
    db.add(demo)
    await db.commit()
    
    # Enviar email de confirmación
    await send_email(
        to=req.email,
        subject="Confirmamos tu solicitud de demo — Sonora Digital Corp",
        template="demo_confirmation",
        context={"name": req.name, "demo_id": demo.id}
    )
    
    # Notificar al CEO vía Telegram
    await notify_ceo(f"Nueva solicitud de demo de {req.company}")
    
    return {"status": "success", "demo_id": str(demo.id)}
```

### 1.3 Integrar en Landing

En `components/Hero.tsx` y `Footer.tsx`:

```tsx
'use client'

import { useState } from 'react'

export function DemoButton() {
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState('')

  const handleDemo = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/demo/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          name: 'Guest',
          company: 'Not specified',
        }),
      })
      
      if (res.ok) {
        alert('¡Gracias! Nos pondremos en contacto pronto.')
        setEmail('')
      }
    } catch (error) {
      alert('Error al enviar. Intenta de nuevo.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <input
        type="email"
        placeholder="tu@email.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={handleDemo} disabled={isLoading}>
        {isLoading ? 'Enviando...' : 'Solicita Demo'}
      </button>
    </div>
  )
}
```

## 2. Landing en Docker

Para que el landing corra en docker-compose junto a hermes-api:

### 2.1 Dockerfile

```dockerfile
# /home/mystic/hermes-os/apps/landing/Dockerfile

FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json .
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]
```

### 2.2 docker-compose.yml

Agregar servicio `landing`:

```yaml
# En /home/mystic/hermes-os/docker-compose.yml

services:
  landing:
    build:
      context: ./apps/landing
      dockerfile: Dockerfile
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://hermes-api:8000
      - NODE_ENV=production
    depends_on:
      - hermes-api
    networks:
      - hermes-network
```

Luego:

```bash
docker compose up -d landing
```

## 3. Nginx reverse proxy

Para servir landing en `/` y API en `/api`:

```nginx
# /home/mystic/hermes-os/infra/nginx/sites-enabled/sonora

server {
  server_name sonoradigital.com www.sonoradigital.com;

  listen 443 ssl http2;
  ssl_certificate /etc/letsencrypt/live/sonoradigital.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/sonoradigital.com/privkey.pem;

  # Landing
  location / {
    proxy_pass http://landing:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
  }

  # API
  location /api {
    proxy_pass http://hermes-api:8000;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}

# Redirect HTTP a HTTPS
server {
  listen 80;
  server_name sonoradigital.com www.sonoradigital.com;
  return 301 https://$server_name$request_uri;
}
```

Luego:

```bash
sudo systemctl restart nginx
```

## 4. Email de confirmación

Usa Resend API para enviar emails automáticos:

```bash
npm install resend
```

En `apps/api/app/services/email.py`:

```python
from resend import Resend

resend = Resend(os.getenv("RESEND_API_KEY"))

async def send_demo_confirmation(email: str, name: str):
    resend.emails.send(
        from_="no-reply@sonoradigital.com",
        to=email,
        subject="Confirmamos tu solicitud de demo",
        html=f"""
        <h1>Hola {name},</h1>
        <p>Gracias por tu interés en Sonora Digital Corp.</p>
        <p>Nos pondremos en contacto en las próximas 24 horas.</p>
        <a href="https://sonoradigital.com">Volver al sitio</a>
        """,
    )
```

## 5. Analytics

Habilita Vercel Analytics en el landing:

```bash
npm install @vercel/analytics
```

En `app/page.tsx`:

```tsx
import { Analytics } from '@vercel/analytics/react'

export default function Home() {
  return (
    <main>
      {/* componentes */}
      <Analytics />
    </main>
  )
}
```

Configurar en vercel.com para ver métricas.

## 6. Subdominio de staging

Para testing antes de prod:

```bash
# Deploy a staging.sonoradigital.com
vercel deploy --prod --target production
```

Luego en Nginx:

```nginx
server {
  server_name staging.sonoradigital.com;
  listen 443 ssl;
  
  location / {
    proxy_pass http://landing:3001; # Puerto diferente
  }
}
```

## 7. CI/CD integration

En GitHub Actions (`.github/workflows/deploy-landing.yml`):

```yaml
name: Deploy Landing

on:
  push:
    branches: [main]
    paths:
      - 'apps/landing/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: |
          cd apps/landing
          npm install
          npm run build
      
      - name: Deploy to VPS
        run: |
          ssh -i ${{ secrets.VPS_SSH_KEY }} root@${{ secrets.VPS_HOST }} \
            "cd hermes-os && docker compose up -d --build landing"
```

## 8. Monitoreo

Agregar healthcheck en docker-compose:

```yaml
landing:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3000"]
    interval: 30s
    timeout: 10s
    retries: 3
```

Monitorea en dashboard interno:

```python
# apps/api/app/routes/health.py

@router.get("/health/landing")
async def landing_health():
    """Check landing service status"""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("http://landing:3000", timeout=5)
            return {"status": "healthy" if resp.status_code == 200 else "unhealthy"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
```

## 9. SEO y meta tags

Landing ya tiene metadata en `app/layout.tsx`. Agrega meta tags dinámicos si es necesario:

```tsx
// app/layout.tsx
export const metadata: Metadata = {
  title: 'Sonora Digital Corp - Automatiza tu negocio con IA',
  description: 'Agentes IA que trabajan 24/7 para tu negocio. Sin código. Sin setup.',
  canonical: 'https://sonoradigital.com',
  openGraph: {
    type: 'website',
    url: 'https://sonoradigital.com',
    title: 'Sonora Digital Corp',
    description: 'Agentes IA automatizados para tu negocio',
    images: [{ url: 'https://sonoradigital.com/og-image.png' }],
  },
  robots: 'index, follow',
  keywords: 'IA, automatización, agentes digitales, México',
}
```

## 10. Cron jobs

Para enviar emails de follow-up a demo requests no respondidas:

```python
# apps/api/app/tasks/demo_followup.py

from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def send_demo_followup():
    """Envia follow-up a demo requests sin respuesta después de 2 días"""
    
    cutoff = datetime.utcnow() - timedelta(days=2)
    pending = db.query(DemoRequest).filter(
        DemoRequest.status == 'pending',
        DemoRequest.created_at < cutoff
    ).all()
    
    for req in pending:
        await send_email(
            to=req.email,
            subject="¿Aún interesado en Sonora Digital?",
            template="demo_followup",
            context={"name": req.name}
        )
        req.status = 'follow-up-sent'
    
    db.commit()
```

Configurar en `infra/celery/celery.conf`:

```python
beat_schedule = {
    'demo-followup': {
        'task': 'app.tasks.demo_followup.send_demo_followup',
        'schedule': crontab(hour=9, minute=0),  # 9am diario
    },
}
```

---

## Checklist de integración

- [ ] Crear tabla `demo_requests` en PostgreSQL
- [ ] Crear endpoint `/api/v1/demo/request`
- [ ] Integrar formulario en componentes (Hero, Footer)
- [ ] Crear Dockerfile para landing
- [ ] Agregar `landing` a docker-compose.yml
- [ ] Configurar Nginx reverse proxy
- [ ] Habilitar HTTPS con Let's Encrypt
- [ ] Configurar Resend API para emails
- [ ] Habilitar Vercel Analytics
- [ ] Crear GitHub Actions workflow
- [ ] Configurar healthcheck
- [ ] Agregar RESEND_API_KEY a .env
- [ ] Testear deploy end-to-end

---

**Estado**: Listo para integrar

**Próximo**: Ejecutar pasos 1-5 para MVP funcional
