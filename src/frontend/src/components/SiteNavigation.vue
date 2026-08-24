  <script setup>
    import { RouterLink, useRouter } from 'vue-router'
    import { useAuthStore } from '@/authState'
    import { ref } from 'vue'
    import Burger from './Burger.vue'
    import SiteBrand from './SiteBrand.vue'
    import UserAvatar from './UserAvatar.vue'

    const emit = defineEmits(['toggle-menu'])
    const authStore = useAuthStore()
    const router = useRouter()
    const accountMenuOpen = ref(false)

    function toggleAccountMenu() {
      accountMenuOpen.value = !accountMenuOpen.value
    }

    function logout() {
      authStore.clearAuth()
      accountMenuOpen.value = false
      router.push({ name: 'welcome' })
    }
</script>

<template>
  <header class="sticky top-0 bg-primary shadow-lg">
    <nav class="flex w-full items-center justify-between px-6 py-6 text-white">
      <!-- left side -->
      <div class="flex items-center gap-3">
        <Burger
          label="Ouvrir le menu"
          @activate="emit('toggle-menu')"
        />
        <SiteBrand />
      </div>

      <!-- right side -->
      <div class="relative">
        <UserAvatar
          :user="authStore.user"
          :expanded="accountMenuOpen"
          @activate="toggleAccountMenu"
        />

        <!-- Transparency area covering remaining page space -->
        <div
          v-if="accountMenuOpen"
          class="fixed inset-0 z-40"
          @click="accountMenuOpen = false"
        ></div>
        
        <div
          v-if="accountMenuOpen"
          class="absolute right-0 top-full z-50 mt-2 w-48 rounded-lg bg-menu-background p-2 text-gray-800 shadow-md"
        >
          <template v-if="!authStore.user">
            <RouterLink
              :to="{ name: 'login' }"
              class="block rounded-full px-4 py-2 hover:bg-primary-light"
              @click="accountMenuOpen = false"
            >
              Connexion
            </RouterLink>

            <RouterLink
              :to="{ name: 'register' }"
              class="block rounded-full px-4 py-2 hover:bg-primary-light"
              @click="accountMenuOpen = false"
            >
              Inscription
            </RouterLink>
          </template>

          <template v-else>
            <RouterLink
              :to="{ name: 'profile' }"
              class="block rounded-full px-4 py-2 hover:bg-primary-light"
              @click="accountMenuOpen = false"
            >
              Mon profil
            </RouterLink>

            <button
              type="button"
              class="w-full rounded-full px-4 py-2 text-left hover:bg-primary-light"
              @click="logout"
            >
              Déconnexion
            </button>
          </template>
        </div>
      </div>
    </nav>
  </header>
</template>

