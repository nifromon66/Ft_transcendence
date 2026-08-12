/**
 * Validates an uploaded avatar file (checks existence, allowed extensions, MIME types, and 10MB size limit).
 * @param {File} file - The uploaded image file to validate.
 * @returns {{isValid: boolean, error: string|null}} An object indicating if the file is valid, along with an error message if it is not.
 */
export const validateAvatar = (file) => {
    const MAX_UPLOAD_SIZE = 10 * 1024 * 1024
    const ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp']
    const ALLOWED_MIMETYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

    if (!file) return {
        isValid: false,
        error: "Aucun fichier fourni."
    }

    const fileName = file.name
    const hasExtension = fileName.includes('.')
    const fileExtension = hasExtension ? fileName.split('.').pop().toLowerCase() : ''

    if (!hasExtension || !ALLOWED_EXTENSIONS.includes(fileExtension)) {
        return {
            isValid: false,
            error: "L'extension du fichier n'est pas autorisée (.png, .jpg, .jpeg, .gif, ou .webp uniquement)."
        }
    }

    if (!ALLOWED_MIMETYPES.includes(file.type)) {
        return {
            isValid: false,
            error: "Le format du fichier n'est pas reconnu comme une image valide."
        }
    }

    if (file.size > MAX_UPLOAD_SIZE) {
        return {
            isValid: false,
            error: "Le fichier dépasse la taille autorisée (10 Mo max)."
        }
    }
    return {
        isValid: true,
        error: null
    }
}