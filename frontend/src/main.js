import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import vant from 'vant'
import '@vant/touch-emulator' // 桌面端触摸模拟

import 'vant/lib/index.css'

const app = createApp(App)
app.use(router)
app.use(vant)
app.mount('#app')