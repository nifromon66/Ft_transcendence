<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="min-h-screen flex flex-col items-center justify-center gap-6 px-4">
    <h1 class="text-3xl font-bold text-blue-600">Bienvenue</h1>
    <div class="flex flex-col sm:flex-row gap-3">
      <button
        @click="goToLogin"
        class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded transition-colors"
      >
        Se connecter
      </button>
      <button
        @click="goToRegister"
        class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors"
      >
        S'inscrire
      </button>
    </div>
  </div>
</template>