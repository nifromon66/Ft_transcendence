import { io } from 'socket.io-client'

const apiUrl = import.meta.env.VITE_API_URL || ''

export const socket = io(apiUrl, {
    path: '/socket.io/',
    autoConnect: false,
    reconnectionAttempts: 3,
    reconnectionDelay: 2000
})

export const connectSocket = (token) => {
    if (!navigator.onLine) {
        throw new Error("Impossible de se connecter au serveur : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de se connecter au serveur : vous n'êtes pas authentifié.")
    }

    if (socket.connected && socket.auth?.token === token) {
        return
    }

    socket.auth = { token }
    socket.connect()
}

export const disconnectSocket = () => {
    if (socket.connected) {
        socket.auth = {}
        socket.disconnect()
    }
}