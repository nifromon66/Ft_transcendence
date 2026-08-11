export function formatFileSize(bytes) {
    if (bytes === 0) {
        return '0 Octets'
    }

    const k = 1024
    const sizes = ['Octets', 'Ko', 'Mo']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}