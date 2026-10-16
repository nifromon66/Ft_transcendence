export async function fetchBadges() {
    const response = await fetch('/api/gamification/badges', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })

    const data = await response.json()

    if (!response.ok || data.success === false) {
        throw new Error(data.error || 'Impossible de charger les badges.')
    }

    return data.badges || data
}

export async function claimBadgeApi(badgeId) {
    const response = await fetch('/api/gamification/award', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ badge_id: badgeId }),
    })

    const data = await response.json()

    if (!response.ok || data.success === false) {
        throw new Error(data.error || 'Erreur lors de la réclamation du badge.')
    }

    return data
}
