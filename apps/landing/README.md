# Sonora Digital Corp — Landing Page

Landing premium con scroll effects avanzados para Sonora Digital Corp. MVP visual completo en Next.js 14.

## Stack técnico

- **Next.js 14** — App Router, Server Components
- **React 19** — Compatible
- **TypeScript** — Strict mode
- **Tailwind CSS** — Utility-first styling con variables personalizadas
- **Framer Motion** — Animations suaves
- **GSAP + ScrollTrigger** — Scroll effects complejos
- **Spline.design** — Placeholders para objetos 3D (listos para embed)

## Estructura

```
apps/landing/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page principal
│   └── globals.css         # Tailwind + variables CSS
├── components/
│   ├── Navbar.tsx          # Barra de navegación flotante
│   ├── Hero.tsx            # Sección hero con efecto 3D
│   ├── VisionStatement.tsx  # Vision statement con scan light
│   ├── CasosDeUso.tsx       # 3 casos con cards interactivas
│   ├── Pilares.tsx          # 4 pilares left/right alternados
│   ├── Stats.tsx            # Números con count-up GSAP
│   ├── DemoChat.tsx         # Chat demo interactivo
│   ├── Testimonios.tsx      # Carousel con glow effect
│   └── Footer.tsx           # Footer con CTA + contacto
├── lib/
│   ├── animations.ts        # GSAP helpers y utilidades
│   └── utils.ts             # Funciones utilitarias
├── public/                  # Assets estáticos
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.js
├── next.config.ts
└── .eslintrc.json
```

## Instalación y desarrollo

### Requisitos
- Node.js 18+
- npm o yarn

### Instalar dependencias

```bash
cd /home/mystic/hermes-os/apps/landing
npm install
```

### Desarrollo local

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador.

### Build para producción

```bash
npm run build
npm start
```

## Características implementadas

### 1. Navbar flotante
- Fixed top con blur glass effect
- Links: Logo | Productos | Casos | Docs | Contact
- Sticky en scroll con cambio de estilo
- Botón CTA "Demo Gratis"

### 2. Hero (100vh)
- Background gradient negro → púrpura
- Contenedor 3D con rotación seguida por scroll Y
- Heading: "Agentes que trabajan por ti"
- 2 CTAs: Demo Interactivo | Contacta Ventas
- Animated scroll hint
- Trust badge con avatares

### 3. Vision Statement
- Texto grande con clip-path scan animation
- Luz que se desplaza izq → der (GSAP)
- Stats secundarios: 99.9% uptime | <1ms latencia | ∞ escala

### 4. Casos de Uso
- Grid 3 columnas (Pastelería | Restaurante | Abogado)
- Cards con hover effects (flotación + sombra dinámica)
- Features expandibles al hover
- Parallax leve en scroll

### 5. 4 Pilares
- Left/Right alternado
- Sección 1: Automatización Inteligente
- Sección 2: Vende 24/7
- Sección 3: Integración Instantánea
- Sección 4: Análisis Profundo
- Fade in + slide staggered (GSAP ScrollTrigger)

### 6. Stats
- 3 números grandes con count-up (GSAP Tween)
- 500+ Empresas | 2.3M Transacciones | 99.9% Uptime
- Trust metrics debajo (ISO 27001, AES-256, etc.)

### 7. Demo Interactiva
- Chat widget con mensajes animados
- Typing indicators
- Parallax bot detrás del chat (🤖)
- Botón para solicitar demo completa

### 8. Testimonios
- Carousel horizontal (scroll smooth)
- Cards con glow effect que sigue cursor
- ⭐⭐⭐⭐⭐ ratings
- Flechas de navegación
- Mouse tracking en hover

### 9. Footer CTA
- Heading: "¿Listo para automatizar tu negocio?"
- CTAs: Solicita Demo | Ver Precios
- Contacto: Email | WhatsApp | Ubicación
- Footer links + privacy
- Gradient animado de fondo

## Paleta de colores

```css
--primary: #0F0F0F     (negro profundo)
--accent: #00D9FF      (cyan brillante)
--secondary: #6D28D9   (púrpura sutil)
--light: #F5F5F5       (gris claro)
--dark-bg: #1A1A1A     (fondo oscuro cards)
```

## GSAP Effects implementados

| Componente | Efecto | Archivo |
|-----------|--------|---------|
| Hero | 3D light source sigue scroll Y | `Hero.tsx` + `animations.ts` |
| Vision | Scan clip-path izq → der | `VisionStatement.tsx` |
| Casos | Cards floatan hover | `CasosDeUso.tsx` |
| Pilares | Fade in + slide staggered | `Pilares.tsx` |
| Stats | Count-up números | `Stats.tsx` |
| Demo | Chat typing + parallax | `DemoChat.tsx` |
| Testimonios | Glow sigue cursor | `Testimonios.tsx` |
| Footer | Gradient animado continuo | `Footer.tsx` |

## Agregar Spline Objects (3D)

Actualmente, el hero usa un placeholder. Para agregar objetos 3D reales de Spline.design:

1. **Exporta desde Spline.design**
   - Ve a [spline.design](https://spline.design)
   - Diseña tu objeto 3D (robot, logo, etc.)
   - Export → Next.js component

2. **Instala Spline viewer**
   ```bash
   npm install @spline/react-spline
   ```

3. **Reemplaza el placeholder en Hero.tsx**
   ```tsx
   import Spline from '@spline/react-spline'

   export default function Hero() {
     return (
       <Spline
         scene="https://prod.spline.design/XXXXX/scene.splinecode"
         style={{ width: '100%', height: '100%' }}
       />
     )
   }
   ```

4. **Para Pilares.tsx**, repite el proceso para cada icono 3D.

## Responsive design

Todos los componentes usan Tailwind breakpoints:
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

Mobile first: se ve bien en iPhone, tablet y desktop.

## Performance

- Next.js Image Optimization (si agregas imágenes)
- GSAP ScrollTrigger con lazy loading
- Framer Motion usa GPU acceleration
- CSS variables para colores dinámicos

## TypeScript

Strict mode habilitado. Todos los componentes usan `'use client'` (Client Components) para Framer Motion.

## Deployment

### Vercel (recomendado)

```bash
vercel deploy
```

### Docker

```bash
docker build -t sonora-landing .
docker run -p 3000:3000 sonora-landing
```

### Manual (VPS)

```bash
npm run build
npm start
```

## Variables de ambiente

No requiere variables de ambiente para desarrollo. Para producción:

```
NEXT_PUBLIC_API_URL=https://api.sonoradigital.com
```

## Troubleshooting

### GSAP ScrollTrigger no funciona

Asegúrate de que `gsap.registerPlugin(ScrollTrigger)` se ejecuta en `lib/animations.ts`.

### Scroll effects se ven lentos

Verifica que los `duration` en GSAP no sean muy altos. Usa `ease: 'none'` para animaciones de scroll.

### Framer Motion animations laggy

Habilita GPU acceleration:
```tsx
style={{ transform: 'translateZ(0)' }}
```

## Próximos pasos

- [ ] Integrar base de datos para formularios
- [ ] Agregar reCAPTCHA en CTA buttons
- [ ] Configurar Spline 3D objects reales
- [ ] Implementar multi-idioma (en/es)
- [ ] Analytics (Vercel Analytics / Mixpanel)
- [ ] A/B testing en CTAs

## Licencia

© 2026 Sonora Digital Corp. Todos los derechos reservados.

## Contacto

- Email: contacto@sonoradigital.com
- WhatsApp: +52 (555) 123-4567
- Website: https://sonoradigital.com
