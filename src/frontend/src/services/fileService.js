export async function fetchDocumentBlob(fileUrl, token) {
    const baseUrl = import.meta.env.VITE_API_URL || ''
    const url = fileUrl.startsWith('http') ? fileUrl : `${baseUrl}${fileUrl}`

    const response = await fetch(url, {
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

    return await response.blob()
}