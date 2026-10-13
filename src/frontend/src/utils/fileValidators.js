import { formatFileSize } from "@/utils/formatters.js"

/**
 * @typedef {Object} ValidationOptions
 * @property {string[]} allowedExtensions - List of allowed file extensions (e.g., ['png', 'jpg']).
 * @property {string[]} allowedMimeTypes - List of allowed MIME types (e.g., ['image/png']).
 * @property {number} maxSize - Maximum file size in bytes.
 * @property {string} typeName - Descriptive name of the file type for error messages (e.g., "avatar").
 */

/**
 * @typedef {Object} ValidationResult
 * @property {boolean} isValid - Indicates if the file passes all checks.
 * @property {string|null} error - Error message if validation fails, null otherwise. 
 */

/**
 * Generic utility to validate a file's extension, MIME type, and size.
 * @param {File} file - The file object to validate. 
 * @param {ValidationOptions} options - The validation constraints. 
 * @returns {ValidationResult} The result of the validation.
 */
const validateFile = (file, options) => {
    const {
        allowedExtensions,
        allowedMimeTypes,
        maxSize,
        typeName
    } = options

    if (!file) return {
        isValid: false,
        error: "Aucun fichier fourni."
    }

    const fileName = file.name
    const hasExtension = fileName.includes('.')
    const fileExtension = hasExtension ? fileName.split('.').pop().toLowerCase() : ''

    if (!hasExtension || !allowedExtensions.includes(fileExtension)) {
        return {
            isValid: false,
            error: "L'extension du fichier n'est pas autorisée."
        }
    }

    if (!allowedMimeTypes.includes(file.type)) {
        return {
            isValid: false,
            error: `Le format du fichier n'est pas reconnu comme un ${typeName} valide.`
        }
    }

    if (file.size > maxSize) {
        const readableMaxSize = formatFileSize(maxSize)
        return {
            isValid: false,
            error: `Le fichier dépasse la taille autorisée (${readableMaxSize} max).`
        }
    }
    return {
        isValid: true,
        error: null
    }
}

/**
 * Validates a user avatar image file.
 * @param {File} file - The avatar file to validate.
 * @returns {ValidationResult}
 */
export const validateAvatar = (file) => {
    return validateFile(file, {
        typeName: "avatar",
        allowedExtensions: ['png', 'jpg', 'jpeg', 'gif', 'webp'],
        allowedMimeTypes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
        maxSize: 10 * 1024 * 1024
    })
}

/**
 * Validates a document file.
 * @param {File} file - The document file to validate.
 * @returns {ValidationResult}
 */
export const validateDocument = (file) => {
    return validateFile(file, {
        typeName: "document",
        allowedExtensions: ['pdf'],
        allowedMimeTypes: ['application/pdf'],
        maxSize: 5 * 1024 * 1024
    })
}

/**
 * Validates a recipe cover image or step image file.
 * @param {File} file - The image file to validate. 
 * @returns {ValidationResult}
 */
export const validateRecipeImage = (file) => {
    return validateFile(file, {
        typeName: "image",
        allowedExtensions: ['png', 'jpg', 'jpeg', 'webp'],
        allowedMimeTypes: [
            'image/png',
            'image/jpeg',
            'image/webp',
        ],
        maxSize: 10 * 1024 * 1024
    })
}