import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'

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

export async function uploadDocument(file, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'envoyer le fichier : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible d'envoyer le fichier : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''
    const formData = new FormData()
    formData.append('file', file)

    let response
    try {
        response = await fetch(`${baseUrl}/api/messages/documents`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur pour l'envoi du fichier.", { cause: error })
    }

    if (response.status === 401) {
        const authStore = useAuthStore()
        authStore.clearAuth()
        import('@/router/index.js').then(m => m.default.push({ name: 'login' }))
        throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
    }

    let data
    try {
        data = await response.json()
    } catch (error) {
        throw new Error("Erreur de communication avec le serveur lors de l'envoi du fichier.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible d'envoyer le fichier.")
    }

    return data
}

export async function deleteMessage(messageId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer le message : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de supprimer le message : vous n'êtes pas authentifié.")
    }

    const baseUrl = import.meta.env.VITE_API_URL || ''

    let response
    try {
        response = await fetch(`${baseUrl}/api/messages/${encodeURIComponent(messageId)}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Accept': 'application/json'
            }
        })
    } catch (error) {
        throw new Error("Impossible de contacter le serveur.", { cause: error })
    }

    if (response.status === 401) {
        const authStore = useAuthStore()
        authStore.clearAuth()
        router.push({ name: 'login' })
        throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
    }

    let data
    try {
        data = await response.json()
    } catch (error) {
        throw new Error("Erreur de communication avec le serveur.", { cause: error })
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de supprimer le message.")
    }

    return true
}
