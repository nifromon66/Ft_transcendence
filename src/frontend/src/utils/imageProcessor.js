export async function optimizeImage(file, maxWidth = 800, maxHeight = 800, quality = 0.8) {
    if (typeof createImageBitmap === 'function') {
        const bitmap = await createImageBitmap(file)
        let { width, height } = bitmap

        if (width > height) {
            if (width > maxWidth) {
                height = Math.round(height * (maxWidth / width))
                width = maxWidth
            }
        } else {
            if (height > maxHeight) {
                width = Math.round(width * (maxHeight / height))
                height = maxHeight
            }
        }

        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d')
        ctx.drawImage(bitmap, 0, 0, width, height)
        bitmap.close()

        return new Promise((resolve, reject) => {
            canvas.toBlob(
                (blob) => {
                    if (!blob) {
                        reject(new Error('Canvas conversion failed.'))
                        return
                    }

                    const newFileName = file.name.replace(/\.[^/.]+$/, "") + ".webp"
                    const optimizedFile = new File([blob], newFileName, {
                        type: 'image/webp',
                        lastModified: Date.now()
                    })

                    optimizedFile.originalName = file.name
                    resolve(optimizedFile)
                },
                'image/webp',
                quality
            )
        })
    }

    return new Promise((resolve, reject) => {
        const url = URL.createObjectURL(file)
        const img = new Image()

        img.onload = () => {
            URL.revokeObjectURL(url)
            let width = img.width
            let height = img.height

            if (width > height) {
                if (width > maxWidth) {
                    height = Math.round(height * (maxWidth / width))
                    width = maxWidth
                }
            } else {
                if (height > maxHeight) {
                    width = Math.round(width * (maxHeight / height))
                    height = maxHeight
                }
            }

            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height

            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)

            canvas.toBlob(
                (blob) => {
                    if (!blob) {
                        reject(new Error('Canvas conversion failed.'))
                        return
                    }

                    const newFileName = file.name.replace(/\.[^/.]+$/, "") + ".webp"
                    const optimizedFile = new File([blob], newFileName, {
                        type: 'image/webp',
                        lastModified: Date.now()
                    })

                    optimizedFile.originalName = file.name
                    resolve(optimizedFile)
                },
                'image/webp',
                quality
            )
        }

        img.onerror = () => {
            URL.revokeObjectURL(url)
            reject(new Error("File could not be loaded as an image."))
        }

        img.src = url
    })
}
