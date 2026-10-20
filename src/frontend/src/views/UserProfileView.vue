<script setup>
import AvatarFrame from '@/components/AvatarFrame.vue'
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/authState'
import { fetchUserProfile, deleteAccount, updateMyProfile, deleteAvatar } from '@/services/userService'
import { uploadAvatar } from '@/services/userService'
import { fetchAvatarBlob } from '@/services/userService'
import { validateAvatar } from '@/utils/fileValidators'
import { optimizeImage } from '@/utils/imageProcessor'
import QrcodeVue from 'qrcode.vue'

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

const isEditingInfo = ref(false)
const isInfoUpdating = ref(false)
const infoSuccessMessage = ref('')
const infoErrorMessage = ref('')
const editForm = ref({
    username: '',
    email: ''
})

const recoveryCodes = ref([])
const isCopied = ref(false)

const is2FaModalOpen = ref(false)
const twoFaStep = ref(1)
const twoFaPassword = ref('')
const twoFaCode = ref('')
const qrCodeUrl = ref('')
const twoFaError = ref('')
const is2FaLoading = ref(false)

const isDisable2FaModalOpen = ref(false)
const disable2FaPassword = ref('')
const disable2FaError = ref('')
const isDisable2FaLoading = ref(false)
const disable2FaCode = ref('')

const openEditInfo = () => {
    editForm.value.username = authStore.user.username
    editForm.value.email = authStore.user.email
    isEditingInfo.value = true
    infoSuccessMessage.value = ''
    infoErrorMessage.value = ''
}

const cancelEditInfo = () => {
    isEditingInfo.value = false
}

const saveProfileInfo = async () => {
    if (isInfoUpdating.value) {
        return
    }
    isInfoUpdating.value = true
    infoSuccessMessage.value = ''
    infoErrorMessage.value = ''

    try {
        const token = authStore.token
        const updatedUser = await updateMyProfile(editForm.value, token)

        authStore.user.username = updatedUser.username
        authStore.user.email = updatedUser.email

        infoSuccessMessage.value = "Vos informations ont été mises à jour avec succès !"
        isEditingInfo.value = false

        setTimeout(() => infoSuccessMessage.value = '', 3000)
    } catch (err) {
        if (err.message === "SESSION_EXPIRED") {
            await authStore.logout()
            router.push('/login')
        } else {
            infoErrorMessage.value = err.message
        }
    } finally {
        isInfoUpdating.value = false
    }
}

const open2FaModal = () => {
    is2FaModalOpen.value = true
    twoFaStep.value = 1
    twoFaPassword.value = ''
    twoFaCode.value = ''
    twoFaError.value = ''
}

const close2FaModal = () => {
    is2FaModalOpen.value = false
    twoFaStep.value = 1
    twoFaPassword.value = ''
    twoFaCode.value = ''
    twoFaError.value = ''
    recoveryCodes.value = []
}

const submit2FaPassword = async () => {
    if (!twoFaPassword.value) {
        twoFaError.value = "Veuillez entrer votre mot de passe."
        return
    }

    try {
        is2FaLoading.value = true
        twoFaError.value = ''

        const response = await fetch('/api/auth/2fa/setup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.token}`
            },
            body: JSON.stringify({ password: twoFaPassword.value })
        })

        let data = {}

        try {
            data = await response.json()
        } catch (parseError) {
            throw new Error(`Erreur serveur (${response.status}). Veuillez réessayer.`, { cause: parseError })
        }

        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Mot de passe incorrect.")
        }

        qrCodeUrl.value = data.qr_uri
        twoFaStep.value = 2
    } catch (err) {
        twoFaError.value = err.message || "Impossible de joindre le serveur."
    } finally {
        is2FaLoading.value = false
    }
}

const confirm2FaCode = async () => {
    if (!twoFaCode.value || twoFaCode.value.length !== 6) {
        twoFaError.value = "Le code doit contenir 6 chiffres."
        return
    }

    try {
        is2FaLoading.value = true
        twoFaError.value = ''

        const response = await fetch('/api/auth/2fa/verify-setup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.token}`
            },
            body: JSON.stringify({ code: twoFaCode.value })
        })

        let data = {}
        try {
            data = await response.json()
        } catch (parseError) {
            throw new Error(`Erreur serveur (${response.status}). Veuillez réessayer.`, { cause: parseError })
        }

        if (!response.ok || data.success === false) {
            if (response.status === 401) {
                throw new Error("Le code est incorrect ou a expiré.")
            }
            throw new Error(data.error || "Code invalide.")
        }

        authStore.user.is_2fa_enabled = true
        recoveryCodes.value = data.recovery_codes
        twoFaStep.value = 3
    } catch (err) {
        if (err.name === 'TypeError') {
            twoFaError.value = "Erreur réseau : Impossible de joindre le serveur."
        } else {
            twoFaError.value = err.message
        }
    } finally {
        is2FaLoading.value = false
    }
}

const copyRecoveryCodes = async () => {
    const textToCopy = recoveryCodes.value.join('\n')
    try {
        await navigator.clipboard.writeText(textToCopy)
        isCopied.value = true
        setTimeout(() => { isCopied.value = false }, 2000)
    } catch {
        // Ignore clipboard write failures
    }
}

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
    if (!authStore.user?.oauth_provider && !deletePassword.value) {
        deleteError.value = "Veuillez renseigner votre mot de passe."
        return
    }
    try {
        const token = authStore.token

        await deleteAccount(deletePassword.value, token)

        closeDeleteModal()
        await authStore.logout()
        router.push('/')

        alert("Votre compte a été supprimé avec succès.")
    } catch (err) {
        if (err.message === "SESSION_EXPIRED") {
            closeDeleteModal()
            await authStore.logout()
            router.push('/login')
        } else {
            deleteError.value = err.message || "Impossible de supprimer le compte."
        }
    }
}

const openDisable2FaModal = () => {
    disable2FaPassword.value = ''
    disable2FaCode.value = ''
    disable2FaError.value = ''
    isDisable2FaModalOpen.value = true
}

const closeDisable2FaModal = () => {
    isDisable2FaModalOpen.value = false
}

const confirmDisable2Fa = async () => {
    if (!disable2FaPassword.value) {
        disable2FaError.value = "Le mot de passe est requis."
        return
    }

    if (!disable2FaCode.value || disable2FaCode.value.length !== 6) {
        disable2FaError.value = "Veuillez entrer le code à 6 chiffres."
        return
    }

    isDisable2FaLoading.value = true
    disable2FaError.value = ''

    try {
        const response = await fetch('/api/auth/2fa/disable', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.token}`
            },
            body: JSON.stringify({
                password: disable2FaPassword.value,
                code: disable2FaCode.value
            })
        })

        let data = {}
        try {
            data = await response.json()
        } catch {
            // Ignore response parsing errors on disable 2FA
        }

        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Erreur lors de la désactivation.")
        }

        authStore.user.is_2fa_enabled = false
        closeDisable2FaModal()
    } catch (err) {
        disable2FaError.value = err.message
    } finally {
        isDisable2FaLoading.value = false
    }
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
            await authStore.logout()
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

        await deleteAvatar(token)

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
    const { isValid, error } = validateAvatar(rawFile)
    if (!isValid) {
        alert(error)
        return
    }

    selectedFile.value = rawFile
    previewImageSrc.value = URL.createObjectURL(rawFile)
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
            <h1 class="mb-6 border-b pb-4 text-2xl font-bold text-gray-800">Informations du compte</h1>

            <div v-if="isLoading" class="text-gray-500">Chargement des informations...</div>

            <div v-else-if="errorMessage" class="text-red-500 font-medium p-4 bg-red-50 rounded-lg">
                {{ errorMessage }}
            </div>

            <div v-else-if="authStore.user"
                class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">

                <div class="flex flex-col items-center space-y-4">

                    <div class="relative">
                        <AvatarFrame :frame="authStore.user.avatar_frame" />
                        <div class="group relative flex h-32 w-32 shrink-0 cursor-pointer items-center justify-center overflow-hidden
                                rounded-full border-4 border-primary-light bg-gray-200 text-4xl font-bold text-gray-500 shadow-md transition-all hover:border-primary"
                            @click="isEditingAvatar = !isEditingAvatar" title="Modifier l'avatar">
                            <img v-if="avatarImageSrc" :src="avatarImageSrc"
                                :alt="`Avatar de ${authStore.user.username}`" class="h-full w-full object-cover" />
                            <span v-else-if="authStore.user.username">
                                {{ authStore.user.username.charAt(0).toUpperCase() }}
                            </span>
                            <span v-else>?</span>

                            <div
                                class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 transition-opacity group-hover:opacity-100">
                                <span class="text-sm font-medium text-white">Modifier</span>
                            </div>
                        </div>
                    </div>

                    <button v-if="avatarImageSrc" @click="handleDeleteAvatar"
                        class="text-sm font-medium text-red-500 transition-colors hover:text-red-700 hover:underline">
                        Supprimer l'avatar
                    </button>
                </div>

                <div class="flex-1 w-full">

                    <div v-if="infoSuccessMessage"
                        class="mb-4 p-3 bg-green-50 text-green-700 rounded-lg text-sm font-medium border border-green-200">
                        {{ infoSuccessMessage }}
                    </div>
                    <div v-if="infoErrorMessage"
                        class="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm font-medium border border-red-200">
                        {{ infoErrorMessage }}
                    </div>

                    <div class="flex flex-col space-y-2">

                        <div v-if="!isEditingInfo" class="flex justify-between items-start">
                            <div class="space-y-3">
                                <div>
                                    <span class="text-sm font-semibold text-gray-400">Nom d'utilisateur</span>
                                    <p class="text-xl font-bold text-gray-800">{{ authStore.user.username }}</p>
                                </div>
                                <div>
                                    <span class="text-sm font-semibold text-gray-400">Email</span>
                                    <p class="text-lg text-gray-600">{{ authStore.user.email }}</p>
                                </div>
                            </div>
                            <button @click="openEditInfo"
                                class="text-sm font-medium text-blue-500 hover:text-blue-700 hover:underline transition-colors">
                                Modifier mes infos
                            </button>
                        </div>

                        <div v-else class="bg-gray-50 p-5 rounded-xl border border-gray-200 shadow-sm animate-fade-in">
                            <h2 class="mb-4 text-lg font-semibold text-gray-700">Modifier mes informations</h2>
                            <form @submit.prevent="saveProfileInfo" class="space-y-4">
                                <div>
                                    <label for="edit-username" class="block text-sm font-medium text-gray-700 mb-1">Pseudo</label>
                                    <input id="edit-username" name="username" autocomplete="username" v-model="editForm.username" type="text" required
                                        class="w-full rounded border p-2 bg-white text-black focus:outline-none focus:ring-2 focus:ring-blue-500">
                                </div>
                                <div>
                                    <label for="edit-email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                                    <input id="edit-email" name="email" autocomplete="email" v-model="editForm.email" type="email" required
                                        class="w-full rounded border p-2 bg-white text-black focus:outline-none focus:ring-2 focus:ring-blue-500">
                                </div>

                                <div class="flex space-x-3 pt-2">
                                    <button type="submit" :disabled="isInfoUpdating"
                                        class="px-4 py-2 bg-blue-500 text-white text-sm font-semibold rounded-lg hover:bg-blue-600 transition-colors">
                                        {{ isInfoUpdating ? 'Enregistrement des modifications...' : 'Enregistrer' }}
                                    </button>
                                    <button type="button" @click="cancelEditInfo" :disabled="isInfoUpdating" class="px-4 py-2
                                        bg-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-300
                                        transition-colors">
                                        Annuler
                                    </button>
                                </div>
                            </form>
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

                    <div v-if="avatarError || (errorMessage && authStore.user)" class="mt-4">
                        <p v-if="avatarError" class="text-sm text-red-500">{{ avatarError }}</p>
                        <p v-if="errorMessage && authStore.user" class="text-sm text-red-500">{{ errorMessage }}</p>
                    </div>

                    <div v-if="authStore.user && !authStore.user.oauth_provider"
                        class="mt-8 pt-6 border-t border-gray-200">
                        <h2 class="mb-4 text-lg font-semibold text-gray-800">Sécurité</h2>

                        <div
                            class="bg-gray-50 p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row md:items-center justify-betwwen gap-4">
                            <div>
                                <p class="font-bold text-gray-700 text-base">Authentification à double facteur (2FA)</p>
                                <p class="text-sm text-gray-500 mt-1">
                                    <template v-if="authStore.user.is_2fa_enabled">
                                        Le 2FA est activé. Votre compte bénéficie d'une sécurité renforcée.
                                    </template>
                                    <template v-else>
                                        Ajoutez une couche de sécurité supplémentaire en activant l'authentification à
                                        double facteurs (2FA).
                                    </template>
                                </p>
                            </div>
                            <button v-if="!authStore.user.is_2fa_enabled" @click="open2FaModal"
                                class="px-4 py-2 bg-gray-800 text-white text-sm font-semibold rounded-lg hover:bg-gray-900 transition-colors whitespace-nowrap">
                                Activer le 2FA
                            </button>
                            <div v-else class="flex items-center space-x-3">
                                <span
                                    class="px-3 py-1.5 bg-green-100 text-green-800 text-sm font-semibold rounded border border-green-200">
                                    ✓ Activé
                                </span>
                                <button @click="openDisable2FaModal"
                                    class="text-sm font-medium text-red-500 hover:text-red-700 hover:underline transition-colors whitespace-nowrap">
                                    Désactiver
                                </button>
                            </div>
                        </div>
                    </div>


                    <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                        <button @click="openDeleteModal"
                            class="text-red-600 hover:text-red-800 font-medium text-sm underline transition-colors">
                            Supprimer mon compte
                        </button>
                    </div>
                </div>
            </div>
            <div v-else class="text-red-500">
                Impossible de charger le profil.
            </div>
        </div>

        <div v-if="isDeleteModalOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
            <form @submit.prevent="confirmDelete" class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 class="text-xl font-bold text-red-600 mb-4">Supprimer mon compte</h3>

                <p class="text-gray-700 mb-4 text-sm">
                    Attention, cette action est définitive. Vos données personnelles et votre avatar seront effacés.
                    Vos
                    contributions seront conservées, mais anonymisées.
                </p>

                <div v-if="!authStore.user?.oauth_provider" class="mb-6">
                    <input type="text" name="username" autocomplete="username" :value="authStore.user?.username || ''" class="hidden" aria-hidden="true" tabindex="-1" readonly>
                    <label for="delete-password" class="block text-sm font-medium text-gray-700 mb-1">
                        Entrez votre mot de passe pour supprimer votre compte :
                    </label>
                    <input type="password" id="delete-password" name="password" v-model="deletePassword" placeholder="Mot de passe"
                        autocomplete="current-password"
                        class="w-full rounded border p-2 bg-gray-50 text-black focus:outline-none focus:ring-2 focus:ring-red-500">
                    <p v-if="deleteError" class="text-red-500 text-xs mt-1">{{ deleteError }}</p>
                </div>
                <p v-else-if="deleteError" class="text-red-500 text-xs mb-4">{{ deleteError }}</p>

                <div class="flex justify-end space-x-3">
                    <button type="button" @click="closeDeleteModal"
                        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 font-medium transition-colors">
                        Annuler
                    </button>
                    <button type="submit"
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium transition-colors">
                        ⚠️ Supprimer mon compte
                    </button>
                </div>
            </form>
        </div>

        <div v-if="is2FaModalOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">

                <form v-if="twoFaStep === 1" @submit.prevent="submit2FaPassword">
                    <h3 class="text-xl font-bold text-gray-800 mb-4">Activer le 2FA</h3>
                    <p class="text-gray-600 mb-4 text-sm">Veuillez confirmer votre mot de passe pour activer le 2FA.
                    </p>
                    <input type="text" name="username" autocomplete="username" :value="authStore.user?.username || ''" class="hidden" aria-hidden="true" tabindex="-1" readonly>
                    <input id="enable-2fa-password" name="password" autocomplete="current-password" type="password" v-model="twoFaPassword" placeholder="Votre mot de passe"
                        class="w-full rounded border p-2 bg-white text-black focus:outline-none focus:ring-2 focus:ring-gray-800 mb-2">
                    <p v-if="twoFaError" class="text-red-500 text-xs mb-4">{{ twoFaError }}</p>

                    <div class="flex justify-end space-x-3 mt-4">
                        <button type="button" @click="close2FaModal"
                            class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors">Annuler</button>
                        <button type="submit" :disabled="is2FaLoading"
                            class="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900 transition-colors">
                            {{ is2FaLoading ? 'Vérification...' : 'Continuer' }}
                        </button>
                    </div>
                </form>

                <form v-else-if="twoFaStep === 2" @submit.prevent="confirm2FaCode">
                    <h3 class="text-xl font-bold text-gray-800 mb-4 text-center">Scanner le QR Code</h3>
                    <p class="text-gray-600 mb-4 text-sm text-center">Utilisez Google Authenticator pour scanner ce
                        QR
                        Code :
                    </p>

                    <div class="flex justify-center mb-6">
                        <div class="p-2 bg-white border rounded-xl shadow-sm">
                            <qrcode-vue :value="qrCodeUrl" :size="200" level="H" />
                        </div>
                    </div>

                    <input id="enable-2fa-code" name="twofa-code" autocomplete="one-time-code" type="text" v-model="twoFaCode" placeholder="Code à 6 chiffres" maxlength="6"
                        class="w-full text-center tracking-widest text-xl font-mono rounded border p-3 bg-white text-black focus:outline-none focus:ring-2 focus:ring-gray-800 mb-2">
                    <p v-if="twoFaError" class="text-red-500 text-xs mb-4 text-center">{{ twoFaError }}</p>

                    <div class="flex justify-end space-x-3 mt-4">
                        <button type="button" @click="close2FaModal"
                            class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors">Annuler</button>
                        <button type="submit" :disabled="is2FaLoading"
                            class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors font-medium">
                            {{ is2FaLoading ? 'Validation...' : 'Valider et Activer le 2FA' }}
                        </button>
                    </div>
                </form>

                <div v-else-if="twoFaStep === 3" class="animate-fade-in">
                    <h3 class="text-xl font-bold text-gray-800 mb-2 text-center">Codes de récupération</h3>

                    <div class="bg-yellow-50 border border-yellow-200 p-3 rounded-lg mb-5">
                        <p class="text-yellow-800 text-sm text-center font-medium">
                            Sauvegardez ces codes en lieu sûr.
                            Ils ne seront affichés qu'une seule fois et vous permettront de récupérer votre compte
                            si
                            vous
                            perdez l'accès à Google Authenticator.
                        </p>
                    </div>

                    <div class="grid grid-cols-2 gap-3 mb-5">
                        <div v-for="code in recoveryCodes" :key="code"
                            class="bg-gray-50 border border-gray-200 p-2 rounded text-center font-mono tracking-wider text-gray-800 text-sm font-semibold">
                            {{ code }}
                        </div>
                    </div>

                    <button @click="copyRecoveryCodes" type="button"
                        class="w-full flex justify-center items-center gap-2 px-4 py-2.5 bg-gray-100 border border-gray-300 text-gray-800 rounded-lg hover:bg-gray-200 transition-colors mb-4 font-semibold">
                        <span v-if="!isCopied">Copier les codes</span>
                        <span v-else class="text-green-600">Codes copiés !</span>
                    </button>

                    <div class="w-full border-t border-gray-200 pt-4 mt-2">
                        <button @click="close2FaModal"
                            class="w-full px-4 py-2.5 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors font-semibold">
                            J'ai bien sauvegardé ces codes
                        </button>
                    </div>
                </div>
            </div>

        </div>

        <div v-if="isDisable2FaModalOpen"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
            <form @submit.prevent="confirmDisable2Fa" class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">

                <h3 class="text-xl font-bold text-gray-800 mb-4">Désactiver le 2FA</h3>
                <p class="text-gray-600 mb-4 text-sm">
                    En désactivant le 2FA, votre compte sera moins sécurisé. Veuillez confirmer votre identité pour
                    continuer.
                </p>

                <input type="text" name="username" autocomplete="username" :value="authStore.user?.username || ''" class="hidden" aria-hidden="true" tabindex="-1" readonly />
                <input id="disable-2fa-password" name="password" autocomplete="current-password" type="password" v-model="disable2FaPassword" placeholder="Votre mot de passe"
                    class="w-full rounded border p-2 bg-white text-black focus:outline-none focus:ring-2 focus:ring-gray-800 mb-4" />

                <input id="disable-2fa-code" name="twofa-code" autocomplete="one-time-code" type="text" v-model="disable2FaCode" placeholder="Code à 6 chiffres" maxlength="6"
                    class="w-full text-center tracking-widest text-xl font-mono rounded border p-3 bg-white text-black focus:outline-none focus:ring-2 focus:ring-gray-800 mb-2" />

                <p v-if="disable2FaError" class="text-red-500 text-xs mb-4 text-center">{{ disable2FaError }}</p>

                <div class="flex justify-end space-x-3 mt-4">
                    <button type="button" @click="closeDisable2FaModal"
                        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors">
                        Annuler
                    </button>
                    <button type="submit" :disabled="isDisable2FaLoading"
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors font-medium disabled:opacity-50">
                        {{ isDisable2FaLoading ? 'Désactivation...' : 'Désactiver' }}
                    </button>
                </div>
            </form>
        </div>

    </main>
</template>
