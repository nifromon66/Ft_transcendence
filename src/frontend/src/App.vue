<script setup>
import { ref, onMounted, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useChatStore } from './stores/chatState.js'
import { useAuthStore } from './stores/authState.js'
import { socket, connectSocket, disconnectSocket } from './services/socketService.js'

import SiteNavigation from './components/SiteNavigation.vue'
import SideMenu from './components/SideMenu.vue'
import SiteFooter from './components/SiteFooter.vue'
import OfflineBanner from './components/OfflineBanner.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()
const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}

onMounted(async () => {
  socket.on('force_logout', () => {
    authStore.clearAuth()
    router.push({ name: 'login' })
  })

  window.addEventListener('storage', (event) => {
    if (event.key === 'token' || event.key === 'user' || event.key === null) {
      const previousToken = authStore.token
      authStore.initializeAuth()
      if (authStore.token && authStore.token !== previousToken) {
        disconnectSocket()
        connectSocket(authStore.token)
        chatStore.initializeSocketListeners()
      } else if (!authStore.token) {
        disconnectSocket()
      }
    }
  })

  if (!authStore.isInitialized) {
    if (authStore.token || localStorage.getItem('has_session') === 'true') {
      try {
        await authStore.silentRefresh()
      } catch {
        // Ignore initial silent refresh error
      }
    }
    authStore.isInitialized = true
  }

  authStore.initializeAuth()

  if (authStore.token) {
    connectSocket(authStore.token)
    chatStore.initializeSocketListeners()
  }

  setInterval(async () => {
    if (authStore.token) {
      try {
        await authStore.silentRefresh()
      } catch {
        window.location.href = '/login'
      }
    }
  }, 10 * 60 * 1000)
})

watch(() => authStore.token, (newToken) => {
  if (newToken) {
    connectSocket(newToken)
    chatStore.initializeSocketListeners()
  } else {
    disconnectSocket()
  }
})

</script>

<template>
  <div class="flex min-h-screen flex-col bg-page-background">

    <OfflineBanner />

    <SiteNavigation @toggle-menu="toggleMenu" />

    <div v-if="menuOpen" class="fixed inset-0 z-40" @click="closeMenu"></div>

    <SideMenu v-if="menuOpen" @close-menu="closeMenu" />

    <RouterView />

    <SiteFooter />
  </div>
</template>
