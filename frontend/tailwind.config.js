/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#050812',
          900: '#080d19',
          850: '#0d1424',
          800: '#121c30',
          700: '#1d2a42',
          600: '#34445f',
        },
        teal: {
          400: '#82aaff',
          500: '#4f83f1',
          600: '#3569d4',
        },
        cyan: {
          400: '#9bbcff',
          500: '#6799ff',
        },
        risk: {
          clean: '#10b981',
          low: '#3b82f6',
          medium: '#f59e0b',
          high: '#f97316',
          critical: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      }
    },
  },
  plugins: [],
}
