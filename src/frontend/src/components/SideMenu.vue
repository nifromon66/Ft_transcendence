<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/authState'
import Burger from './Burger.vue'
import SiteBrand from './SiteBrand.vue'

const emit = defineEmits(['close-menu'])
const authStore = useAuthStore()
</script>

<template>
  <aside class="fixed left-0 top-0 z-50 h-screen w-60 bg-menu-background p-6 shadow-2xl">
    <div class="mb-8 flex items-center gap-3">
      <Burger label="Fermer le menu" @activate="emit('close-menu')" />
      <SiteBrand @select="emit('close-menu')" />
    </div>

    <nav class="flex flex-col gap-3 text-center">
      <RouterLink :to="{ name: 'welcome' }" class="rounded-full px-4 py-2 text-gray-800 hover:bg-primary-light"
        @click="emit('close-menu')">
        Accueil
      </RouterLink>

      <RouterLink v-if="authStore.user" :to="{ name: 'friends' }"
        class="rounded-full px-4 py-2 text-gray-800 hover:bg-primary-light" @click="emit('close-menu')">
        Mes amis
      </RouterLink>

      <RouterLink
        v-if="authStore.user"
        :to="{ name: 'postRecipe' }"
        class="rounded-full px-4 py-2 text-gray-800 hover:bg-primary-light"
        @click="emit('close-menu')"
      >
        Poster une recette
      </RouterLink>
      
      <RouterLink
        :to="{ name: 'about' }"
        class="rounded-full px-4 py-2 text-gray-800 hover:bg-primary-light"
        @click="emit('close-menu')"
      >
        A propos
      </RouterLink>
    </nav>
  </aside>
</template>
