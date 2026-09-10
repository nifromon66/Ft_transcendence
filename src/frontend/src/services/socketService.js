import { io } from 'socket.io-client'

export let socket = null

export const connectSocket = (userId) => {
    if (socket) {
        return socket
    }

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'

    socket = io(apiUrl, {
        path: '/socket.io',
        query: { user_id: userId },
        transports: ['websocket'],
        reconnectionAttempts: 3,
        reconnectionDelay: 2000
    })

    return socket
}

export const disconnectSocket = () => {
    if (socket) {
        socket.disconnect()
        socket = null
    }
}