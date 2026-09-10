import { ref } from 'vue'
import { useAuthStore } from '@/authState'
import {
    fetchFriends,
    searchUsers,
    fetchDiscoverUsers,
    fetchReceivedRequests,
    fetchSentRequests,
    sendFriendRequest,
    acceptFriendRequest,
    cancelFriendRequest,
    denyFriendRequest,
    removeFriend
} from '@/services/friendService'

export function useFriends() {
    const authStore = useAuthStore()

    const friendsList = ref([])
    const searchResults = ref([])
    const discoverList = ref([])
    const receivedRequestsList = ref([])
    const sentRequestsList = ref([])

    const errorMessage = ref('')
    const isLoading = ref(false)

    const loadFriends = async () => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        isLoading.value = true
        try {
            friendsList.value = await fetchFriends(token)
            errorMessage.value = ''
        } catch (error) {
            errorMessage.value = error.message
            friendsList.value = []
        } finally {
            isLoading.value = false
        }
    }

    const loadReceivedRequests = async () => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            receivedRequestsList.value = await fetchReceivedRequests(token)
            errorMessage.value = ''
        } catch (error) {
            errorMessage.value = error.message
        }
    }

    const loadSentRequests = async () => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            sentRequestsList.value = await fetchSentRequests(token)
            errorMessage.value = ''
        } catch (error) {
            errorMessage.value = error.message
        }
    }

    const loadDiscoverUsers = async () => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        isLoading.value = true
        try {
            discoverList.value = await fetchDiscoverUsers(token)
            errorMessage.value = ''
        } catch (error) {
            errorMessage.value = error.message
        } finally {
            isLoading.value = false
        }
    }

    const performSearch = async (query) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        if (!query.trim()) {
            searchResults.value = []
            return
        }

        isLoading.value = true
        try {
            searchResults.value = await searchUsers(query, token)
            errorMessage.value = ''
        } catch (error) {
            errorMessage.value = error.message
            searchResults.value = []
        } finally {
            isLoading.value = false
        }
    }

    const addFriend = async (targetUserId) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            await sendFriendRequest(targetUserId, token)
            errorMessage.value = ''

            const discUser = discoverList.value.find(u => u.id === targetUserId)
            const searchUser = searchResults.value.find(u => u.id === targetUserId)
            const userToAdd = discUser || searchUser

            if (discUser) {
                discoverList.value = discoverList.value.filter(u => u.id !== targetUserId)
            }

            if (searchUser) {
                searchUser.friendship_status = 'pending_sent'
            }

            if (userToAdd) {
                if (!sentRequestsList.value.some(u => u.id === targetUserId)) {
                    sentRequestsList.value.push({ ...userToAdd, friendship_status: 'pending_sent' })
                }
            } else {
                await loadSentRequests()
            }

        } catch (error) {
            errorMessage.value = error.message
            throw error
        }
    }

    const acceptRequest = async (senderId) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            await acceptFriendRequest(senderId, token)
            errorMessage.value = ''

            const acceptedUser = receivedRequestsList.value.find(req => req.id === senderId)
            receivedRequestsList.value = receivedRequestsList.value.filter(req => req.id !== senderId)

            const searchUser = searchResults.value.find(u => u.id === senderId)
            if (searchUser) {
                searchUser.friendship_status = 'accepted'
            }

            if (acceptedUser) {
                friendsList.value.push(acceptedUser)
            } else {
                await loadFriends()
            }
        } catch (error) {
            errorMessage.value = error.message
            throw error
        }
    }

    const denyRequest = async (senderId) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            await denyFriendRequest(senderId, token)
            errorMessage.value = ''

            receivedRequestsList.value = receivedRequestsList.value.filter(req => req.id !== senderId)

            const searchUser = searchResults.value.find(u => u.id === senderId)
            if (searchUser) {
                searchUser.friendship_status = 'none'
            }
        } catch (error) {
            errorMessage.value = error.message
            throw error
        }
    }

    const cancelRequest = async (targetUserId) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            await cancelFriendRequest(targetUserId, token)
            errorMessage.value = ''

            const userToRestore = sentRequestsList.value.find(req => req.id === targetUserId)

            sentRequestsList.value = sentRequestsList.value.filter(req => req.id !== targetUserId)

            const searchUser = searchResults.value.find(u => u.id === targetUserId)
            if (searchUser) {
                searchUser.friendship_status = 'none'
            }

            if (userToRestore && !discoverList.value.some(u => u.id === targetUserId)) {
                discoverList.value.unshift(userToRestore)
            }
        } catch (error) {
            errorMessage.value = error.message
            throw error
        }
    }

    const deleteFriend = async (friendId) => {
        const token = authStore.token
        if (!token) {
            errorMessage.value = "Utilisateur non authentifié"
            return
        }

        try {
            const friendObj = friendsList.value.find(f => f.id === friendId)

            await removeFriend(friendId, token)
            errorMessage.value = ''

            friendsList.value = friendsList.value.filter(f => f.id !== friendId)

            if (friendObj && !discoverList.value.some(u => u.id === friendId)) {
                discoverList.value.unshift(friendObj)
            }

            const searchUser = searchResults.value.find(u => u.id === friendId)
            if (searchUser) {
                searchUser.friendship_status = 'none'
            }
        } catch (error) {
            errorMessage.value = error.message
            throw error
        }
    }

    const updateUserStatus = (userId, isOnline) => {
        const friend = friendsList.value.find(f => f.id === userId)
        if (friend) {
            friend.is_online = isOnline
        }

        const searchUser = searchResults.value.find(u => u.id === userId)
        if (searchUser) {
            searchUser.is_online = isOnline
        }

        const discoverUser = discoverList.value.find(u => u.id === userId)
        if (discoverUser) {
            discoverUser.is_online = isOnline
        }

        const sentUser = sentRequestsList.value.find(u => u.id === userId)
        if (sentUser) {
            sentUser.is_online = isOnline
        }

        const receivedUser = receivedRequestsList.value.find(u => u.id === userId)
        if (receivedUser) {
            receivedUser.is_online = isOnline
        }
    }

    return {
        friendsList,
        searchResults,
        discoverList,
        receivedRequestsList,
        sentRequestsList,
        errorMessage,
        isLoading,
        loadFriends,
        loadReceivedRequests,
        loadSentRequests,
        loadDiscoverUsers,
        performSearch,
        addFriend,
        acceptRequest,
        denyRequest,
        cancelRequest,
        deleteFriend,
        updateUserStatus
    }
}