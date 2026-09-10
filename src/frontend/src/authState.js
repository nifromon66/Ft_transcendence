import { defineStore } from 'pinia'
import { fetchUserProfile } from '@/services/userService'
import { connectSocket, disconnectSocket } from '@/services/socketService'

export const useAuthStore = defineStore('auth', {
  state: () => {
    const rawUser = localStorage.getItem('user')
    const parsedUser = (rawUser && rawUser !== 'undefined') ? JSON.parse(rawUser) : null

    if (parsedUser && parsedUser.id) {
      connectSocket(parsedUser.id)
    }

    return {
      token: localStorage.getItem('token') || null,
      user: parsedUser
    }
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('token', token)

      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
        connectSocket(user.id)
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
