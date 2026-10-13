import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'
import { uploadFileToServer } from '@/services/uploadService.js'

/**
 * @typedef {Object} GenericResponse
 * @property {boolean} success - Indicates if the operation was successful.
 * @property {string} [message] - Success or error message.
 * @property {string} [error] - Error message if applicable.
 */

/**
 * @typedef {Object} UserProfile
 * @property {number} id - The user's unique ID.
 * @property {string} username - The user's username.
 * @property {string} email - The user's email address.
 * @property {string|null} avatar_url - The full URL to the user's avatar.
 */

/**
 * @typedef {Object} PublicProfile
 * @property {number} id - The user's unique ID.
 * @property {string} username - The user's username.
 * @property {string|null} avatar_url - The full URL to the user's avatar.
 * @property {boolean} is_online - Indicates if the user is online.
 * @property {'self'|'none'|'accepted'|'pending_sent'|'pending_received'} friendship_status - The relationship status with the current user.
 */

/**
 * Updates the authenticated user's profile.
 * @param {Object} userData - The data to update.
 * @param {string} [userData.username] - The new username.
 * @param {string} [userData.email] - The new email address.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<UserProfile>} The updated user profile data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function updateMyProfile(userData, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de modifier le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de modifier le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/me`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(userData)
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de modifier le profil.")
    }

    return data.user
}

/**
 * Uploads a user avatar.
 * @param {string} token - The user's JWT access token.
 * @param {File} file - The image file.
 * @param {Function} [onProgress] - Callback function receiving the upload percentage.
 * @returns {Promise<{success: boolean, filename: string, error?: string}>} The server response data.
 */
export async function uploadAvatar(token, file, onProgress) {
    const data = await uploadFileToServer(token, file, '/api/users/me/avatar', "l'image", onProgress)
    return data
}

/**
 * Deletes the authenticated user's avatar.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<GenericResponse>} The server confirmation response.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */

export async function deleteAvatar(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer l'avatar : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de supprimer l'avatar : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/me/avatar`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de supprimer l'avatar.")
    }

    return data
}

/**
 * Deletes the authenticated user's account.
 * @param {string} password - The user's password to confirm deletion.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<string>} The success message from the server
 * @throws {Error} If the request fails, the user is unauthorized, the password is incorrect, or a network error occurs.
 */
export const deleteAccount = async (password, token) => {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer le compte : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de supprimer le compte : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/me`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ password })
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de supprimer le compte.")
    }

    return data.message
}

/**
 * Fetches the authenticated user's profile data.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<UserProfile>} The user profile data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function fetchUserProfile(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer le profil utilisateur.")
    }

    return data.user
}

/**
 * Fetches the list of all users.
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<UserProfile[]>} The list of users.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
*/
export async function fetchAllUsers(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer la liste des utilisateurs : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer la liste des utilisateurs : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer la liste des utilisateurs.")
    }

    return data.users || []
}

/**
 * Fetches the public profile of a specific user.
 * @param {number|string} userId - The ID of the user whose profile is being fetched. 
 * @param {string} token - The authenticated user's token. 
 * @returns {Promise<PublicProfile>} The public profile data.
 * @throws {Error} If the request fails, the user is unauthorized, the profile is not found, or a network error occurs.
 */
export async function fetchPublicProfile(userId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/${encodeURIComponent(userId)}/profile`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer le profil utilisateur.")
    }

    return data.profile
}

/**
 * Fetches the user's avatar image as Blob.
 * @param {string} avatarUrl - The full API route to the avatar (e.g., "/api/users/avatars/123.jpg").
 * @param {string} token - The user's JWT access token.
 * @returns {Promise<Blob>} The avatar image Blob.
 * @throws {Error} If the request fails, the user is unauthorized, the file is not an image, or a network error occurs.
 */
export async function fetchAvatarBlob(avatarUrl, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer l'avatar : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer l'avatar : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}${avatarUrl}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'image/*, application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
    }

    if (response.status === 401) {
        const authStore = useAuthStore()
        authStore.clearAuth()
        router.push({ name: 'login' })
        throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
    }

    if (response.status === 403) {
        throw new Error("Accès refusé. Compte inactif ou supprimé.")
    }

    if (response.status === 404) {
        throw new Error("Avatar introuvable.")
    }

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    const contentType = response.headers.get("content-type")

    if (contentType && contentType.includes("application/json")) {
        let data
        try {
            data = await response.json()
        } catch (error) {
            throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
        }

        if (!response.ok || data.success === false) {
            throw new Error(data.error || "Impossible de récupérer l'avatar.")
        }
    }

    if (!contentType || !contentType.includes("image")) {
        throw new Error("Le format du fichier retourné n'est pas une image.")
    }

    try {
        return await response.blob()
    } catch (error) {
        throw new Error("Impossible de lire les données de l'image.", { cause: error })
    }
}

export async function updateAvatarFrame(frame, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de modifier le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de modifier le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/users/me/avatar-frame`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ frame }),
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible d'enregistrer le cercle.")
    }

    return data
}