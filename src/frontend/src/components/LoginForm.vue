<script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/authState'

  const router = useRouter()
  const authStore = useAuthStore()
  const email = ref('')
  const password = ref('')
  const errorMessage = ref('')

  async function login() {
    errorMessage.value = ''

    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value })
    })

    const data = await response.json()

    if (!response.ok || !data.access_token) {
      errorMessage.value = data.error || 'Email ou mot de passe incorrect'
      return
    }

    authStore.setAuth(data.access_token, data.user)
    router.push({ name: 'welcome' })
  }
</script>

<template>
  <div class="flex flex-1 items-center justify-center bg-primary-dark">

    <div class="w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">

      <h2 class="mb-6 text-center text-2xl font-bold text-black">
        Connexion
      </h2>

      <form @submit.prevent="login" class="flex flex-col gap-0.5">

        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full rounded border p-2 bg-white font-semibold text-black"
        />

        <input
          v-model="password"
          type="password"
          placeholder="Mot de passe"
          class="w-full rounded border p-2 bg-white font-semibold text-black"
        />

        <button
          type="submit"
          class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700"
        >
          Se connecter
        </button>

      </form>

      <p class="mt-4 h-6 text-center text-red-600">
        {{ errorMessage }}
      </p>

    </div>

  </div>
</template>