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
  <div>
    <h1>Bienvenue</h1>
    <button @click="goToLogin">Se connecter</button>
    <button @click="goToRegister">S'inscrire</button>
  </div>
</template>
