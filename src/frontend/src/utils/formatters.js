export function formatFileSize(bytes) {
    if (bytes === 0) {
        return '0 Octets'
    }

    const k = 1024
    const sizes = ['Octets', 'Ko', 'Mo', 'Go', 'To']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    const validIndex = Math.min(i, sizes.length - 1)
    return parseFloat((bytes / Math.pow(k, validIndex)).toFixed(1)) + ' ' + sizes[validIndex]
}