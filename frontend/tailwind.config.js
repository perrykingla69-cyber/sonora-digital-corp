/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#f0f4ff',
          100: '#e0e9ff',
          500: '#4f6ef7',
          600: '#3b5bf5',
          700: '#2a47e8',
          900: '#1a2db8',
        },
        // SOVEREIGN — Negro/Dorado palette
        sovereign: {
          bg:       '#0A0A0A',
          surface:  '#111111',
          card:     '#161616',
          border:   '#222222',
          gold:     '#D4AF37',
          'gold-dim': '#8B7520',
          'gold-glow': 'rgba(212,175,55,0.15)',
          text:     '#E8E8E8',
          muted:    '#666666',
          user:     '#1A1600',
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
