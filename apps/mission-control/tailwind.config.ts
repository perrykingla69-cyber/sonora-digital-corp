import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0F0F0F',
        accent: '#00D9FF',
        secondary: '#6D28D9',
        light: '#F5F5F5',
        'dark-bg': '#1A1A1A',
        'card-dark': '#141414',
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
        display: ['Space Grotesk', ...defaultTheme.fontFamily.sans],
        mono: ['Courier Prime', ...defaultTheme.fontFamily.mono],
      },
      fontSize: {
        h1: ['3.5rem', { lineHeight: '1.1', fontWeight: '700' }],
        h2: ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
        h3: ['1.875rem', { lineHeight: '1.3', fontWeight: '600' }],
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        glow: 'glow 2s ease-in-out infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
      },
      boxShadow: {
        glow: '0 0 20px rgba(0, 217, 255, 0.3)',
        'glow-lg': '0 0 40px rgba(0, 217, 255, 0.5)',
        'card': '0 4px 20px rgba(0, 0, 0, 0.3)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-gradient': 'linear-gradient(135deg, #0F0F0F 0%, #1A1A1A 100%)',
        'card-gradient': 'linear-gradient(135deg, rgba(0, 217, 255, 0.1) 0%, rgba(109, 40, 217, 0.1) 100%)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

export default config
