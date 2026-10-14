import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'
import { uploadFileToServer } from '@/services/uploadService.js'

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

    return data.user || data
}

export async function updateAvatarFrame(frame, token) {
    if (!navigator.onLine) throw new Error("Vous êtes hors ligne.")
    if (!token) throw new Error("SESSION_EXPIRED")
    const baseUrl = import.meta.env.VITE_API_URL || ''
    return data.user
}

export async function uploadAvatar(token, file, onProgress) {
    const data = await uploadFileToServer(token, file, '/api/users/me/avatar', "l'image", onProgress)
    return data
}

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
