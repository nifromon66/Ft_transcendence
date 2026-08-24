<script setup>
    import { ref, onMounted, computed } from 'vue'
    import { useAuthStore } from '@/authState'
    import { useAvatar } from '@/composables/useAvatar'

    const authStore = useAuthStore()
    const errorMessage = ref('')
    const loading = ref(true)

    const currentUser = computed(() => authStore.user)
    const { avatarImageSrc, errorMessage: avatarError } = useAvatar(currentUser)

    const fetchProfile = async () => {
        loading.value = true
        errorMessage.value = ''

        try {
            if (!authStore.user && authStore.token) {
                await authStore.fetchUser()
            }

            if (!authStore.user) {
                errorMessage.value = "Impossible de récupérer le profil utilisateur."
            }
        } catch (err) {
            errorMessage.value = err.message || "Erreur lors du chargement des données."
        } finally {
            loading.value = false
        }
    }

    onMounted(() => {
        fetchProfile()
    })
</script>

<template>
    <main class="flex-1 px-6 py-8">
        <div class="mx-auto mt-10 max-w-2xl rounded-xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 border-b pb-4 text-2xl font-bold text-gray-800">Profil Utilisateur</h1>
            
            <div v-if="loading" class="text-gray-500">Chargement des informations...</div>

            <div v-else-if="authStore.user" class="flex items-center space-x-8">
                
                <div
                    class="relative flex h-32 w-32 shrink-0 items-center justify-center overflow-hidden
                        rounded-full border-4 border-primary-light bg-gray-200 text-4xl font-bold text-gray-500 shadow-md"
                >
                    <img
                        v-if="avatarImageSrc"
                        :src="avatarImageSrc"
                        :alt="`Avatar de ${authStore.user.username}`"
                        class="h-full w-full object-cover"
                    />
                    <span v-else-if="authStore.user.username">
                        {{ authStore.user.username.charAt(0).toUpperCase() }}
                    </span>
                    <span v-else>?</span>
                </div>

                <div class="flex flex-col space-y-2">
                    <div>
                        <span class="text-sm font-semibold text-gray-400">Nom d'utilisateur</span>
                        <p class="text-xl font-bold text-gray-800">{{ authStore.user.username }}</p>
                    </div>
                    <div>
                        <span class="text-sm font-semibold text-gray-400">Email</span>
                        <p class="text-lg text-gray-600">{{ authStore.user.email }}</p>
                    </div>

                    <p v-if="avatarError" class="text-sm text-red-500">{{ avatarError }}</p>
                    <p v-if="errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>
                </div>
            </div>

            <div v-else class="text-red-500">
                {{ errorMessage || "Impossible de charger le profil." }}
            </div>
        </div>
    </main>
</template>