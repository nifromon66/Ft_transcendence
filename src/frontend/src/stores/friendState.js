import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/authState.js'
import * as friendService from '@/services/friendService.js'

export const useFriendStore = defineStore('friend', {
    state: () => ({
        friendsList: [],
        searchResults: [],
        discoverList: [],
        receivedRequestsList: [],
        sentRequestsList: [],
        errorMessage: '',
        isLoading: false
    }),

    actions: {
        async loadFriends() {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            this.isLoading = true
            try {
                this.friendsList = await friendService.fetchFriends(authStore.token)
                this.errorMessage = ''
            } catch (error) {
                this.errorMessage = error.message
                this.friendsList = []
            } finally {
                this.isLoading = false
            }
        },

        async loadReceivedRequests() {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                this.receivedRequestsList = await friendService.fetchReceivedRequests(authStore.token)
                this.errorMessage = ''
            } catch (error) {
                this.errorMessage = error.message
            }
        },

        async loadSentRequests() {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                this.sentRequestsList = await friendService.fetchSentRequests(authStore.token)
                this.errorMessage = ''
            } catch (error) {
                this.errorMessage = error.message
            }
        },

        async loadDiscoverUsers() {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            this.isLoading = true
            try {
                this.discoverList = await friendService.fetchDiscoverUsers(authStore.token)
                this.errorMessage = ''
            } catch (error) {
                this.errorMessage = error.message
            } finally {
                this.isLoading = false
            }
        },

        async performSearch(query) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            if (!query.trim()) {
                this.searchResults = []
                return
            }

            this.isLoading = true
            try {
                this.searchResults = await friendService.searchUsers(query, authStore.token)
                this.errorMessage = ''
            } catch (error) {
                this.errorMessage = error.message
                this.searchResults = []
            } finally {
                this.isLoading = false
            }
        },

        async addFriend(targetUserId) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                await friendService.sendFriendRequest(targetUserId, authStore.token)
                this.errorMessage = ''

                const discUser = this.discoverList.find(u => u.id === targetUserId)
                const searchUser = this.searchResults.find(u => u.id === targetUserId)
                const userToAdd = discUser || searchUser

                if (discUser) {
                    this.discoverList = this.discoverList.filter(u => u.id !== targetUserId)
                }

                if (searchUser) {
                    searchUser.friendship_status = 'pending_sent'
                }

                if (userToAdd && !this.sentRequestsList.some(u => u.id === targetUserId)) {
                    this.sentRequestsList.push({ ...userToAdd, friendship_status: 'pending_sent' })
                } else {
                    await this.loadSentRequests()
                }
            } catch (error) {
                this.errorMessage = error.message
                throw error
            }
        },

        async acceptRequest(senderId) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                await friendService.acceptFriendRequest(senderId, authStore.token)
                this.errorMessage = ''

                const acceptedUser = this.receivedRequestsList.find(req => req.id === senderId)
                this.receivedRequestsList = this.receivedRequestsList.filter(req => req.id !== senderId)

                const searchUser = this.searchResults.find(u => u.id === senderId)
                if (searchUser) {
                    searchUser.friendship_status = 'accepted'
                }

                if (acceptedUser) {
                    this.friendsList.push(acceptedUser)
                } else {
                    await this.loadFriends()
                }
            } catch (error) {
                this.errorMessage = error.message
                throw error
            }
        },

        async denyRequest(senderId) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                await friendService.denyFriendRequest(senderId, authStore.token)
                this.errorMessage = ''

                this.receivedRequestsList = this.receivedRequestsList.filter(req => req.id !== senderId)

                const searchUser = this.searchResults.find(u => u.id === senderId)
                if (searchUser) {
                    searchUser.friendship_status = 'none'
                }
            } catch (error) {
                this.errorMessage = error.message
                throw error
            }
        },

        async cancelRequest(targetUserId) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                await friendService.cancelFriendRequest(targetUserId, authStore.token)
                this.errorMessage = ''

                const userToRestore = this.sentRequestsList.find(req => req.id === targetUserId)
                this.sentRequestsList = this.sentRequestsList.filter(req => req.id !== targetUserId)

                const searchUser = this.searchResults.find(u => u.id === targetUserId)
                if (searchUser) {
                    searchUser.friendship_status = 'none'
                }

                if (userToRestore && !this.discoverList.some(u => u.id === targetUserId)) {
                    this.discoverList.unshift(userToRestore)
                }
            } catch (error) {
                this.errorMessage = error.message
                throw error
            }
        },

        async deleteFriend(friendId, username) {
            if (!confirm(`Êtes-vous sûr de vouloir retirer ${username} de vos amis ?`)) {
                return
            }

            const authStore = useAuthStore()
            if (!authStore.token) {
                return
            }

            try {
                await friendService.removeFriend(friendId, authStore.token)
                this.errorMessage = ''

                const friendObj = this.friendsList.find(f => f.id === friendId)
                this.friendsList = this.friendsList.filter(f => f.id !== friendId)

                if (friendObj && !this.discoverList.some(u => u.id === friendId)) {
                    this.discoverList.unshift(friendObj)
                }

                const searchUser = this.searchResults.find(u => u.id === friendId)
                if (searchUser) {
                    searchUser.friendship_status = 'none'
                }
            } catch (error) {
                this.errorMessage = error.message
                throw error
            }
        },

        updateUserStatus(userId, isOnline) {
            const targets = [
                this.friendsList,
                this.searchResults,
                this.discoverList,
                this.receivedRequestsList,
                this.sentRequestsList
            ]

            targets.forEach(list => {
                const user = list.find(u => u.id === userId)
                if (user) {
                    user.is_online = isOnline
                }
            })
        }
    }
})