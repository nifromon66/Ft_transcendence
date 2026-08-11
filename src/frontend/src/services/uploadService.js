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
            } else {
                let errorMsg = "Une erreur est survenue lors du transfert de l'image."
                try {
                    const uploadError = JSON.parse(xhr.responseText)
                    errorMsg = uploadError.error || errorMsg
                } catch (e) { }
                reject(new Error(errorMsg))
            }
        }

        xhr.onerror = () => reject(new Error("Erreur réseau lors du transfert de l'image."))

        xhr.send(formData)
    })
}