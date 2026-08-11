export async function registerUser(userData) {
    const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    const data = await response.json()
    if (!response.ok) {
        throw new Error(data.error || "Erreur lors de l'isncription")
    }

    return data
}