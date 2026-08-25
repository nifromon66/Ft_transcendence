import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const rawUser = localStorage.getItem('user')

    return {
      token: localStorage.getItem('token') || null,
      user: (rawUser && rawUser !== 'undefined') ? JSON.parse(rawUser) : null
    }
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)

      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user');
      }
    },
    clearAuth() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
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
