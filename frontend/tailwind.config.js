/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        // MYSTIC PEARL — Blanco perla + atardecer + verde bosque + dorado
        sovereign: {
          // Fondos
          bg:        '#F8F6F1',          // blanco perla cálido
          surface:   '#FFFFFF',
          card:      'rgba(255,255,255,0.82)',
          border:    'rgba(200,168,75,0.18)',
          // Acentos
          gold:      '#C8A84B',          // dorado cálido
          'gold-dim':'#A8893A',
          'gold-glow':'rgba(200,168,75,0.20)',
          // Verde bosque
          green:     '#2D6A4F',
          'green-light': '#52B788',
          'green-pale':  '#D8F3DC',
          // Texto
          text:      '#1C1C1E',          // casi negro suave
          muted:     '#6B7280',
          subtle:    '#9CA3AF',
          // Atardecer (acentos sutiles)
          sunset:    'rgba(251,146,60,0.07)',   // naranja atardecer muy sutil
          'sunset-deep': 'rgba(239,68,68,0.05)', // rojo atardecer
          dusk:      'rgba(167,139,250,0.06)',   // violeta crepúsculo
          // Legado (mantener compatibilidad)
          user:      '#FFF9EC',
        },
      },
      fontFamily: {
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'gold-pulse': 'goldPulse 2s ease-in-out infinite',
        'fade-up': 'fadeUp 0.3s ease-out',
        'thinking': 'thinking 1.4s ease-in-out infinite',
      },
      keyframes: {
        goldPulse: {
          '0%, 100%': { opacity: '0.6', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.05)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        thinking: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
      },
      backdropBlur: { xs: '2px' },
    },
  },
  plugins: [],
}
