export async function registerUser(userData) {
    if (!navigator.onLine) {
        throw new Error("Impossible de s'inscrire : vous êtes hors ligne.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/auth/register`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(userData)
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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
        throw new Error(data.error || "Impossible de s'inscrire.")
    }

    return data.access_token
}

export async function loginUser(credentials) {
    if (!navigator.onLine) {
        throw new Error("Impossible de se connecter : vous êtes hors ligne.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/auth/login`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(credentials)
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
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

export async function refreshAccessToken() {
    if (!navigator.onLine) {
        throw new Error("Hors ligne")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''
    const response = await fetch(`${baseUrl}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Accept': 'application/json'
        }
    })

    if (!response.ok) {
        throw new Error("Session expirée")
    }

    const data = await response.json()
    if (data.success === false) {
        throw new Error(data.error || "Session expirée")
    }

    return data.access_token
}

export async function logoutUser() {
    if (!navigator.onLine) return;

    const baseUrl = import.meta.env.VITE_API_URL || ''
    try {
        await fetch(`${baseUrl}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        })
    } catch {
        // Ignore network errors during logout
    }
}
