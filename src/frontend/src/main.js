import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { registerSW } from 'virtual:pwa-register'
import { useAppStore } from '@/stores/appState.js'

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
app.use(router)

const updateSW = registerSW({
    immediate: true,

    onNeedRefresh() {
        const appStore = useAppStore(pinia)
        appStore.promptUpdate(() => updateSW(true))
    },

    onOfflineReady() {
        const appStore = useAppStore(pinia)
        appStore.setOfflineReady()
    }
})

app.mount('#app')
