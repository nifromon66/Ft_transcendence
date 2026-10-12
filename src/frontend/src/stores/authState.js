import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService.js'
import { connectSocket, disconnectSocket } from '@/services/socketService.js'

/**
 * @typedef {import('@/services/userService').UserProfile} UserProfile
 */

export const useAuthStore = defineStore('auth', {
    state: () => {
        const rawUser = localStorage.getItem('user')
        const parsedUser = (rawUser && rawUser !== 'undefined') ? JSON.parse(rawUser) : null
        const token = localStorage.getItem('token') || null

        return {
            /** @type {string | null} */
            token: token,
            /** @type {UserProfile | null} */
            user: parsedUser
        }
    },
    actions: {
        initializeAuth() {
            if (this.token) {
                connectSocket(this.token)
            }
        },

        /**
         * @param {string} token 
         * @param {UserProfile} user 
         */
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
