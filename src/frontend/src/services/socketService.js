import { io } from 'socket.io-client'

const apiUrl = import.meta.env.VITE_API_URL || ''

export const socket = io(apiUrl, {
    path: '/socket.io/',
    transports: ['websocket'],
    autoConnect: false,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: Infinity,
    auth: (cb) => {
        const token = localStorage.getItem('token')
        cb({ token })
    }
})

if (typeof window !== 'undefined') {
    window.addEventListener('focus', () => {
        if (localStorage.getItem('token') && !socket.connected && !socket.active) {
            socket.connect()
        }
    })
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && localStorage.getItem('token') && !socket.connected && !socket.active) {
            socket.connect()
        }
    })
}

export const connectSocket = (token) => {
    if (!navigator.onLine) {
        throw new Error("Impossible de se connecter au serveur : vous êtes hors ligne.")
    }

    if (!token) {
        throw new Error("Impossible de se connecter au serveur : vous n'êtes pas authentifié.")
    }

    if (socket.connected || socket.active) {
        return
    }

    socket.connect()
}

export const disconnectSocket = () => {
    if (socket.connected) {
        socket.disconnect()
    } else if (socket.active) {
        const closeWhenReady = () => {
            socket.off('connect', closeWhenReady)
            socket.off('connect_error', closeWhenReady)
            socket.disconnect()
        }
        socket.on('connect', closeWhenReady)
        socket.on('connect_error', closeWhenReady)
    }
}
