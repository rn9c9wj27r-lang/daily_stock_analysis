import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 根据环境动态设置 base 路径，完美兼容本地开发与 GitHub Pages 部署
const getBase = () => {
  if (process.env.VITE_BASE_URL) {
    return process.env.VITE_BASE_URL
  }
  if (process.env.NODE_ENV === 'development') {
    return '/'
  }
  return '/daily_stock_analysis/'
}

export default defineConfig({
  plugins: [react()],
  base: getBase(),  // ✅ 核心改动：彻底解决 /assets/... 404 资源找不到的陷阱
  build: {
    outDir: 'dist', // 保持打到当前目录的 dist，再由 actions 搬运
  }
})
