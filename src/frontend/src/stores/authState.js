import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService.js'
import { connectSocket, disconnectSocket } from '@/services/socketService.js'
import { refreshAccessToken, logoutUser } from '@/services/authService.js'

let refreshPromise = null

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
    getters: {
        can: (state) => (permission) => Boolean(state.token && state.user?.permissions?.includes(permission)),
    },
    actions: {
        updateRewards(data) {
            if (!this.user) return
            this.user.avatar_frame = data.avatar_frame
            this.user.level_rewards = data.level_rewards
            this.user.xp_progress = data.xp_progress
            localStorage.setItem('user', JSON.stringify(this.user))
        },

        async refreshRewards() {
            const token = this.token
            if (!token || !this.user) return
            try {
                const data = await fetchUserProfile(token)
                if (this.token === token) this.updateRewards(data)
            } catch {
            }
        },

        async initializeAuth() {
            if (this.token) {
                connectSocket(this.token)
                try { await this.fetchUser() } catch { /* La session invalide est effacée par fetchUser. */ }
            }
        },

        setAuth(token, user) {
            this.token = token
            this.user = user
            localStorage.setItem('token', token)
            localStorage.setItem('has_session', 'true')

            if (user) {
                localStorage.setItem('user', JSON.stringify(user))
                connectSocket(token)
            } else {
                localStorage.removeItem('user');
            }
        },

        async silentRefresh() {
            if (!this.token && !localStorage.getItem('has_session')) {
                return null
            }
            if (refreshPromise) {
                return refreshPromise
            }
            refreshPromise = (async () => {
                try {
                    const newToken = await refreshAccessToken()
                    this.token = newToken
                    localStorage.setItem('token', newToken)
                    localStorage.setItem('has_session', 'true')
                    if (!this.user) {
                        await this.fetchUser()
                    } else {
                        connectSocket(this.token)
                    }
                    return newToken
                } catch (error) {
                    this.clearAuth()
                    throw error
                } finally {
                    refreshPromise = null
                }
            })()
            return refreshPromise
        },

        async logout() {
            this.clearAuth()
            await logoutUser()
        },

        clearAuth() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
            localStorage.removeItem('has_session')
            disconnectSocket()
        },

        async fetchUser() {
            const token = this.token
            if (!token) return
            try {
                const userData = await fetchUserProfile(token)
                if (this.token === token) this.setAuth(token, userData)
            } catch (error) {
                if (this.token === token) this.clearAuth()
                throw error
            }
        }
    }
})
