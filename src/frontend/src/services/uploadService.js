export function uploadAvatar(token, file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        const formData = new FormData()
        formData.append('file', file)

        xhr.open('POST', '/api/upload')
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable && onProgress) {
                const progress = Math.round((event.loaded / event.total) * 100)
                onProgress(progress)
            }
        }

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve()
                return
            }

            let serverErrorMessage = "Une erreur est survenue lors du transfert de l'image."

            try {
                const responseData = JSON.parse(xhr.responseText)
                if (responseData.error) {
                    serverErrorMessage = responseData.error
                }
            } catch (e) {

            }

            let finalMessage = serverErrorMessage;

            switch (xhr.status) {
                case 400:
                    finalMessage = `Requête invalide : ${serverErrorMessage}`
                    break;
                case 401:
                case 403:
                    finalMessage = "Session invalide ou expirée. L'envoi a été refusé."
                    break;
                case 413:
                    finalMessage = "L'image est trop volumineuse."
                    break;
                case 500:
                    finalMessage = `Erreur interne du serveur : ${serverErrorMessage}`
                    break;
                default:
                    finalMessage = `Erreur ${xhr.status} : ${serverErrorMessage}`
            }

            reject(new Error(finalMessage))
        }

        xhr.onerror = () => {
            reject(new Error("Erreur réseau lors du transfert de l'image."))
        }
        xhr.send(formData)
    })
}