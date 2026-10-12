/**
 * @typedef {Object} AuthUser
 * @property {number} id - The user's unique ID.
 * @property {string} username - The user's username.
 * @property {string} email - The user's email address.
 * @property {string|null} [avatar_url] - The full URL to the user's avatar, if any.
 */


/**
 * Registers a new user on the server.
 * @param {Object} userData - The user registration data.
 * @param {string} userData.username - The chosen username.
 * @param {string} userData.email - The user's email address.
 * @param {string} userData.password - The user's password.
 * @returns {Promise<string>} The JWT access token.
 * @throws {Error} If the request fails or a network error occurs.
 */
export async function registerUser(userData) {
    if (!navigator.onLine) {
        throw new Error("Impossible de s'inscrire : vous êtes hors ligne.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(userData)
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.")
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
        throw new Error(data.error || "Impossible de s'inscrire.")
    }

    return data.access_token
}

/**
 * Authenticates a user and retrieves an access token.
 * @param {Object} credentials - The user's login credentials.
 * @param {string} credentials.email - The user's email address.
 * @param {string} credentials.password - The user's password.
 * @returns {Promise<{ token: string, user: AuthUser }>} The JWT access token.
 * @throws {Error} If the server fails, authentication is unsuccessful or a network error occurs.
 */
export async function loginUser(credentials) {
    if (!navigator.onLine) {
        throw new Error("Impossible de se connecter : vous êtes hors ligne.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(credentials)
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.")
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
        throw new Error(data.error || "Identifiants incorrects ou compte inactif.")
    }

    if (!data.access_token) {
        throw new Error(data.error || "Impossible de se connecter.")
    }

    return {
        token: data.access_token,
        user: data.user
    }
}