<script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'

  const router = useRouter()
  const username = ref('')
  const email = ref('')
  const password = ref('')
  const errorMessage = ref('')

  async function register() {
    errorMessage.value = ''

  const response = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: username.value,
      email: email.value,
      password: password.value
    })
  })

  const data = await response.json()

  if (!response.ok) {
    errorMessage.value = data.error || 'Erreur lors de l\'inscription'
    return
  }

  router.push('/login')
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center bg-primary-dark">
    <div class="-translate-y-32 w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">
      <h2 class="mb-6 text-center text-2xl font-bold text-black">Inscription</h2>
      <form @submit.prevent="register" class="flex flex-col gap-0.5">
        <div>
          <input 
            v-model="username" 
            placeholder="Nom d'utilisateur" 
            class="w-full rounded border p-2 bg-white font-semibold text-black"
          />
        </div>
        <div>
          <input 
            v-model="email"
            type="email" 
            placeholder="Email" 
            class="w-full rounded border p-2 bg-white font-semibold text-black"
          />
        </div>
        <div>
          <input 
            v-model="password" 
            type="password" 
            placeholder="Mot de passe" 
            class="w-full rounded border p-2 bg-white font-semibold text-black"
          />
        </div>
        <button type="submit"
          class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700"
        >
          S'inscrire
        </button>
      </form>
      <p class="mt-4 h-6 text-center text-red-600">
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>
