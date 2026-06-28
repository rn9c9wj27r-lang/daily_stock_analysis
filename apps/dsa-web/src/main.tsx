import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from './components/theme/ThemeProvider'

/**
 * 静态数据穿透：在 React 挂载前，将 window.__INITIAL_DATA__
 * 作为离线数据源拦截组件发出的本地 API GET 请求。
 *
 * 设计原则（对比原版的改进）：
 *  1. 仅拦截 GET 请求 → 放行 POST/PUT/DELETE
 *  2. 仅匹配 /api/<endpoint> 本地路径 → 不误伤外部 JSON / CDN 资源
 *  3. 按端点名映射到 staticData[endpoint] 对应切片 → 多端点不再返回同一份数据
 *  4. originalFetch.bind(window) → 避免 this 上下文丢失
 */
if (typeof window !== 'undefined' && (window as any).__INITIAL_DATA__) {
  const staticData = (window as any).__INITIAL_DATA__ as Record<string, unknown>
  console.log('[静态穿透] 检测到注入数据，启用离线 API 拦截')

  const originalFetch = window.fetch.bind(window)

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const method = (init?.method ?? 'GET').toUpperCase()
    if (method !== 'GET') {
      return originalFetch(input, init)
    }

    const urlStr =
      typeof input === 'string'
        ? input
        : input instanceof URL
          ? input.href
          : input.url

    // 仅拦截本地 /api/ 路径，提取端点名做数据切片映射
    const match = urlStr.match(/\/api\/([^/?#]+)/)
    if (match) {
      const endpoint = match[1]
      // 若 staticData 有对应 key 则取切片，否则回退到整包
      const payload = staticData[endpoint] ?? staticData
      return new Response(JSON.stringify(payload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    }

    return originalFetch(input, init)
  }
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </StrictMode>,
)
