/**
 * Resizes and compresses an image using HTML5 Canvas.
 * @param {File} file - The original image file.
 * @param {number} maxWidth - The maximum allowed width.
 * @param {number} maxHeight - The maximum allowed height.
 * @param {number} quality - The WebP compression quality (0 to 1).
 * @returns {Promise<File>} - The new optimized image file.
 */
export function optimizeImage(file, maxWidth = 800, maxHeight = 800, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()

        reader.onload = (event) => {
            const img = new Image()
            img.src = event.target.result

            img.onload = () => {
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

            img.onerror = () => reject(new Error('File could not be loaded as an image.'))
        }

        reader.onerror = () => reject(new Error('Error reading the file.'))

        reader.readAsDataURL(file)
    })
}