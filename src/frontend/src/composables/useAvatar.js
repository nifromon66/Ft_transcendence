import { ref, watch, onMounted, unref } from 'vue'
import { useAuthStore } from '@/authState'
import { fetchAvatarBlob } from '@/services/userService'

export function useAvatar(userRef) {
    const authStore = useAuthStore()

    const avatarImageSrc = ref(null)
    const errorMessage = ref('')

    const loadAvatar = async () => {
        const user = unref(userRef)
        if (!user || !user.avatar_url) {
            avatarImageSrc.value = null
            return
        }

        try {
            const token = authStore.token

            if (!token) {
                errorMessage.value = "Utilisateur non authentifié"
                avatarImageSrc.value = null
                return
            }

            const blob = await fetchAvatarBlob(user.avatar_url, token)

            avatarImageSrc.value = URL.createObjectURL(blob)
            errorMessage.value = ''

        } catch (error) {
            errorMessage.value = error.message
            avatarImageSrc.value = null
        }
    }

    onMounted(loadAvatar)
    watch(userRef, loadAvatar, { deep: true })

    return {
        avatarImageSrc,
        errorMessage,
        reloadAvatar: loadAvatar
    }
}