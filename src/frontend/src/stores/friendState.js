import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/authState.js'
import * as friendService from '@/services/friendService.js'

/**
 * @typedef {import('@/services/friendService').FriendUser} FriendUser
 */

export const useFriendStore = defineStore('friend', {
    state: () => ({
        /** @type {FriendUser[]} */
        friendsList: [],
        /** @type {FriendUser[]} */
        searchResults: [],
        /** @type {FriendUser[]} */
        discoverList: [],
        /** @type {FriendUser[]} */
        receivedRequestsList: [],
        /** @type {FriendUser[]} */
        sentRequestsList: [],
        /** @type {string} */
        errorMessage: '',
        /** @type {boolean} */
        isLoading: false
    }),

    actions: {
        /**
         * Loads the accepted friends list.
         * @returns {Promise<void>}
         */
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

        /**
         * Loads pending friend requests received by the user.
         * @returns {Promise<void>}
         */
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

        /**
         * Loads pending friend requests sent by the user.
         * @returns {Promise<void>}
         */
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

        /**
         * Loads suggestions for new users to discover.
         * @returns {Promise<void>}
         */
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

        /**
         * Searches for users by username.
         * @param {string} query - The search query. 
         * @returns {Promise<void>}
         */
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

        /**
         * Sends a friend request to a specific user.
         * @param {number} targetUserId - The ID of the user to add.
         * @returns {Promise<void>}
         */
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

        /**
         * Accepts a pending friend request.
         * @param {number} senderId - The ID of the user who sent the request.
         * @returns {Promise<void>}
         */
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

        /**
         * Denies a pending friend request.
         * @param {number} senderId - The ID of the user aho sent the request.
         * @returns {Promise<void>}
         */
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

        /**
         * Cancels a friend request previously sent by the current user.
         * @param {number} targetUserId - The ID of the user the request was sent to. 
         * @returns {Promise<void>}
         */
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

        /**
         * Removes a user from the friends list.
         * @param {number} friendId - The ID of the friend to remove.
         * @param {string} username - The username of the friend
         * @returns {Promise<void>}
         */
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

        /**
         * Updates a user's online status across all relevant lists.
         * @param {number} userId - The ID of the user.
         * @param {boolean} isOnline - The new online status.
         */
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