import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vant from 'vant'
import '@vant/touch-emulator' // 桌面端触摸模拟

import 'vant/lib/index.css'

// PWA注册
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then((registration) => {
        console.log('SW registered: ', registration)
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError)
      })
  })
}

const app = createApp(App)
app.use(router)
app.use(vant)
app.mount('#app')