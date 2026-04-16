# 🚀 Quickstart — Sonora Landing

Landing Sonora Digital Corp está **listo para correr**. Aquí te digo cómo.

## 1. Instalar y correr en dev

```bash
cd /home/mystic/hermes-os/apps/landing
npm install
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

## 2. Estructura de 9 secciones

✅ **Navbar** — flotante, sticky, blend glass effect  
✅ **Hero** — 100vh, efecto 3D light source, CTAs  
✅ **Vision** — scan light effect, "Sin código. Sin setup"  
✅ **Casos de uso** — 3 cards hover flotantes (Pastelería, Restaurante, Abogado)  
✅ **Pilares** — 4 secciones left/right con fade + slide  
✅ **Stats** — count-up números GSAP, trust badges  
✅ **Demo** — chat widget interactivo, typing effect  
✅ **Testimonios** — carousel, glow sigue cursor  
✅ **Footer** — CTA, contacto, links, gradient animado  

## 3. Personalizar colores

En `tailwind.config.ts`:

```ts
colors: {
  'primary-dark': '#0F0F0F',   // Fondo negro
  'accent': '#00D9FF',        // Cyan
  'secondary': '#6D28D9',      // Púrpura
  'light': '#F5F5F5',          // Texto claro
  'dark-bg': '#1A1A1A',        // Cards
}
```

## 4. Agregar Spline 3D Objects

Actualmente placeholders. Para 3D reales:

```bash
npm install @spline/react-spline
```

En `components/Hero.tsx`:

```tsx
import Spline from '@spline/react-spline'

// Reemplaza el div placeholder:
<Spline
  scene="https://prod.spline.design/XXXXX/scene.splinecode"
/>
```

Obtén tu URL en [spline.design](https://spline.design).

## 5. Build para producción

```bash
npm run build
npm start
```

O deploy a Vercel:

```bash
vercel deploy
```

## 6. CTAs customizables

En cada componente hay botones con:
- `onClick` handlers vacíos (agregar funciones)
- Clases Tailwind predefinidas
- Hover effects con Framer Motion

Ejemplo en `Hero.tsx`:

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  onClick={() => {
    // Tu lógica de demo o checkout
  }}
>
  Demo Interactivo
</motion.button>
```

## 7. Integrar con tu API

Para formularios (si agregas):

```ts
// En lib/animations.ts o nuevo archivo:
export async function submitDemoRequest(email: string) {
  const res = await fetch('/api/demo', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
  return res.json()
}
```

Luego en componentes:

```tsx
const handleDemo = async () => {
  await submitDemoRequest(email)
}
```

## 8. Scroll effects — cómo funcionan

**GSAP ScrollTrigger** en `lib/animations.ts`:

```ts
gsap.fromTo(element, 
  { opacity: 0, y: 40 },
  {
    opacity: 1,
    y: 0,
    scrollTrigger: {
      trigger: element,
      start: 'top 80%',  // Cuándo empieza
    }
  }
)
```

Los componentes usan esto automáticamente. Si cambias layout, llama:

```ts
import { refreshScrollTriggers } from '@/lib/animations'
refreshScrollTriggers()
```

## 9. Responsive check

Abre DevTools (F12) y prueba en:
- iPhone 12 (390px)
- iPad (768px)
- Desktop (1280px+)

Todos tienen layout responsive automático.

## 10. TypeScript strict

Strict mode está ON. Si agregas código:

```bash
npm run type-check
```

Corregirá type errors.

## 11. Dark mode — ya implementado

Todo el landing es dark mode. Si quieres light mode o toggle:

1. Agrega `next-themes`:
   ```bash
   npm install next-themes
   ```

2. Wrap en `app/layout.tsx`:
   ```tsx
   import { ThemeProvider } from 'next-themes'
   
   export default function RootLayout() {
     return (
       <ThemeProvider>
         {children}
       </ThemeProvider>
     )
   }
   ```

## 12. Analytics

Agrega Vercel Analytics o Mixpanel:

```bash
npm install @vercel/analytics
```

En `app/page.tsx`:

```ts
import { Analytics } from '@vercel/analytics/react'

export default function Home() {
  return (
    <>
      {/* componentes */}
      <Analytics />
    </>
  )
}
```

## 13. SEO

Metadata ya está en `app/layout.tsx`. Customiza:

```ts
export const metadata: Metadata = {
  title: 'Tu título',
  description: 'Tu descripción',
  openGraph: {
    title: 'OG title',
  }
}
```

## 14. Troubleshooting

| Problema | Solución |
|----------|----------|
| Scroll effects laggy | Verifica GSAP ease, aumenta `duration` |
| Spline no aparece | Checa URL spline scene, permisos CORS |
| TypeScript errors | `npm run type-check` luego arregla |
| Slow build | Limpia `.next`, reinstala node_modules |

## 15. Contacto para cambios

- Email: contacto@sonoradigital.com
- WhatsApp: +52 (555) 123-4567

---

**Listo.** Ya tienes un landing premium. A escalar 🚀
