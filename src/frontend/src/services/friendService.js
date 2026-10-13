import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'

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