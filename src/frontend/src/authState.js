import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
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
