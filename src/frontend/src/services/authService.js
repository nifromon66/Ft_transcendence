/**
 * Authenticates a user and retrieves an access token.
 * @param {Object} credentials - The user's login credentials.
 * @param {string} credentials.email - The user's email address.
 * @param {string} credentials.password - The user's password.
 * @returns {Promise<string>} The JWT access token.
 * @throws {Error} If the server fails or authentication is unsuccessful.
 */
export async function loginUser(credentials) {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
    })

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    const data = await response.json()

    if (!data.success) {
        throw new Error(data.error || "Votre compte a été créé avec succès. Cependant, une erreur réseau a empêché l'authentification.")
    }

    return data.access_token
}