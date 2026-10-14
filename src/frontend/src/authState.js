import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService'
import { connectSocket, disconnectSocket } from '@/services/socketService'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const rawUser = localStorage.getItem('user')
    const parsedUser = (rawUser && rawUser !== 'undefined') ? JSON.parse(rawUser) : null
    const token = localStorage.getItem('token') || null

    if (token) {
      connectSocket(token)
    }

    return {
      token: token,
      user: parsedUser
    }
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
      } catch (error) {
        console.warn('Impossible d’actualiser les récompenses du compte.', error)
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
