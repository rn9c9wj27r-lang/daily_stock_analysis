import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ThemeProvider } from './components/theme/ThemeProvider'

// ⚡ 吸收强 AI 的核心拦截思想：在挂载第一步执行静态数据穿透
if (typeof window !== 'undefined' && (window as any).__INITIAL_DATA__) {
  console.log('✅ [静态穿透模式] 检测到全局行情底座数据，正在接管状态...');
  
  // 💡 最小改动核心：如果你的组件后续去 fetch 接口，我们直接在前端拦截掉原生的 fetch 请求
  const staticData = (window as any).__INITIAL_DATA__;
  const originalFetch = window.fetch;
  
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const urlStr = input.toString();
    // 拦截任何看盘相关的本地 API 请求，直接返回 Actions 刚刚算出来的离线 JSON 镜像
    if (urlStr.includes('/api/') || urlStr.includes('json')) {
      return new Response(JSON.stringify(staticData), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    return originalFetch(input, init);
  };
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </StrictMode>,
)
