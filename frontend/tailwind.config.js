/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mine: {
          dark: '#0f172a',
          card: '#1e293b',
          border: '#334155',
          safe: '#22c55e',
          low: '#0ea5e9',
          medium: '#eab308',
          high: '#f97316',
          critical: '#ef4444',
        }
      }
    },
  },
  plugins: [],
}
