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
    const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    const data = await response.json()

    if (data.success === false) {
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
    const baseUrl = import.meta.env.VITE_API_URL || ''
    const response = await fetch(`${baseUrl}/api/users/me`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillew réessayer.")
    }

    const data = await response.json()

    if (data.success === false) {
        throw new Error(data.error || "Impossible de récupérer le profil utilisateur.")
    }

    return data.user || data
}