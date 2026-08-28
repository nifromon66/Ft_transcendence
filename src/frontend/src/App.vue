<script setup>
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import SiteNavigation from './components/SiteNavigation.vue'
import SideMenu from './components/SideMenu.vue'
import SiteFooter from './components/SiteFooter.vue'
import OfflineBanner from './components/OfflineBanner.vue'

const menuOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}
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
