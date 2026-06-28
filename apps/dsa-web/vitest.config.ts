import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const getBase = () => {
  if (process.env.VITE_BASE_URL) return process.env.VITE_BASE_URL
  if (process.env.NODE_ENV === 'development') return '/'
  return '/daily_stock_analysis/'
}

export default defineConfig({
  plugins: [react()],
  base: getBase(),
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
