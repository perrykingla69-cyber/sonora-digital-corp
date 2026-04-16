# 🏗️ Arquitectura — Sonora Landing

Guía técnica para entender, extender y mantener el landing.

## Filosofía de diseño

1. **Client Components** — Framer Motion y event listeners requieren `'use client'`
2. **Composition over configuration** — Cada sección es un componente independiente
3. **GSAP para scroll complejos** — Framer Motion para micro-interactions
4. **Tailwind utility-first** — Sin custom CSS excepto en `globals.css`
5. **TypeScript strict** — No `any`, tipos definidos explícitos

## Flujo de datos

```
app/page.tsx (layout master)
  ├── Navbar.tsx (gestiona scroll listener)
  ├── Hero.tsx (3D rotation + scroll tracking)
  ├── VisionStatement.tsx (GSAP clip-path)
  ├── CasosDeUso.tsx (hover state local)
  ├── Pilares.tsx (useInView desde react-intersection-observer)
  ├── Stats.tsx (GSAP count-up)
  ├── DemoChat.tsx (display messages con delay)
  ├── Testimonios.tsx (carousel scroll + glow tracking)
  └── Footer.tsx (gradient animation continua)
```

**Estado**: Local en cada componente (no Redux/Zustand necesario).

## Stack GSAP

### Registrar plugins

En `lib/animations.ts`:

```ts
import gsap from 'gsap'
import ScrollTrigger from 'gsap/ScrollTrigger'

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger)
}
```

Siempre check `typeof window` para SSR safety.

### Patrones comunes

**1. Reveal on scroll (fade in + slide)**

```ts
gsap.fromTo(element,
  { opacity: 0, y: 40 },
  {
    opacity: 1, y: 0,
    duration: 0.8,
    scrollTrigger: {
      trigger: element,
      start: 'top 80%',
      toggleActions: 'play none none none',
    }
  }
)
```

**2. Count-up numbers**

```ts
gsap.to(obj, {
  value: endValue,
  duration: 2,
  scrollTrigger: { trigger, start: 'top 80%' },
  onUpdate() { element.textContent = Math.floor(obj.value) }
})
```

**3. Clip-path scan**

```ts
gsap.fromTo(element,
  { clipPath: 'polygon(0 0, 0 0, 0 100%, 0 100%)' },
  {
    clipPath: 'polygon(0 0, 100% 0, 100% 100%, 0 100%)',
    duration: 1.5,
    scrollTrigger: { trigger, start: 'top 70%' }
  }
)
```

**4. Parallax**

```ts
gsap.to(element, {
  y: (i, target) => -ScrollTrigger.getVelocity(target) * speed,
  overwrite: 'auto',
  scrollTrigger: {
    onUpdate: (self) => {
      gsap.to(element, {
        y: -self.getVelocity() * speed,
        overwrite: 'auto',
        duration: 0.5,
      })
    }
  }
})
```

## Stack Framer Motion

### Patrones comunes

**1. Hover animations**

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

**2. Animate on view**

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.8 }}
>
  Content
</motion.div>
```

**3. Continuous animation**

```tsx
<motion.div
  animate={{
    rotate: 360,
    scale: [1, 1.1, 1],
  }}
  transition={{ duration: 3, repeat: Infinity }}
/>
```

## Tailwind customizations

### Variables CSS en `globals.css`

```css
:root {
  --primary: #0F0F0F;
  --accent: #00D9FF;
  --secondary: #6D28D9;
  --light: #F5F5F5;
  --dark-bg: #1A1A1A;
}
```

### Extend config

En `tailwind.config.ts`:

```ts
theme: {
  extend: {
    colors: {
      'primary-dark': '#0F0F0F',
      'accent': '#00D9FF',
    },
    backgroundImage: {
      'hero-gradient': 'linear-gradient(135deg, #0F0F0F 0%, #1a0a2e 50%, #16213e 100%)',
    },
    boxShadow: {
      'glow': '0 0 20px rgba(0, 217, 255, 0.3)',
    }
  }
}
```

Luego usa en componentes:

```tsx
<div className="bg-hero-gradient shadow-glow">
  Content
</div>
```

## Cómo agregar una nueva sección

### 1. Crear componente

Archivo: `components/NewSection.tsx`

```tsx
'use client'

import { motion } from 'framer-motion'
import { useEffect, useRef } from 'react'

export function NewSection() {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Inicializar GSAP aquí si es necesario
  }, [])

  return (
    <section ref={ref} className="relative w-full py-32 bg-primary-dark">
      {/* Content */}
    </section>
  )
}
```

### 2. Agregar a page.tsx

```tsx
import { NewSection } from '@/components/NewSection'

export default function Home() {
  return (
    <main>
      {/* ... otros componentes ... */}
      <NewSection />
      <Footer />
    </main>
  )
}
```

### 3. Styles

- Usa clases Tailwind
- Si necesitas custom CSS, agrega en `globals.css` o en el componente con `<style>` tag
- Respeta la paleta de colores

## Responsividad

Breakpoints Tailwind estándar:

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
```

Uso en componentes:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Automáticamente responsivo */}
</div>
```

## Performance

### Lazy loading

GSAP ScrollTrigger ya hace lazy load de animations (no ejecuta hasta visible).

```ts
scrollTrigger: {
  trigger: element,
  toggleActions: 'play none none none', // Solo play, nunca repeat
}
```

### Image optimization

Usa `next/image` para imágenes:

```tsx
import Image from 'next/image'

<Image
  src="/path/to/image.png"
  alt="Description"
  width={400}
  height={300}
  priority={false} // lazy load
/>
```

### Code splitting

Next.js hace code splitting automático por ruta. Para dynamic imports:

```tsx
const HeavyComponent = dynamic(() => import('@/components/Heavy'), {
  loading: () => <p>Loading...</p>,
})
```

## Testing

### Type checking

```bash
npm run type-check
```

Verifica tipos sin compilar.

### Linting

```bash
npm run lint
```

Usa `.eslintrc.json` predefinido.

## Deployment

### Vercel (recomendado)

```bash
vercel deploy
```

Auto-detecta Next.js, builds optimizados.

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package* .
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### VPS manual

```bash
npm run build
npm start
```

Luego configura Nginx como reverse proxy:

```nginx
location / {
  proxy_pass http://localhost:3000;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection 'upgrade';
}
```

## Debugging

### GSAP

```ts
// En lib/animations.ts
gsap.config({ force3D: true }); // Força GPU
gsap.set("*", { force3D: true }); // Para todos
```

### Framer Motion

Habilita timeline inspector en dev:

```tsx
import { MotionConfig } from 'framer-motion'

<MotionConfig reducedMotion="user">
  {/* Components */}
</MotionConfig>
```

### ScrollTrigger

Visualiza triggers:

```ts
scrollTrigger: {
  trigger: element,
  markers: true, // Muestra líneas rojas/verdes en dev
}
```

## Convenciones

1. **Nombres**: PascalCase para componentes, camelCase para funciones/variables
2. **Imports**: Agrupa stdlib, terceros, luego locales
3. **Props**: Desestructura explícitamente, no spread
4. **Exports**: Default export para componentes, named para utilidades
5. **CSS**: Tailwind primeiro, custom CSS si es necesario

## Gotchas

1. **SSR + GSAP**: Siempre wrap con `if (typeof window !== 'undefined')`
2. **GSAP + Framer**: Evita animar el mismo elemento con ambos (conflictos)
3. **ScrollTrigger + Dynamic content**: Llama `refreshScrollTriggers()` después de agregar/remover elementos
4. **Mobile**: Reduce blur effects (performance), mantén animations cortas
5. **Touch**: Algunos efectos scroll no funcionan en mobile — usa Framer Motion para touch

## Extensiones futuras

- [ ] Multi-idioma (i18n + next-intl)
- [ ] Dark/Light toggle
- [ ] Custom fonts (Google Fonts ya importadas)
- [ ] Blog integrado
- [ ] CMS (Contentful, Sanity)
- [ ] E-commerce (Stripe integration)
- [ ] Email newsletter (Resend API)
- [ ] Analytics (Vercel Analytics, Mixpanel)
