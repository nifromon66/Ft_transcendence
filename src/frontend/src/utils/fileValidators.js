const validateFile = (file, options) => {
    const {
        allowedExtensions,
        allowedMimeTypes,
        maxSize,
        maxSizeLabel,
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
        return {
            isValid: false,
            error: `Le fichier dépasse la taille autorisée (${maxSizeLabel} max).`
        }
    }
    return {
        isValid: true,
        error: null
    }
}

export const validateAvatar = (file) => {
    return validateFile(file, {
        typeName: "avatar",
        allowedExtensions: ['png', 'jpg', 'jpeg', 'gif', 'webp'],
        allowedMimeTypes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
        maxSize: 10 * 1024 * 1024,
        maxSizeLabel: "10 Mo"
    })
}

export const validateDocument = (file) => {
    return validateFile(file, {
        typeName: "document",
        allowedExtensions: ['pdf'],
        allowedMimeTypes: ['application/pdf'],
        maxSize: 5 * 1024 * 1024,
        maxSizeLabel: "5 Mo"
    })
}

export const validateRecipeImage = (file) => {
    return validateFile(file, {
        typeName: "image",
        allowedExtensions: ['png', 'jpg', 'jpeg', 'webp'],
        allowedMimeTypes: [
            'image/png',
            'image/jpeg',
            'image/webp',
        ],
        maxSize: 10 * 1024 * 1024,
        maxSizeLabel: "10 Mo",
    })
}