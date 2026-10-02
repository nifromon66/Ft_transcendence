<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/authState'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const is2FaStep = ref(false)
const tempToken = ref('')
const twoFaCode = ref('')

async function login() {
  errorMessage.value = ''
  isLoading.value = true

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value
      })
    })

    let data = {}
    try {
      data = await response.json()
    } catch (e) {
      throw new Error("Erreur de communication avec le serveur.")
    }

    if (!response.ok) {
      throw new Error(data.error || "Email ou mot de passe incorrect.")
    }

    if (data.status === '2FA_REQUIRED') {
      tempToken.value = data.temp_token
      is2FaStep.value = true
      return
    }

    authStore.setAuth(data.access_token, null)
    await authStore.fetchUser()
    router.push({ name: 'welcome' })

  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

async function confirm2FaLogin() {
  if (!twoFaCode.value || twoFaCode.value.length !== 6) {
    errorMessage.value = "Le code doit contenir 6 chiffres."
    return
  }

  errorMessage.value = ''
  isLoading.value = true

  try {
    const response = await fetch('/api/auth/2fa/verify-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${tempToken.value}`
      },
      body: JSON.stringify({ code: twoFaCode.value })
    })

    let data = {}
    try {
      data = await response.json()
    } catch (e) {
      throw new Error("Erreur serveur.")
    }

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error("Le code est incorrect ou a expiré.")
      }
      throw new Error(data.error || "Code invalide.")
    }

    authStore.setAuth(data.access_token, null)
    await authStore.fetchUser()
    router.push({ name: 'welcome' })
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

const cancel2Fa = () => {
  is2FaStep.value = false
  twoFaCode.value = ''
  tempToken.value = ''
  password.value = ''
  errorMessage.value = ''
}

const loginWith42 = () => {
  window.location.href = 'https://localhost:8443/api/auth/login/42'
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center bg-primary-dark">

    <div class="w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">

      <div v-if="!is2FaStep">
        <h2 class="mb-6 text-center text-2xl font-bold text-black">
          Connexion
        </h2>

        <form @submit.prevent="login" class="flex flex-col gap-0.5">

          <input v-model="email" type="email" id="email" autocomplete="email" placeholder="Email" required
            class="w-full rounded border p-2 bg-white font-semibold text-black" />

          <input v-model="password" type="password" id="password" placeholder="Mot de passe" required
            class="w-full rounded border p-2 bg-white font-semibold text-black" />

          <button type="submit" :disabled="isLoading"
            class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-50 mt-2">
            {{ isLoading ? 'Connexion...' : 'Se connecter' }}
          </button>

        </form>

        <div class="my-4 flex items-center justify-center">
          <div class="w-full border-t border-gray-300"></div>
          <span class="px-2 text-sm text-gray-500 uppercase">ou</span>
          <div class="w-full border-t border-gray-300"></div>
        </div>

        <button @click="loginWith42" :disabled="isLoading"
          class="w-full rounded bg-neutral-900 p-2 text-white hover:bg-black font-semibold transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
          <span>Se connecter avec 42</span>
        </button>
      </div>

      <div v-else>
        <h2 class="mb-6 text-center text-2xl font-bold text-black">
          Authentification à double facteurs (2FA)
        </h2>
        <p class="mb-4 text-center text-sm font-medium text-gray-700">
          Entrez le code à 6 chiffres de votre application.
        </p>

        <form @submit.prevent="confirm2FaLogin" class="flex flex-col gap-2">
          <input v-model="twoFaCode" type="text" inputmode="numeric" maxlength="6" placeholder="000000" required
            class="w-full rounded border p-3 text-center font-mono text-2xl tracking-widest bg-white font-semibold text-black focus:border-blue-500 focus:outline-none" />

          <button type="submit" :disabled="isLoading"
            class="mt-2 w-full rounded bg-green-600 p-2 text-white hover:bg-green-700 font-semibold disabled:opacity-50">
            {{ isLoading ? 'Vérification...' : 'Valider' }}
          </button>

          <button type="button" @click="cancel2Fa" :disabled="isLoading"
            class="w-full rounded bg-gray-200 p-2 text-gray-800 hover:bg-gray-300 font-semibold disabled:opacity-50">
            Annuler
          </button>
        </form>
      </div>

      <p class="mt-4 h-6 text-center text-red-600">
        {{ errorMessage }}
      </p>

    </div>

  </div>
</template>