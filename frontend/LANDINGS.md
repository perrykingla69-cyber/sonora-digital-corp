# Landings Especializados — HERMES

## Resumen

Se crearon 3 landings Next.js 14 SSG (pre-renderizadas) + componentes reutilizables para dos verticales clave:

1. **Landing General** (`/`) - Resumen HERMES para todas las PYMEs
2. **Landing Contadores** (`/contadores`) - Solución fiscal MX, NOMs, alertas, reportes DIOT/RESICO
3. **Landing Artistas** (`/artistas`) - Distribución digital, regalías, monetización automática

## Archivos Creados

### Páginas Principales
- `src/app/contadores/page.tsx` — Landing contadores (5.2 KB compilado, 99.3 KB gzipped)
- `src/app/artistas/page.tsx` — Landing artistas (5.1 KB, 99.8 KB)
- `src/app/page.tsx` — Landing general (actualizada con sección especializada)

### Páginas de Conversión
- `src/app/contadores/demo/page.tsx` — Form solicitud demo (2.3 KB, 96.9 KB)
- `src/app/artistas/onboarding/page.tsx` — Form signup creadores (2.4 KB, 97 KB)

### Componentes Reutilizables (`src/components/landing/`)
- `HermesEyeLogo.tsx` — SVG logo (eye icon con gradientes dorados)
- `Hero.tsx` — Sección hero con badge, título, descripción, CTA (acepta variantes)
- `Features.tsx` — Grid 2-col features con iconos (responsive, variantes de color)
- `CaseStudy.tsx` — Sección caso de uso/problema/solución/resultado
- `Navigation.tsx` — Navbar reutilizable (volver/login)
- `Footer.tsx` — Footer consistente con links

### Layout & Metadata
- `src/app/contadores/layout.tsx` — Metadata SEO contadores
- `src/app/artistas/layout.tsx` — Metadata SEO artistas
- `src/app/layout.tsx` — Layout raíz (actualizado con metadata genérica)

### Recursos Estáticos
- `public/sitemap.xml` — Sitemap con 6 URLs principales
- `public/robots.txt` — Robots exclusiones (/api, /admin, /.next)

## Características Técnicas

### Performance & SEO
- **SSG (Static Site Generation)**: Todas las páginas pre-renderizadas en build time
- **Metadata OpenGraph**: Cada landing tiene title, description, OG tags para redes
- **Mobile-first responsive**: Tailwind breakpoints sm/md/lg
- **Dark mode**: Colores HERMES (dorado #D4AF37, verde bosque, azul contador, púrpura artista)
- **Next.js Image Optimization**: Preparado para imágenes futuras

### Build & Deploy
- **Next.js 14.2.3** con App Router
- **Output mode: standalone** (compatible Hostinger Node.js 18+)
- **Package.json scripts**:
  - `npm run build` → Next.js build SSG (bundler turbopack)
  - `npm start` → Next.js server modo standalone
- **Dockerfile**: Multi-stage, image ~150 MB

### Estilos & Tokens
```tailwind
Colors (extensión sovereign):
  - gold: #D4AF37 (dorado cálido)
  - green: #2D6A4F (bosque)
  - bg: #F8F6F1 (blanco perla)
  - text: #1C1C1E (casi negro suave)

Dark background: #0a0500 (muy oscuro para particle effects)
Variantes landing:
  - contador: azul (bg-blue-500/10, text-blue-400)
  - artista: púrpura (bg-purple-500/10, text-purple-400)
  - general: dorado #D4AF37
```

## Rutas Disponibles

```
/                               → Landing general (hero + features + planes)
/contadores                     → Landing contadores especializado
/contadores/demo                → Form solicitud demo
/artistas                       → Landing artistas especializado
/artistas/onboarding            → Form signup creadores
/login                          → Login existente
/dashboard                      → Dashboard existente (post-login)
```

## Componentes Reutilizables

### Hero
```tsx
<Hero
  badge="Para Contadores y Despachos Fiscales"
  title={<>HERMES para<br /><span className="text-blue-400">Contadores</span></>}
  subtitle="Normatividad fiscal MX en IA..."
  cta={{ text: 'Solicita Demo Gratis', href: '/contadores/demo' }}
  variant="contador"
/>
```

### Features
```tsx
<Features
  features={[
    { icon: FileText, title: 'NOMs', description: '...' },
    // ... más features
  ]}
  variant="contador"
  title="Diseñado para tu despacho"
/>
```

### CaseStudy
```tsx
<CaseStudy
  variant="contador"
  title="Contador con 50 clientes"
  problem="..."
  solution="..."
  result="..."
  metric="15 horas/semana → 10 horas/semana"
/>
```

## SEO & Metadata

### Landing General
- Title: `HERMES — SaaS IA para tu negocio`
- Keywords: contabilidad, CFDI, SAT, IA, Mexico

### Landing Contadores
- Title: `HERMES para Contadores | Normatividad MX + IA`
- Keywords: contador, despacho fiscal, NOM-251, DIOT, RESICO, SAT

### Landing Artistas
- Title: `HERMES para Creadores | Distribución + Monetización Automática`
- Keywords: música, distribución digital, Spotify, regalías, creador independiente, podcast

Todos incluyen `og:title`, `og:description`, `og:type: website` para compartir en redes.

## Notas Técnicas

### Correcciones Realizadas
1. **TypeScript error en (app)/agents/page.tsx**: Duplicate key 'online' en object spread. Solución: mover spread al inicio para que la asignación posterior lo sobrescriba.
2. **Symlink app→src/app**: Agregado para compatibilidad con referencias directas.

### Próximos Pasos Opcionales
1. **Imágenes heroicas**: Reemplazar placeholders con vector art (SVG de contador/artista)
2. **Testimonios reales**: Agregar carousel con testimonios (Framer Motion)
3. **Analytics**: Integrar Vercel Analytics o Mixpanel para tracking conversiones
4. **Email integration**: Endpoint `/api/demo-request` y `/api/artist-signup` para guardar en DB
5. **PWA**: Agregar service worker si se requiere offline support

## Compilación & Tamaños

```
✓ Compilado exitosamente
  /                               ○ 4.89 kB → 99.3 kB
  /artistas                       ○ 5.16 kB → 99.8 kB
  /artistas/onboarding            ○ 2.38 kB → 97.0 kB
  /contadores                     ○ 4.70 kB → 99.3 kB
  /contadores/demo                ○ 2.30 kB → 96.9 kB
  
  First Load JS shared by all     87.3 kB
  ├ chunks/23-d5ce99f95caa154a.js 31.6 kB
  ├ chunks/fd9d1056-...js         53.6 kB
```

## Deploy a Hostinger

1. **Build**:
   ```bash
   npm install
   npm run build
   ```

2. **Start** (standalone mode):
   ```bash
   npm start
   ```

3. **Nginx proxy** (reverse proxy a :3000):
   ```nginx
   location / {
     proxy_pass http://localhost:3000;
     proxy_set_header Host $host;
     proxy_set_header X-Real-IP $remote_addr;
   }
   ```

4. **PM2 (opcional)**:
   ```bash
   pm2 start npm --name hermes -- start
   pm2 save
   ```

---

**Creado**: 2026-04-08  
**Autor**: Claude Code  
**Proyecto**: HERMES OS / Sonora Digital Corp
