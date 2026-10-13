import { io } from 'socket.io-client'

const apiUrl = import.meta.env.VITE_API_URL || ''

/**
 * The single Socket instance (Singleton).
 * Created immediately but disconnected by default (autoConnect: false).
 * This allows stores to attach listeners (.on) before the network is active.
 * @type {import('socket.io-client').Socket}
 */
export const socket = io(apiUrl, {
    path: '/socket.io/',
    autoConnect: false,
    reconnectionAttempts: 3,
    reconnectionDelay: 2000
})

/**
 * Connects the socket instance for real-time communication.
 * @param {string} token - The user's JWT access token.
 * @throws {Error} If the user is unauthorized or a network error occurs.
 */
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

/**
 * Disconnects and destroys the curent socket instance.
 */
export const disconnectSocket = () => {
    if (socket.connected) {
        socket.auth = {}
        socket.disconnect()
    }
}