export function uploadFileToServer(token, file, endpoint, fileTypeLabel, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        const formData = new FormData()
        formData.append('file', file)

        xhr.open('POST', endpoint)
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)

        xhr.upload.onprogress = (event) => {
            if (event.lengthComputable && onProgress) {
                const progress = Math.round((event.loaded / event.total) * 100)
                onProgress(progress)
            }
        }

        xhr.onload = () => {
            let responseData = {}
            try {
                responseData = JSON.parse(xhr.responseText)
            } catch (e) {

            }

            if (xhr.status >= 200 && xhr.status < 300) {
                if (responseData.success === false) {
                    reject(new Error(responseData.error || `Erreur serveur lors de l'envoi de ${fileTypeLabel}.`))
                    return
                }
                resolve(responseData)
                return
            }

            let serverErrorMessage = responseData.error || `Une erreur est survenue lors du transfert de ${fileTypeLabel}.`
            let finalMessage

            switch (xhr.status) {
                case 400:
                    finalMessage = `Requête invalide : ${serverErrorMessage}`
                    break
                case 401:
                case 403:
                    finalMessage = "Session invalide ou expirée. L'envoi a été refusé."
                    break
                case 413:
                    finalMessage = "Le fichier est trop volumineux."
                    break
                case 500:
                    finalMessage = `Erreur interne du serveur : ${serverErrorMessage}`
                    break
                default:
                    finalMessage = `Erreur ${xhr.status} : ${serverErrorMessage}`
            }

            reject(new Error(finalMessage))
        }

        xhr.onerror = () => {
            reject(new Error(`Erreur réseau lors du transfert de ${fileTypeLabel}.`))
        }
        xhr.send(formData)
    })
}

export function uploadAvatar(token, file, onProgress) {
    return uploadFileToServer(token, file, '/api/upload/avatar', "l'image", onProgress)
}

export function uploadDocument(token, file, onProgress) {
    return uploadFileToServer(token, file, '/api/upload/document', "le document", onProgress)
}