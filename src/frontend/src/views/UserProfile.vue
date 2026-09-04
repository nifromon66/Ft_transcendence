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
import router from '@/router'

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

const isDeleteModalOpen = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

const openDeleteModal = () => {
    isDeleteModalOpen.value = true
    deleteError.value = ''
}

const closeDeleteModal = () => {
    isDeleteModalOpen.value = false
    deletePassword.value = ''
    deleteError.value = ''
}

const confirmDelete = async () => {
    if (!deletePassword.value) {
        deleteError.value = "Veuillez renseigner votre mot de passe."
        return
    }
    console.log("Mot de passe prêt à être envoyé :", deletePassword.value)
}

onMounted(async () => {
    try {
        const token = authStore.token

        if (!token) {
            return
        }

        if (!navigator.onLine) {
            errorMessage.value = "Vous êtes hors ligne. Impossible de charger les données du profil."
            return
        }

        const userProfile = await fetchUserProfile(token)
        authStore.user = userProfile

        if (authStore.user?.avatar_url) {
            const blob = await fetchAvatarBlob(authStore.user.avatar_url, token)
            avatarImageSrc.value = URL.createObjectURL(blob)
        }
    } catch (err) {
        if (err.message === "SESSION_EXPIRED") {
            authStore.logout()
            router.push('/login')
        } else {
            errorMessage.value = err.message || "Impossible de charger le profil."
        }
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
    if (!navigator.onLine) {
        alert("Impossible de supprimer l'avatar en mode hors ligne.")
        return
    }
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

    if (!navigator.onLine) {
        alert("Impossible d'enregistrer l'avatar en mode hors ligne.")
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

            <div v-else-if="errorMessage" class="text-red-500 font-medium p-4 bg-red-50 rounded-lg">
                {{ errorMessage }}
            </div>

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

                <div v-if="avatarError || (errorMessage && authStore.user)" class="mt-4">
                    <p v-if="avatarError" class="text-sm text-red-500">{{ avatarError }}</p>
                    <p v-if="errorMessage && authStore.user" class="text-sm text-red-500">{{ errorMessage }}</p>
                </div>

                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button @click="openDeleteModal"
                        class="text-red-600 hover:text-red-800 font-medium text-sm underline transition-colors">
                        Supprimer mon compte
                    </button>
                </div>
            </div>

            <div v-else class="text-red-500">
                Impossible de charger le profil.
            </div>
        </div>

        <div v-if="isDeleteModalOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 class="text-xl font-bold text-red-600 mb-4">Supprimer mon compte</h3>

                <p class="text-gray-700 mb-4 text-sm">
                    Attention, cette action est définitive. Vos données personnelles et votre avatar seront effacés. Vos
                    contributions seront conservées, mais anonymisées.
                </p>

                <div class="mb-6">
                    <label for="delete-password" class="block text-sm font-medium text-gray-700 mb-1">
                        Entrez votre mot de passe pour supprimer votre compte :
                    </label>
                    <input type="password" id="delete-password" v-model="deletePassword" placeholder="Mot de passe"
                        autocomplete="current-password"
                        class="w-full rounded border p-2 bg-gray-50 text-black focus:outline-none focus:ring-2 focus:ring-red-500"
                        @keyup.enter="confirmDelete">
                    <p v-if="deleteError" class="text-red-500 text-xs mt-1">{{ deleteError }}</p>
                </div>

                <div class="flex justify-end space-x-3">
                    <button @click="closeDeleteModal"
                        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 font-medium transition-colors">
                        Annuler
                    </button>
                    <button @click="confirmDelete"
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium transition-colors">
                        ⚠️ Supprimer mon compte
                    </button>
                </div>
            </div>
        </div>
    </main>
</template>