/**
 * @typedef {Object} Badge
 * @property {number|string} id
 * @property {string} name
 * @property {string} description
 * @property {boolean} eligible
 * @property {boolean} owned
 */

/**
 * Fetches the user's badges.
 * @returns {Promise<Badge[]}
 */
export async function fetchBadges() {
    const response = await fetch('/api/badges', {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    })

    if (!response.ok) {
        throw new Error('Impossible de charger les badges.')
    }

    return await response.json()
}

/**
 * Claims a specific badge.
 * @param {number|string} badgeId
 * @returns {Promise<void>}
 */
export async function claimBadgeApi(badgeId) {
    const response = await fetch('/api/getbadge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ badge_id: badgeId }),
    })
    //   .then(async response => {
    //     console.log("status:", response.status);
    //     console.log("body:", await response.text());
    // });

    if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || 'Erreur lors de la réclamation du badge.')
    }
}