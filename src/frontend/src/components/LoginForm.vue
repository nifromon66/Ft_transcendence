<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../authState'

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

  if (!response.ok) {
    errorMessage.value = data.error || 'Erreur de connexion'
    return
  }

  authStore.setAuth(data.access_token, data.user)
  router.push('/home')
}
</script>

<template>
  <div>
    <h2>Connexion</h2>
    <form @submit.prevent="login">
      <input v-model="email" type="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Mot de passe" />
      <button type="submit">Se connecter</button>
    </form>
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>
