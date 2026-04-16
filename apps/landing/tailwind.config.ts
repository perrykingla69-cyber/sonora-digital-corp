import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'primary-dark': '#0F0F0F',
        'accent': '#00D9FF',
        'secondary': '#6D28D9',
        'light': '#F5F5F5',
        'dark-bg': '#1A1A1A',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Courier Prime', 'monospace'],
        display: ['Space Grotesk', 'sans-serif'],
      },
      fontSize: {
        'h1': ['64px', { lineHeight: '1.2', fontWeight: '700' }],
        'h2': ['48px', { lineHeight: '1.3', fontWeight: '700' }],
        'h3': ['36px', { lineHeight: '1.4', fontWeight: '600' }],
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, #0F0F0F 0%, #1a0a2e 50%, #16213e 100%)',
        'card-gradient': 'linear-gradient(135deg, #1A1A1A 0%, #2a1a3e 100%)',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(0, 217, 255, 0.3)',
        'glow-lg': '0 0 40px rgba(0, 217, 255, 0.4)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'gradient-shift': 'gradient-shift 8s ease infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(0, 217, 255, 0.6)' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
  plugins: [],
}

export default config
