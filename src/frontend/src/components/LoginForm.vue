<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/authState'
import { loginUser } from '@/services/authService'

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const errorMessage = ref('')

async function login() {
  errorMessage.value = ''

  try {
    const token = await loginUser({
      email: email.value,
      password: password.value
    })

    authStore.setAuth(token, null)
    await authStore.fetchUser()

    router.push({ name: 'welcome' })

  } catch (error) {
    errorMessage.value = error.message
  }
}

const loginWith42 = () => {
  window.location.href = 'https://localhost:8443/api/auth/login/42'
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center bg-primary-dark">

    <div class="w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">

      <h2 class="mb-6 text-center text-2xl font-bold text-black">
        Connexion
      </h2>

      <form @submit.prevent="login" class="flex flex-col gap-0.5">

        <input v-model="email" type="email" id="email" autocomplete="email" placeholder="Email"
          class="w-full rounded border p-2 bg-white font-semibold text-black" />

        <input v-model="password" type="password" id="password" placeholder="Mot de passe"
          class="w-full rounded border p-2 bg-white font-semibold text-black" />

        <button type="submit" class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700">
          Se connecter
        </button>

      </form>

      <div class="my-4 flex items-center justify-center">
        <div class="w-full border-t border-gray-300"></div>
        <span class="px-2 text-sm text-gray-500 uppercase">ou</span>
        <div class="w-full border-t border-gray-300"></div>
      </div>

      <button @click="loginWith42"
        class="w-full rounded bg-neutral-900 p-2 text-white hover:bg-black font-semibold transition-colors flex items-center justify-center gap-2">
        <span>Se connecter avec 42</span>
      </button>

      <p class="mt-4 h-6 text-center text-red-600">
        {{ errorMessage }}
      </p>

    </div>

  </div>
</template>