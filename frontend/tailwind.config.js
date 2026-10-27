/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border, 214.3 31.8% 91.4%))',
        input: 'hsl(var(--input, 214.3 31.8% 91.4%))',
        ring: 'hsl(var(--ring, 221.2 83.2% 53.3%))',
        background: 'hsl(var(--background, 0 0% 100%))',
        foreground: 'hsl(var(--foreground, 222.2 84% 4.9%))',
        primary: {
          DEFAULT: '#2563eb',
          foreground: '#ffffff',
          hover: '#1d4ed8',
        },
        category: {
          supplier: {
            DEFAULT: '#ef4444',
            light: '#fee2e2',
            text: '#b91c1c',
            border: '#fca5a5',
            glow: 'rgba(239, 68, 68, 0.25)',
          },
          part: {
            DEFAULT: '#f59e0b',
            light: '#fef3c7',
            text: '#b45309',
            border: '#fcd34d',
            glow: 'rgba(245, 158, 11, 0.25)',
          },
          product: {
            DEFAULT: '#0d9488',
            light: '#ccfbf1',
            text: '#0f766e',
            border: '#99f6e4',
            glow: 'rgba(13, 148, 136, 0.25)',
          },
          order: {
            DEFAULT: '#2563eb',
            light: '#dbeafe',
            text: '#1d4ed8',
            border: '#bfdbfe',
            glow: 'rgba(37, 99, 235, 0.25)',
          },
          muted: {
            DEFAULT: '#94a3b8',
            light: '#f1f5f9',
            text: '#64748b',
            border: '#e2e8f0',
          },
        },
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'sans-serif',
        ],
      },
      boxShadow: {
        card: '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        glow: '0 0 15px -3px rgba(37, 99, 235, 0.3)',
      },
    },
  },
  plugins: [],
}
