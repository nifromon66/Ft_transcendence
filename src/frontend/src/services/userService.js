/**
 * Registers a new user on the server.
 * @param {Object} userData - The user registration data.
 * @param {string} userData.username - The chosen username.
 * @param {string} userData.email - The user's email address.
 * @param {string} userData.password - The user's password.
 * @returns {Promise<Object>} The server response data upon successful registration.
 * @throws {Error} If the server fails or registration is unsuccessful.
 */
export async function registerUser(userData) {
    let response;
    try {
        response = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        })
    } catch (e) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connection internet.")
    }

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) {

    }

    if (!response.ok) {
        throw new Error(data.error || "Erreur lors de l'inscription")
    }

    if (data.error || data.success === false) {
        throw new Error(data.error || "Erreur lors de l'inscription")
    }

    return data
}

/**
 * Fetches the authenticated user's profile data.
 * @param {string} token - The user's authentication token.
 * @returns {Promise<Object>} The user profile data.
 * @throws {Error} If the request fails or unauthorized.
 */
export async function fetchUserProfile(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || '';

    const response = await fetch(`${baseUrl}/api/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status === 401) {
        throw new Error("SESSION_EXPIRED")
    }

    if (response.status === 404) {
        throw new Error("Utilisateur introuvable.")
    }

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) {

    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer le profil utilisateur.")
    }

    return data.user || data
}

export const deleteAccount = async (password, token) => {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer le compte : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de supprimer le compte : vous n'êtes pas authentifié.")
    }

    const response = await fetch('/api/users/me/delete', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ password })
    })

    let data = {}
    try {
        data = await response.json()
    } catch (e) {

    }

    if (response.status === 401) {
        throw new Error("SESSION_EXPIRED")
    }

    if (response.status === 404) {
        throw new Error("Utilisateur introuvable.")
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de la suppression du compte.")
    }

    return data
}

export async function fetchPublicProfile(userId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer le profil : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de récupérer le profil : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || '';

    const response = await fetch(`${baseUrl}/api/users/${userId}/profile`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status === 401) {
        throw new Error("SESSION_EXPIRED")
    }

    if (response.status === 404) {
        throw new Error("Utilisateur introuvable.")
    }

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) {

    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer le profil utilisateur.")
    }

    return data.profile
}