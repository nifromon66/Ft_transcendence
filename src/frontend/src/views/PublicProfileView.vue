<script setup>
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chatState'
import { ref, onMounted, onUnmounted } from 'vue'
import XpBar from '@/components/XpBar.vue'
import AvatarFrame from '@/components/AvatarFrame.vue'
import LevelRewards from '@/components/LevelRewards.vue'
import { useAuthStore } from '@/stores/authState'
import { fetchPublicProfile, updateAvatarFrame } from '@/services/userService'
import { fetchAvatarBlob } from '@/services/userService'

import {
    sendFriendRequest,
    acceptFriendRequest,
    cancelFriendRequest,
    denyFriendRequest,
    removeFriend
} from '@/services/friendService'
import { socket } from '@/services/socketService'

const router = useRouter()
const chatStore = useChatStore()

const props = defineProps({
    id: {
        type: [String, Number],
        required: true
    }
})

const authStore = useAuthStore()

const isLoading = ref(true)
const isActionLoading = ref(false)
const errorMessage = ref('')
const profile = ref(null)
const avatarImageSrc = ref(null)
const isRewardSaving = ref(false)
const rewardError = ref('')

const selectAvatarFrame = async (frame) => {
    if (isRewardSaving.value || profile.value?.friendship_status !== 'self') return
    isRewardSaving.value = true
    rewardError.value = ''
    try {
        const data = await updateAvatarFrame(frame, authStore.token)
        profile.value.avatar_frame = data.avatar_frame
        profile.value.level_rewards = data.level_rewards
        profile.value.xp_progress = data.xp_progress
        if (authStore.user) {
            authStore.user.avatar_frame = data.avatar_frame
            localStorage.setItem('user', JSON.stringify(authStore.user))
        }
    } catch (error) {
        if (error.message === 'SESSION_EXPIRED') {
            authStore.clearAuth()
            errorMessage.value = 'Votre session a expiré. Veuillez vous reconnecter.'
        } else {
            rewardError.value = error.message
        }
    } finally {
        isRewardSaving.value = false
    }
}

const handleUserStatusChange = (data) => {
    if (profile.value && data.user_id == props.id) {
        profile.value.is_online = data.is_online
    }
}

const handleFriendshipUpdated = (data) => {
    if (profile.value && data.user_id == props.id) {
        profile.value.friendship_status = data.status
    }
}

const handleProfileUpdated = (data) => {
    if (profile.value && data.user_id == props.id) {
        profile.value.username = data.new_username
    }
}

const handleFriendAction = async (apiFunction, newStatus) => {
    if (isActionLoading.value) {
        return
    }

    isActionLoading.value = true
    try {
        await apiFunction(props.id, authStore.token)
        profile.value.friendship_status = newStatus
    } catch (err) {
        if (err.message === "SESSION_EXPIRED") {
            await authStore.logout()
            errorMessage.value = "Votre session a expiré. Veuillez vous reconnecter."
        } else {
            alert(err.message)
        }
    } finally {
        isActionLoading.value = false
    }
}

const addFriend = () => handleFriendAction(sendFriendRequest, 'pending_sent')
const acceptRequest = () => handleFriendAction(acceptFriendRequest, 'accepted')
const cancelRequest = () => handleFriendAction(cancelFriendRequest, 'none')
const denyRequest = () => handleFriendAction(denyFriendRequest, 'none')

const removeCurrentFriend = (username) => {
    if (confirm(`Êtes-vous sûr de vouloir retirer ${username} de vos amis ?`)) {
        handleFriendAction(removeFriend, 'none')
    }
}

const goToChatWithFriend = async () => {
    if (profile.value) {
        await chatStore.setActiveContact(profile.value)
        router.push('/chat')
    }
}

onMounted(async () => {
    try {
        const token = authStore.token

        if (!navigator.onLine) {
            errorMessage.value = "Vous êtes hors ligne. Impossible de charger les données du profil."
            return
        }

        if (!token) {
            errorMessage.value = "Vous devez être connecté pour consulter ce profil."
            return
        }

        profile.value = await fetchPublicProfile(props.id, token)

        if (profile.value?.avatar_url) {
            const blob = await fetchAvatarBlob(profile.value.avatar_url, token)
            avatarImageSrc.value = URL.createObjectURL(blob)
        }
    } catch (err) {
        if (err.message === "SESSION_EXPIRED") {
            await authStore.logout()
            errorMessage.value = "Votre session a expiré. Veuillez vous reconnecter."
        } else {
            errorMessage.value = err.message || "Impossible de charger le profil."
        }
    } finally {
        isLoading.value = false
    }

    if (socket) {
        socket.on('user_status_changed', handleUserStatusChange)
        socket.on('friendship_updated', handleFriendshipUpdated)
        socket.on('user_profile_updated', handleProfileUpdated)
    }
})

onUnmounted(() => {
    if (avatarImageSrc.value) {
        URL.revokeObjectURL(avatarImageSrc.value)
    }

    if (socket) {
        socket.off('user_status_changed', handleUserStatusChange)
        socket.off('friendship_updated', handleFriendshipUpdated)
        socket.off('user_profile_updated', handleProfileUpdated)
    }
})
</script>

<template>
    <main class="flex-1 px-6 py-8">

        <div class="mx-auto mt-10 max-w-2xl rounded-xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 border-b pb-4 text-2xl font-bold text-gray-800">
                Profil Public
            </h1>

            <div v-if="isLoading" class="text-gray-500">Chargement des informations...</div>

            <div v-else-if="errorMessage" class="text-red-500 font-medium p-4 bg-red-50 rounded-lg">
                {{ errorMessage }}
            </div>

            <div v-else-if="profile"
                class="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">

                <div class="flex w-48 shrink-0 flex-col items-center space-y-4">
                    <div class="relative">
                        <AvatarFrame :frame="profile.avatar_frame" />
                        <div
                            class="relative flex h-32 w-32 shrink-0 items-center justify-center overflow-hidden rounded-full border-4 border-primary-light bg-gray-200 text-4xl font-bold text-gray-500 shadow-md">
                            <img v-if="avatarImageSrc" :src="avatarImageSrc" :alt="`Avatar de ${profile.username}`"
                                class="h-full w-full object-cover" />
                            <span v-else-if="profile.username">
                                {{ profile.username.charAt(0).toUpperCase() }}
                            </span>
                            <span v-else>?</span>
                        </div>

                        <span
                            class="absolute bottom-2 right-2 z-10 w-6 h-6 rounded-full border-4 border-white shadow-sm"
                            :class="profile.is_online ? 'bg-green-500' : 'bg-gray-400'"
                            :title="profile.is_online ? 'En ligne' : 'Hors ligne'">
                        </span>
                    </div>

                    <XpBar v-if="profile.xp_progress" :progress="profile.xp_progress" />
                </div>

                <div class="flex-1 w-full">
                    <div class="flex flex-col space-y-4">
                        <div>
                            <span class="text-sm font-semibold text-gray-400">Nom d'utilisateur</span>
                            <p class="text-sm font-bold text-gray-800">{{ profile.username }}</p>
                        </div>
                        <div>
                            <span class="text-sm font-semibold text-gray-400">Statut de connexion</span>
                            <p class="text-lg font-medium"
                                :class="profile.is_online ? 'text-green-600' : 'text-gray-500'">
                                {{ profile.is_online ? 'En ligne' : 'Hors ligne' }}
                            </p>
                        </div>
                    </div>

                    <div class="mt-8 pt-6 border-t border-gray-100 flex flex-wrap gap-3">

                        <div v-if="profile.friendship_status === 'self'" class="text-sm text-gray-500 italic">
                            Voici votre profil public.
                        </div>

                        <template v-else-if="profile.friendship_status === 'accepted'">
                            <button @click="goToChatWithFriend"
                                class="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded hover:bg-indigo-700 transition-colors cursor-pointer">
                                Envoyer un message à cet ami
                            </button>
                            <button @click="removeCurrentFriend(profile.username)" :disabled="isActionLoading"
                                class="px-4 py-2 bg-red-50 text-red-600 text-sm font-semibold rounded border border-red-200 hover:bg-red-100 transition-colors disabled:opacity-50 cursor-pointer">
                                Supprimer cet ami
                            </button>
                        </template>

                        <template v-else-if="profile.friendship_status === 'pending_sent'">
                            <button
                                class="px-4 py-2 bg-gray-100 text-gray-600 text-sm font-semibold rounded border border-gray-200 cursor-not-allowed"
                                disabled>
                                Demande d'ami envoyée
                            </button>
                            <button @click="cancelRequest" :disabled="isActionLoading"
                                class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-semibold rounded border border-gray-200 hover:bg-gray-200 transition-colors disabled:opacity-50 cursor-pointer">
                                Annuler la demande d'ami
                            </button>
                        </template>

                        <template v-else-if="profile.friendship_status === 'pending_received'">
                            <button @click="acceptRequest" :disabled="isActionLoading"
                                class="px-4 py-2 bg-green-500 text-white text-sm font-semibold rounded hover:bg-green-600 transition-colors disabled:opacity-50 cursor-pointer">
                                Accepter la demande d'ami
                            </button>
                            <button @click="denyRequest" :disabled="isActionLoading"
                                class="px-4 py-2 bg-gray-100 text-gray-700 text-sm font-semibold rounded border border-gray-200 hover:bg-gray-200 transition-colors disabled:opacity-50 cursor-pointer">
                                Refuser la demande d'ami
                            </button>
                        </template>

                        <template v-else>
                            <button @click="addFriend" :disabled="isActionLoading"
                                class="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded hover:bg-indigo-700 transition-colors disabled:opacity-50 cursor-pointer">
                                Ajouter cet ami
                            </button>
                        </template>

                    </div>
                </div>

            </div>

            <div v-else class="text-red-500">
                Impossible de charger le profil.
            </div>
        </div>

        <LevelRewards v-if="profile && !isLoading && !errorMessage" :rewards="profile.level_rewards || []"
            :selected="profile.avatar_frame" :editable="profile.friendship_status === 'self'" :saving="isRewardSaving"
            :error="rewardError" @select="selectAvatarFrame" />


    </main>
</template>
