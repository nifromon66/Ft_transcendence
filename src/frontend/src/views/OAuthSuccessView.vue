<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authState'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isPendingConsent = ref(false)
const pendingToken = ref('')
const acceptTerms = ref(false)
const acceptPrivacy = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

onMounted(async () => {
    const token = route.query.token
    const pending = route.query.pending_token

    if (token) {
        try {
            authStore.setAuth(token, null)
            await authStore.fetchUser()
            router.push({ name: 'welcome' })
        } catch {
            router.push({ name: 'login' })
        }
        return
    }

    if (pending) {
        pendingToken.value = String(pending)
        isPendingConsent.value = true
        return
    }

    router.push({ name: 'login' })
})

async function completeOAuth() {
    errorMessage.value = ''

    if (!acceptTerms.value || !acceptPrivacy.value) {
        errorMessage.value = "Veuillez accepter les CGU et la politique de confidentialité."
        return
    }

    isSubmitting.value = true
    try {
        const baseUrl = import.meta.env.VITE_API_URL || ''
        const response = await fetch(baseUrl + '/api/auth/oauth/complete', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                pending_token: pendingToken.value,
                accept_terms: acceptTerms.value,
                accept_privacy: acceptPrivacy.value
            })
        })

        const data = await response.json()
        if (!response.ok || data.success === false || !data.access_token) {
            throw new Error(data.error || "Impossible de finaliser l'inscription.")
        }

        authStore.setAuth(data.access_token, null)
        await authStore.fetchUser()
        router.push({ name: 'welcome' })
    } catch (error) {
        errorMessage.value = error.message || "Une erreur est survenue."
    } finally {
        isSubmitting.value = false
    }
}

function cancelOAuth() {
    router.push({ name: 'login' })
}
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-primary-dark px-4">
        <div v-if="!isPendingConsent" class="rounded-lg bg-menu-background p-8 shadow-lg text-center">
            <h2 class="text-xl font-bold text-black mb-2">Authentification 42 en cours...</h2>
            <p class="text-gray-600">Connexion réussie, redirection vers l'application...</p>
        </div>

        <div v-else class="w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">
            <h2 class="mb-3 text-center text-2xl font-bold text-black">
                Finaliser l'inscription 42
            </h2>
            <p class="mb-5 text-center text-sm text-gray-700">
                Bienvenue ! Pour créer votre compte, veuillez accepter nos conditions :
            </p>

            <form @submit.prevent="completeOAuth" class="flex flex-col gap-3">
                <div class="mb-2 flex flex-col gap-2 text-sm text-gray-800">
                    <label for="oauth-accept-terms" class="flex items-start gap-2 cursor-pointer">
                        <input
                            id="oauth-accept-terms"
                            v-model="acceptTerms"
                            type="checkbox"
                            required
                            class="mt-1 h-4 w-4 shrink-0 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>
                            J'ai lu et j'accepte les
                            <RouterLink :to="{ name: 'terms' }" class="text-blue-600 underline hover:text-blue-800">
                                Conditions générales d'utilisation
                            </RouterLink>
                        </span>
                    </label>

                    <label for="oauth-accept-privacy" class="flex items-start gap-2 cursor-pointer">
                        <input
                            id="oauth-accept-privacy"
                            v-model="acceptPrivacy"
                            type="checkbox"
                            required
                            class="mt-1 h-4 w-4 shrink-0 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span>
                            J'ai pris connaissance de la
                            <RouterLink :to="{ name: 'privacy' }" class="text-blue-600 underline hover:text-blue-800">
                                Politique de confidentialité
                            </RouterLink>
                        </span>
                    </label>
                </div>

                <button
                    type="submit"
                    :disabled="isSubmitting || !acceptTerms || !acceptPrivacy"
                    class="w-full rounded bg-blue-600 p-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {{ isSubmitting ? 'Validation...' : 'Créer mon compte' }}
                </button>

                <button
                    type="button"
                    @click="cancelOAuth"
                    :disabled="isSubmitting"
                    class="w-full rounded bg-gray-200 p-2 font-semibold text-gray-800 hover:bg-gray-300 disabled:opacity-50"
                >
                    Annuler
                </button>
            </form>

            <p v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">
                {{ errorMessage }}
            </p>
        </div>
    </div>
</template>
