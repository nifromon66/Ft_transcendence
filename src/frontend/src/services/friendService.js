const baseUrl = import.meta.env.VITE_API_URL || ''

/**
 * Fetches the authenticated user's friends list.
 */
export async function fetchFriends(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer vos amis : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de récupérer vos amis : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer la liste d'amis.")
    }

    return data.friends || []
}

/**
 * Fetches for users by username.
 */
export async function searchUsers(query, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'effectuer la recherche : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible d'effectuer la recherche : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/search?q=${encodeURIComponent(query)}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de la recherche d'utilisateurs.")
    }

    return data.users || []
}

/**
 * Fetches user suggestions for discovery.
 */
export async function fetchDiscoverUsers(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de charger les suggestions d'amis : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de charger les suggestions d'amis : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/discover`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Impossible de récupérer les suggestions d'amis.")
    }

    return data.users || []
}

/**
 * Fetches the authenticated user's received friend requests.
 */
export async function fetchReceivedRequests(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer les demandes d'amis reçues : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de récupérer les demandes d'amis reçues : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/requests/received`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de la récupération des demandes d'amis reçues.")
    }

    return data.received_requests || []
}

/**
 * Fetches the authenticated user's sent friend requests.
 */
export async function fetchSentRequests(token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de récupérer les demandes d'amis envoyées : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de récupérer les demandes d'amis envoyées : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/requests/sent`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de la récupération des demandes d'amis envoyées.")
    }

    return data.sent_requests || []
}

/**
 * Sends a friend request to a specific user.
 */
export async function sendFriendRequest(targetUserId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'envoyer la demande d'ami : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible d'envoyer la demande d'ami : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/request/${targetUserId}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de l'envoi de la demande d'ami.")
    }

    return data
}

/**
 * Accepts a received friend request from a specific user.
 */
export async function acceptFriendRequest(senderId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'accepter la demande d'ami : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible d'accepter la demande d'ami : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/request/${senderId}/accept`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de l'acceptation de la demande d'ami.")
    }

    return data
}

/**
 * Cancel a received friend request from a specific user.
 */
export async function cancelFriendRequest(targetUserId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible d'annuler la demande d'ami : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible d'annuler la demande d'ami : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/request/${targetUserId}/cancel`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de l'annulation de la demande d'ami.")
    }

    return data
}

/**
 * Denies a received friend request.
 */
export async function denyFriendRequest(senderId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de refuser la demande d'ami : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de refuser la demande d'ami : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/request/${senderId}/deny`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors du refus de la demande d'ami.")
    }

    return data
}

/**
 * Removes a user from the authenticated user's friends list.
 */
export async function removeFriend(friendId, token) {
    if (!navigator.onLine) {
        throw new Error("Impossible de supprimer cet ami : vous êtes hors ligne.")
    }
    if (!token) {
        throw new Error("Impossible de supprimer cet ami : vous n'êtes pas authentifié.")
    }

    const response = await fetch(`${baseUrl}/api/friends/${friendId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })

    if (response.status == 401) {
        throw new Error("SESSION_EXPIRED")
    }
    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    let data = {}
    try {
        data = await response.json()
    } catch (e) { }

    if (!response.ok || data.success === false) {
        throw new Error(data.error || "Erreur lors de la suppression de cet ami.")
    }

    return data
}
