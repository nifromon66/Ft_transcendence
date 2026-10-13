import { ref, watch, onMounted, onBeforeUnmount, unref } from 'vue'
import { useAuthStore } from '@/stores/authState.js'
import * as userService from '@/services/userService.js'

/**
 * @typedef {import('@/services/friendService').FriendUser} FriendUser
 * @typedef {import('@/stores/authState').User} AuthUser
 */

/**
 * @typedef {FriendUser | AuthUser | null} AvatarOwner
 */

/**
 * @typedef {Object} useAvatarReturn
 * @property {import('vue').Ref<string | null>} avatarImageSrc - Local blob URL for the avatar.
 * @property {import('vue').Ref<string>} errorMessage - Reactive error message.
 * @property {() => Promise<void>} reloadAvatar - Function to force a manual reload.
 */

/**
 * Composable to securely load and manage a user's avatar image via Blob.
 * @param {import('vue').Ref<AvatarOwner> | AvatarOwner} userRef - The user object or a ref to the user object.
 * @returns {useAvatarReturn}
 */
export function useAvatar(userRef) {
    const authStore = useAuthStore()

    const avatarImageSrc = ref(null)
    const errorMessage = ref('')

    const cleanupAvatarUrl = () => {
        if (avatarImageSrc.value) {
            URL.revokeObjectURL(avatarImageSrc.value)
            avatarImageSrc.value = null
        }
    }

    const loadAvatar = async () => {
        const user = unref(userRef)
        if (!user || !user.avatar_url) {
            cleanupAvatarUrl()
            return
        }

        try {
            const token = authStore.token

            if (!token) {
                errorMessage.value = "Utilisateur non authentifié"
                cleanupAvatarUrl()
                return
            }

            const blob = await userService.fetchAvatarBlob(user.avatar_url, token)

            cleanupAvatarUrl()

            avatarImageSrc.value = URL.createObjectURL(blob)
            errorMessage.value = ''

        } catch (error) {
            errorMessage.value = error.message
            cleanupAvatarUrl()
        }
    }

    onMounted(loadAvatar)

    watch(() => unref(userRef)?.avatar_url, loadAvatar)

    onBeforeUnmount(cleanupAvatarUrl)

    return {
        avatarImageSrc,
        errorMessage,
        reloadAvatar: loadAvatar
    }
}