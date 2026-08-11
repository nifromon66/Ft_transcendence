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
    if (!response.ok) {
        throw new Error(data.error || "Erreur lors de l'inscription")
    }

    return data
}