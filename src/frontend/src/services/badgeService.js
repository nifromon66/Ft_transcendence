export async function fetchBadges() {
    const response = await fetch('/api/badges', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })

    if (!response.ok) {
        throw new Error('Impossible de charger les badges.')
    }

    return await response.json()
}

export async function claimBadgeApi(badgeId) {
    const response = await fetch('/api/getbadge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ badge_id: badgeId }),
    })

    if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || 'Erreur lors de la réclamation du badge.')
    }
}