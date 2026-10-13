<script setup>
import { ref, onMounted, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useChatStore } from './stores/chatState.js'
import SiteNavigation from './components/SiteNavigation.vue'
import SideMenu from './components/SideMenu.vue'
import SiteFooter from './components/SiteFooter.vue'
import OfflineBanner from './components/OfflineBanner.vue'
import { useAuthStore } from './stores/authState.js'

const authStore = useAuthStore()
const chatStore = useChatStore()
const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}

onMounted(() => {
  authStore.initializeAuth()
  if (authStore.token) {
    chatStore.initializeSocketListeners()
  }
})

watch(() => authStore.token, (newToken) => {
  if (newToken) {
    setTimeout(() => {
      chatStore.initializeSocketListeners()
    }, 100)
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
