/**
 * Uploads the user avatar to the server with progress tracking.
 * @param {string} token - The JWT authentication token.
 * @param {File} file - The image file to upload.
 * @param {Function} [onProgress] - Optional callback function to track upload progress percentage (0 to 100).
 * @returns {Promise<void>} Resolves when the upload completes successfully.
 * @throws {Error} If the upload fails due to network issues or server rejection.
 */
export function uploadAvatar(token, file, onProgress) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()
        const formData = new FormData()
        formData.append('file', file)

        xhr.open('POST', '/api/upload/avatar')
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
                    reject(new Error(responseData.error || "Erreur serveur lors de l'envoi de l'image."))
                    return
                }
                resolve(responseData)
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