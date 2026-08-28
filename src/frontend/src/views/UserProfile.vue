<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/authState'
import { fetchUserProfile } from '@/services/userService'
import { uploadAvatar } from '@/services/uploadService'
import { fetchAvatarBlob } from '@/services/avatarService'
import { validateAvatar } from '@/utils/fileValidators'
import { optimizeImage } from '@/utils/imageProcessor'

import ImageDropZone from '@/components/ImageDropZone.vue'
import ProgressBar from '@/components/ProgressBar.vue'

const authStore = useAuthStore()

const isEditingAvatar = ref(false)
const isLoading = ref(true)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMessage = ref('')
const avatarImageSrc = ref(null)
const avatarError = ref('')
const selectedFile = ref(null)
const previewImageSrc = ref(null)

onMounted(async () => {
    try {
        const token = authStore.token

        if (!token) {
            return
        }

        const userProfile = await fetchUserProfile(token)

        authStore.user = userProfile

        if (authStore.user?.avatar_url) {
            const blob = await fetchAvatarBlob(authStore.user.avatar_url, token)
            avatarImageSrc.value = URL.createObjectURL(blob)
        }
    } catch (err) {
        errorMessage.value = "Impossible de charger le profil."
    } finally {
        isLoading.value = false
    }
})

onUnmounted(() => {
    if (avatarImageSrc.value) {
        URL.revokeObjectURL(avatarImageSrc.value)
    }
})

const handleDeleteAvatar = async () => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer votre avatar ?")) {
        return
    }

    try {
        const token = authStore.token
        const response = await fetch('/api/users/avatar', {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        })

        const data = await response.json()
        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Erreur lors de la suppression de l'avatar.")
        }

        if (avatarImageSrc.value) {
            URL.revokeObjectURL(avatarImageSrc.value)
            avatarImageSrc.value = null
        }

        authStore.user.avatar_url = null
    } catch (err) {
        alert(err.message)
    }
}

const handleNewFile = (rawFile) => {
    console.log("Fichier reçu du DropZone :", rawFile)

    const { isValid, error } = validateAvatar(rawFile)
    if (!isValid) {
        alert(error)
        return
    }

    selectedFile.value = rawFile
    previewImageSrc.value = URL.createObjectURL(rawFile)
    console.log("Aperçu généré avec succès :", previewImageSrc.value)
}

const saveAvatar = async () => {
    if (!selectedFile.value) {
        return
    }

    try {
        isUploading.value = true
        uploadProgress.value = 0

        const optimizedFile = await optimizeImage(selectedFile.value)
        const token = authStore.token

        await uploadAvatar(token, optimizedFile, (progress) => {
            uploadProgress.value = progress
        })

        const userProfile = await fetchUserProfile(token)
        authStore.user = userProfile

        if (authStore.user?.avatar_url) {
            const blob = await fetchAvatarBlob(authStore.user.avatar_url, token)
            if (avatarImageSrc.value) {
                URL.revokeObjectURL(avatarImageSrc.value)
            }
            avatarImageSrc.value = URL.createObjectURL(blob)
        }

        cancelEdit()
    } catch (err) {
        alert(err.message || "Erreur lors de l'envoi de l'image.")
    } finally {
        isUploading.value = false
    }
}

const cancelEdit = () => {
    isEditingAvatar.value = false
    selectedFile.value = null
    if (previewImageSrc.value) {
        URL.revokeObjectURL(previewImageSrc.value)
        previewImageSrc.value = null
    }
}

</script>

<template>
    <main class="flex-1 px-6 py-8">
        <div class="mx-auto mt-10 max-w-2xl rounded-xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 border-b pb-4 text-2xl font-bold text-gray-800">Profil Utilisateur</h1>

            <div v-if="isLoading" class="text-gray-500">Chargement des informations...</div>

            <div v-else-if="authStore.user"
                class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">

                <div class="flex flex-col items-center space-y-4">
                    <div class="group relative flex h-32 w-32 shrink-0 cursor-pointer items-center justify-center overflow-hidden
                            rounded-full border-4 border-primary-light bg-gray-200 text-4xl font-bold text-gray-500 shadow-md transition-all hover:border-primary"
                        @click="isEditingAvatar = !isEditingAvatar" title="Modifier l'avatar">
                        <img v-if="avatarImageSrc" :src="avatarImageSrc" :alt="`Avatar de ${authStore.user.username}`"
                            class="h-full w-full object-cover" />
                        <span v-else-if="authStore.user.username">
                            {{ authStore.user.username.charAt(0).toUpperCase() }}
                        </span>
                        <span v-else>?</span>

                        <div
                            class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 transition-opacity group-hover:opacity-100">
                            <span class="text-sm font-medium text-white">Modifier</span>
                        </div>
                    </div>

                    <button v-if="avatarImageSrc" @click="handleDeleteAvatar"
                        class="text-sm font-medium text-red-500 transition-colors hover:text-red-700 hover:underline">
                        Supprimer l'avatar
                    </button>
                </div>

                <div class="flex-1 w-full">
                    <div class="flex flex-col space-y-2">
                        <div>
                            <span class="text-sm font-semibold text-gray-400">Nom d'utilisateur</span>
                            <p class="text-xl font-bold text-gray-800">{{ authStore.user.username }}</p>
                        </div>
                        <div>
                            <span class="text-sm font-semibold text-gray-400">Email</span>
                            <p class="text-lg text-gray-600">{{ authStore.user.email }}</p>
                        </div>
                    </div>

                    <div v-if="isEditingAvatar" class="animate-fade-in mb-4 p-4 border rounded-xl bg-gray-50 mt-4">
                        <h2 class="mb-2 text-lg font-semibold text-gray-700">Nouvel avatar</h2>

                        <ImageDropZone v-if="!selectedFile" @file-selected="handleNewFile" />

                        <div v-else class="flex flex-col items-center space-y-4">
                            <p class="text-sm text-gray-500">Aperçu :</p>
                            <img :src="previewImageSrc" alt="Prévisualisation"
                                class="h-32 w-32 rounded-full object-cover border-4 border-green-400 shadow-md" />

                            <div v-if="isUploading" class="w-full mt-2">
                                <ProgressBar :progress="uploadProgress" />
                                <p class="text-center text-sm text-gray-500 mt-2">Enregistrement...</p>
                            </div>

                            <div v-else class="flex space-x-3 mt-4">
                                <button @click="saveAvatar"
                                    class="px-4 py-2 bg-green-500 text-white text-sm font-semibold rounded-lg hover:bg-green-600 transition-colors">
                                    Enregistrer
                                </button>
                                <button @click="selectedFile = null"
                                    class="px-4 py-2 bg-gray-200 text-gray-700 text-sm rounded-lg hover:bg-gray-300 transition-colors">
                                    Changer d'image
                                </button>
                            </div>
                        </div>

                        <div class="mt-4 pt-3 border-t border-gray-200 flex justify-center" v-if="!isUploading">
                            <button @click="cancelEdit"
                                class="text-sm text-red-400 hover:text-red-600 hover:underline transition-colors">
                                Annuler
                            </button>
                        </div>
                    </div>
                </div>

                <p v-if="avatarError" class="text-sm text-red-500">{{ avatarError }}</p>
                <p v-if="errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>
            </div>

            <div v-else class="text-red-500">
                {{ errorMessage || "Impossible de charger le profil." }}
            </div>

        </div>
    </main>
</template>