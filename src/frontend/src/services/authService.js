export async function loginUser(credentials) {
    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
    })

    if (response.status >= 500) {
        throw new Error("Erreur interne du serveur. Veuillez réessayer.")
    }

    if (!response.ok) {
        throw new Error("Votre compte a été créé avec succès. Cependant, une erreur réseau a empêché l'authentification.")
    }

    const data = await response.json()
    return data.access_token
}