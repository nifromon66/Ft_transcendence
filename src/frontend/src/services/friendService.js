import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'

/**
 * @typedef {Object} GenericResponse
 * @property {boolean} success - Indicates if the operation was successful.
 * @property {string} [message] - Success or error message from the server.
 */

/**
 * @typedef {Object} FriendUser
 * @property {number} id - The user's unique ID.
 * @property {string} username - The user's username.
 * @property {string|null} [avatar_url] - The full URL to the user's avatar.
 * @property {boolean} [is_online] - Indicates if the user is currently online.
 * @property {'none'|'accepted|'pending_sent|'pending_received'} [friendship_status] - Current relationship status
 */

/**
 * Sends a friend request to a specific user.
 * @param {number|string} targetUserId - The ID of the user to send a request to.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function sendFriendRequest(targetUserId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'envoyer la demande d'ami : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible d'envoyer la demande d'ami : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/${encodeURIComponent(targetUserId)}`, {
            method: 'POST',
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
        throw new Error(data.error || "Impossible d'envoyer la demande d'ami.")
    }

    return data
}

/**
 * Accepts a received friend request from a specific user.
 * @param {number|string} senderId - The ID of the user who sent the request.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function acceptFriendRequest(senderId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'accepter la demande d'ami : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible d'accepter la demande d'ami : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/${encodeURIComponent(senderId)}/accept`, {
            method: 'PATCH',
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

    if (response.status === 404) {
        throw new Error("Demande d'ami ou utilisateur introuvable.")
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
        throw new Error(data.error || "Impossible d'accepter la demande d'ami.")
    }

    return data
}

/**
 * Cancels a sent friend request.
 * @param {number|string} targetUserId - The ID of the target user.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function cancelFriendRequest(targetUserId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'annuler la demande d'ami : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible d'annuler la demande d'ami : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/${encodeURIComponent(targetUserId)}/cancel`, {
            method: 'DELETE',
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

    if (response.status === 404) {
        throw new Error("Demande d'ami ou utilisateur introuvable.")
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
        throw new Error(data.error || "Impossible d'annuler la demande d'ami.")
    }

    return data
}

/**
 * Denies a received friend request.
 * @param {number|string} senderId - The ID of the user who sent the request.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function denyFriendRequest(senderId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de refuser la demande d'ami : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de refuser la demande d'ami : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/${encodeURIComponent(senderId)}/deny`, {
            method: 'DELETE',
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

    if (response.status === 404) {
        throw new Error("Demande d'ami ou utilisateur introuvable.")
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
        throw new Error(data.error || "Impossible de refuser la demande d'ami.")
    }

    return data
}

/**
 * Removes a friend.
 * @param {number|string} friendId - The ID of the friend to remove.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function removeFriend(friendId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer cet ami : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de supprimer cet ami : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/${encodeURIComponent(friendId)}`, {
            method: 'DELETE',
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

    if (response.status === 404) {
        throw new Error("Ami ou utilisateur introuvable.")
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
        throw new Error(data.error || "Impossible de supprimer cet ami.")
    }

    return data
}

/**
 * Fetches the user's friend list.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<FriendUser[]>} The list of friends.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchFriends(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer la liste de vos amis : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer la liste de vos amis : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends`, {
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
        throw new Error(data.error || "Impossible de récupérer la liste des amis de cet utilisateur.")
    }

    return data.friends || []
}

/**
 * Fetches the authenticated user's received friend requests.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<FriendUser[]>} The list of received friend requests.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchReceivedRequests(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer les demandes d'amis reçues : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer les demandes d'amis reçues : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/received`, {
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
        throw new Error(data.error || "Impossible de récupérer les demandes d'amis reçues.")
    }

    return data.received_requests || []
}

/**
 * Fetches the authenticated user's sent friend requests.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<FriendUser[]>} The list of sent friends requests.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchSentRequests(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer les demandes d'amis envoyées : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer les demandes d'amis envoyées : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/requests/sent`, {
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
        throw new Error(data.error || "Impossible de récupérer les demandes d'amis envoyées.")
    }

    return data.sent_requests || []
}

/**
 * Fetches user suggestions for discovery (users who are not yet friends).
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<FriendUser[]>} The list of suggested users.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchDiscoverUsers(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de charger les suggestions d'amis : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de charger les suggestions d'amis : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/discover`, {
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
        throw new Error(data.error || "Impossible de récupérer les suggestions d'amis.")
    }

    return data.users || []
}

/**
 * Searches for users by username.
 * @param {string} query - The search query string.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<FriendUser[]>} The list of users matching the search.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function searchUsers(query, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'effectuer la recherche : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible d'effectuer la recherche : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/friends/search?q=${encodeURIComponent(query)}`, {
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
        throw new Error(data.error || "Impossible de rechercher des utilisateurs.")
    }

    return data.users || []
}