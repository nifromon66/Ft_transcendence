import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'

export function uploadFileToServer(token, file, endpoint, fileTypeLabel, onProgress) {
    return new Promise((resolve, reject) => {
        if (!navigator.onLine) {
            return reject(new Error(`Impossible de transférer ${fileTypeLabel} : vous êtes hors ligne.`))
        }

        if (!token) {
            return reject(new Error(`Impossible de transférer ${fileTypeLabel} : vous n'êtes pas authentifié.`))
        }

        const baseUrl = import.meta.env.VITE_API_URL || ''

        const xhr = new XMLHttpRequest()
        const formData = new FormData()
        formData.append('file', file)

        xhr.open('POST', `${baseUrl}${endpoint}`)
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        xhr.setRequestHeader('Accept', 'application/json')

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable && onProgress) {
                const progress = Math.round((event.loaded / event.total) * 100)
                onProgress(progress)
            }
        }

        xhr.onload = () => {
            if (xhr.status === 401) {
                const authStore = useAuthStore()
                authStore.clearAuth()
                router.push({ name: 'login' })
                return reject(new Error("Votre session a expiré. Veuillez vous reconnecter."))
            }

            let responseData = {}
            try {
                responseData = JSON.parse(xhr.responseText)
            } catch (error) {
                return reject(new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard."))
            }

            if (xhr.status >= 200 && xhr.status < 300) {
                if (responseData.success === false || responseData.error) {
                    return reject(new Error(responseData.error || `Impossible de transférer ${fileTypeLabel}.`))
                }
                return resolve(responseData)
            }

            let serverErrorMessage = responseData.error || `Impossible de transférer ${fileTypeLabel}.`
            let finalMessage

            switch (xhr.status) {
                case 400:
                    finalMessage = `Requête invalide : ${serverErrorMessage}`
                    break
                case 403:
                    finalMessage = "Accès refusé. Action non autorisée."
                    break
                case 404:
                    finalMessage = "Ressource introuvable."
                    break
                case 413:
                    finalMessage = "Le fichier est trop volumineux."
                    break
                default:
                    if (xhr.status >= 500) {
                        finalMessage = "Erreur interne du serveur. Veuillez réessayer."
                    } else {
                        finalMessage = `Erreur ${xhr.status} : ${serverErrorMessage}`
                    }
            }

            reject(new Error(finalMessage))
        }

        xhr.onerror = () => {
            reject(new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet."))
        }
        xhr.send(formData)
    })
}