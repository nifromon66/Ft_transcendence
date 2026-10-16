import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService.js'
import { connectSocket, disconnectSocket } from '@/services/socketService.js'
import { refreshAccessToken, logoutUser } from '@/services/authService.js'

export const useAuthStore = defineStore('auth', {
    state: () => {
        const rawUser = localStorage.getItem('user')
        const parsedUser = (rawUser && rawUser !== 'undefined') ? JSON.parse(rawUser) : null
        const token = localStorage.getItem('token') || null

        return {
            token: token,
            user: parsedUser,
            isInitialized: false,
        }
    },
    actions: {
        initializeAuth() {
            if (this.token) {
                connectSocket(this.token)
            }
        },

        setAuth(token, user) {
            this.token = token
            this.user = user
            localStorage.setItem('token', token)

            if (user) {
                localStorage.setItem('user', JSON.stringify(user))
                connectSocket(token)
            } else {
                localStorage.removeItem('user');
            }
        },

        async silentRefresh() {
            try {
                const newToken = await refreshAccessToken()
                this.token = newToken
                localStorage.setItem('token', newToken)
                if (!this.user) {
                    await this.fetchUser()
                } else {
                    connectSocket(this.token)
                }
            } catch (error) {
                this.clearAuth()
                throw error
            }
        },

        async logout() {
            await logoutUser()
            this.clearAuth()
        },

        clearAuth() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            disconnectSocket()
        },

        async fetchUser() {
            if (!this.token) {
                return
            }
            try {
                const userData = await fetchUserProfile(this.token)
                this.setAuth(this.token, userData)
            } catch (error) {
                this.clearAuth()
                throw error
            }
        }
    }
})
