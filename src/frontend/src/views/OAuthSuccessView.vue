<script setup>
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authState'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
    const token = route.query.token

    if (token) {
        try {
            authStore.setAuth(token, null)

            await authStore.fetchUser()

            router.push({ name: 'welcome' })
        } catch (error) {
            router.push({ name: 'login' })
        }
    } else {
        router.push({ name: 'login' })
    }
})
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-primary-dark">
        <div class="rounded-lg bg-menu-background p-8 shadow-lg text-center">
            <h2 class="text-xl font-bold text-black mb-2">Authentification 42 en cours...</h2>
            <p class="text-gray-600">Connexion réussie, redirection vers l'application...</p>
        </div>
    </div>
</template>