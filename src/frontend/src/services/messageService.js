import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'

/**
 * @typedef {Object} ChatMessage
 * @property {number} id - The unique ID of the message.
 * @property {number} sender_id - The ID of the sender.
 * @property {number} receiver_id - The ID of the receiver.
 * @property {string} content - The text content of the message.
 * @property {string} [filename] - The attached filename.
 * @property {string} [file_url] - The full URL to the attached file.
 * @property {string} [created_at] - Creation date string.
 */

/**
 * Fetch the conversation history with a specific friend.
 * @param {number|string} friendId - The ID of the friend.
 * @param {string} token - The user's JWT token.
 * @returns {Promise<ChatMessage[]>} The list of messages.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchConversation(friendId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de charger la conversation : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de charger la conversation : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/messages/${encodeURIComponent(friendId)}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.")
    }

    if (response.status === 401) {
        const authStore = useAuthStore()
        authStore.clearAuth()
        router.push({ name: 'login' })
        throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
    }

    if (response.status === 403) {
        throw new Error("Cet utilisateur ne fait plus partie de vos amis.")
    }

    if (response.status === 404) {
        throw new Error("Utilisateur introuvable.")
    }

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data
    try {
        data = await response.json()
    } catch (error) {
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.")
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de charger la conversation.")
    }

    return data.messages || []
}