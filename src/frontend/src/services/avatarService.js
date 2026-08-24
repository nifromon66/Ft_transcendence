export async function fetchAvatarBlob(avatarUrl, token) {
    const baseUrl = import.meta.env.VITE_API_URL

    const response = await fetch(`${baseUrl}${avatarUrl}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })

    if (!response.ok) {
        throw new Error("Accès refusé ou fichier introuvable")
    }

    const contentType = response.headers.get("content-type")

    if (contentType && contentType.includes("application/json")) {
        const data = await response.json()
        if (data.success === false) {
            throw new Error(data.error || "Erreur serveur")
        }
    }

    if (!contentType || !contentType.includes("image")) {
        throw new Error("Le format du fichier n'est pas une image")
    }

    return await response.blob()
}