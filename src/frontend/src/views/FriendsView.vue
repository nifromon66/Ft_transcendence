<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useFriends } from '@/composables/useFriends'
import { useAuthStore } from '@/stores/authState'
import FriendAvatar from '@/components/FriendAvatar.vue'
import { socket, connectSocket } from '@/services/socketService'

const authStore = useAuthStore()

const {
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
} = useFriends()

const searchQuery = ref('')
const friendToDelete = ref(null)
const isDeletingFriend = ref(false)

const openDeleteFriendModal = (user) => {
    friendToDelete.value = user
}

const closeDeleteFriendModal = () => {
    if (!isDeletingFriend.value) {
        friendToDelete.value = null
    }
}

const confirmDeleteFriend = async () => {
    if (!friendToDelete.value || isDeletingFriend.value) return
    isDeletingFriend.value = true
    try {
        await deleteFriend(friendToDelete.value.id)
        friendToDelete.value = null
    } catch {
        // errorMessage is handled in useFriends
    } finally {
        isDeletingFriend.value = false
    }
}

const requestAllStatuses = () => {
    if (!socket || !socket.connected) return
    const ids = [
        ...friendsList.value.map(u => u.id),
        ...discoverList.value.map(u => u.id),
        ...sentRequestsList.value.map(u => u.id),
        ...receivedRequestsList.value.map(u => u.id),
        ...searchResults.value.map(u => u.id)
    ].filter(Boolean)

    if (ids.length > 0) {
        socket.emit('request_initial_status', ids)
    }
}

const handleSearch = async () => {
    if (searchQuery.value.trim() !== '') {
        await performSearch(searchQuery.value)
        requestAllStatuses()
    }
}

const handleStatusChange = (data) => {
    updateUserStatus(data.user_id, data.is_online)
}

const handleFriendshipUpdated = async () => {
    await loadFriends()
    await Promise.all([
        loadReceivedRequests(),
        loadSentRequests(),
        loadDiscoverUsers()
    ])

    if (searchQuery.value.trim() !== '') {
        await performSearch(searchQuery.value)
    }
    requestAllStatuses()
}

const handleProfileUpdated = (data) => {
    const updateNameInList = (listRef) => {
        if (!listRef.value) {
            return
        }
        const user = listRef.value.find(u => u.id === data.user_id)
        if (user) {
            user.username = data.new_username
        }
    }

    updateNameInList(friendsList)
    updateNameInList(receivedRequestsList)
    updateNameInList(sentRequestsList)
    updateNameInList(discoverList)
    updateNameInList(searchResults)
}

const onWindowFocus = () => {
    requestAllStatuses()
}

onMounted(async () => {
    if (authStore.token && (!socket || !socket.connected)) {
        connectSocket(authStore.token)
    }

    if (socket) {
        socket.on('user_status_changed', handleStatusChange)
        socket.on('friendship_updated', handleFriendshipUpdated)
        socket.on('user_profile_updated', handleProfileUpdated)
        socket.on('connect', requestAllStatuses)
    }

    window.addEventListener('focus', onWindowFocus)
    document.addEventListener('visibilitychange', onWindowFocus)

    await loadFriends()
    await Promise.all([
        loadReceivedRequests(),
        loadSentRequests(),
        loadDiscoverUsers()
    ])

    requestAllStatuses()
})

onUnmounted(() => {
    window.removeEventListener('focus', onWindowFocus)
    document.removeEventListener('visibilitychange', onWindowFocus)
    if (socket) {
        socket.off('user_status_changed', handleStatusChange)
        socket.off('friendship_updated', handleFriendshipUpdated)
        socket.off('user_profile_updated', handleProfileUpdated)
        socket.off('connect', requestAllStatuses)
    }
})
</script>

<template>
    <div class="flex-1 max-w-4xl mx-auto p-4 sm:p-6 space-y-10">
        <header>
            <h1 class="text-3xl font-bold text-gray-800">Gestion des amis</h1>
        </header>

        <div v-if="errorMessage" class="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-sm">
            <p class="font-medium">{{ errorMessage }}</p>
        </div>

        <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Rechercher un utilisateur</h2>

            <div class="flex flex-col sm:flex-row gap-2 mb-6">
                <input id="search-friend" name="search-friend" v-model="searchQuery" type="text" placeholder="Entrez un pseudo..."
                    class="flex-1 px-4 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow"
                    @keyup.enter="handleSearch" />
                <button @click="handleSearch" :disabled="isLoading"
                    class="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-colors disabled:opacity-50">
                    {{ isLoading ? 'Recherche en cours...' : 'Rechercher' }}
                </button>
            </div>

            <ul v-if="searchResults.length > 0" class="space-y-3">
                <li v-for="user in searchResults" :key="user.id"
                    class="flex items-center justify-between gap-3 p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <RouterLink :to="{ name: 'public-profile', params: { id: user.id } }"
                        class="flex items-center gap-3 group cursor-pointer min-w-0 flex-1">
                        <FriendAvatar :user="user" class="transition-transform group-hover:scale-105 shrink-0" />
                        <div class="flex items-center gap-2 min-w-0">
                            <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors truncate" :title="user.username">
                                {{ user.username }}
                            </span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white shrink-0"
                                :class="user.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="user.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </RouterLink>

                    <div class="flex gap-2">
                        <button v-if="user.friendship_status === 'none'" @click="addFriend(user.id)"
                            class="shrink-0 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition">Ajouter</button>
                        <button v-if="user.friendship_status === 'pending_sent'" @click="cancelRequest(user.id)"
                            class="shrink-0 px-4 py-2 bg-white text-gray-600 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-100 transition">Annuler
                            la demande d'ami</button>
                        <button v-if="user.friendship_status === 'pending_received'" @click="acceptRequest(user.id)"
                            class="shrink-0 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition">Accepter
                        </button>
                        <button v-if="user.friendship_status === 'accepted'"
                            @click="openDeleteFriendModal(user)"
                            class="shrink-0 px-4 py-2 bg-white text-red-500 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">Supprimer
                        </button>
                    </div>
                </li>
            </ul>
        </section>

        <section v-if="receivedRequestsList.length > 0"
            class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                Demandes reçues
                <span class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {{ receivedRequestsList.length }}</span>
            </h2>
            <ul class="space-y-3">
                <li v-for="req in receivedRequestsList" :key="req.id"
                    class="flex items-center justify-between gap-3 p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <RouterLink :to="{ name: 'public-profile', params: { id: req.id } }"
                        class="flex items-center gap-3 group cursor-pointer min-w-0 flex-1">
                        <FriendAvatar :user="req" class="transition-transform group-hover:scale-105 shrink-0" />
                        <div class="flex items-center gap-2 min-w-0">
                            <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors truncate" :title="req.username">
                                {{ req.username }}
                            </span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white shrink-0"
                                :class="req.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="req.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </RouterLink>

                    <div class="flex gap-2">
                        <button @click="acceptRequest(req.id)"
                            class="shrink-0 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition">
                            Accepter</button>
                        <button @click="denyRequest(req.id)"
                            class="shrink-0 px-4 py-2 bg-white text-red-600 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">
                            Refuser</button>
                    </div>
                </li>
            </ul>
        </section>

        <section v-if="sentRequestsList.length > 0" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 class="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
                Demandes envoyées
                <span class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {{ sentRequestsList.length }}</span>
            </h2>
            <ul class="space-y-3">
                <li v-for="req in sentRequestsList" :key="req.id"
                    class="flex items-center justify-between gap-3 p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <RouterLink :to="{ name: 'public-profile', params: { id: req.id } }"
                        class="flex items-center gap-3 group cursor-pointer min-w-0 flex-1">
                        <FriendAvatar :user="req" class="transition-transform group-hover:scale-105 shrink-0" />
                        <div class="flex items-center gap-2 min-w-0">
                            <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors truncate" :title="req.username">
                                {{ req.username }}
                            </span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white shrink-0"
                                :class="req.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="req.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </RouterLink>

                    <button @click="cancelRequest(req.id)"
                        class="shrink-0 px-4 py-2 bg-white text-gray-600 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-100 transition">
                        Annuler</button>
                </li>
            </ul>
        </section>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
            <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Mes amis</h2>
                <p v-if="friendsList.length === 0" class="text-gray-500 italic text-sm">
                    Vous n'avez pas encore d'amis.
                </p>
                <ul v-else class="space-y-3">
                    <li v-for="friend in friendsList" :key="friend.id"
                        class="flex items-center justify-between gap-3 p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200">

                        <RouterLink :to="{ name: 'public-profile', params: { id: friend.id } }"
                        class="flex items-center gap-3 group cursor-pointer min-w-0 flex-1">
                            <FriendAvatar :user="friend" class="transition-transform group-hover:scale-105 shrink-0" />
                            <div class="flex items-center gap-2 min-w-0">
                            <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors truncate" :title="friend.username">
                                {{ friend.username }}
                            </span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white shrink-0"
                                    :class="friend.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                    :title="friend.is_online ? 'En ligne' : 'Hors ligne'">
                                </span>
                            </div>
                        </RouterLink>

                        <button @click="openDeleteFriendModal(friend)"
                            class="shrink-0 px-3 py-1.5 bg-white text-red-500 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">Supprimer</button>
                    </li>
                </ul>
            </section>

            <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Suggestions d'amis</h2>
                <p v-if="discoverList.length === 0" class="text-gray-500 italic text-sm">Aucune suggestion d'amis pour
                    le moment</p>
                <ul v-else class="space-y-3">
                    <li v-for="user in discoverList" :key="user.id"
                        class="flex items-center justify-between gap-3 p-3 sm:p-4 bg-gray-50 rounded-lg border border-gray-200">

                        <RouterLink :to="{ name: 'public-profile', params: { id: user.id } }"
                        class="flex items-center gap-3 group cursor-pointer min-w-0 flex-1">
                            <FriendAvatar :user="user" class="transition-transform group-hover:scale-105 shrink-0" />
                            <div class="flex items-center gap-2 min-w-0">
                            <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors truncate" :title="user.username">
                                {{ user.username }}
                            </span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white shrink-0"
                                    :class="user.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                    :title="user.is_online ? 'En ligne' : 'Hors ligne'">
                                </span>
                            </div>
                        </RouterLink>

                        <button @click="addFriend(user.id)"
                            class="shrink-0 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 text-sm font-medium rounded-md hover:bg-blue-100 transition">
                            Ajouter</button>
                    </li>
                </ul>
            </section>
        </div>

        <!-- Modal confirmation suppression ami -->
        <div v-if="friendToDelete"
            class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4"
            role="dialog" aria-modal="true" aria-labelledby="modal-delete-friend-title">
            <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
                <h3 id="modal-delete-friend-title" class="text-xl font-bold text-gray-800 mb-4">
                    Retirer de vos amis
                </h3>
                <p class="text-gray-600 mb-6 text-sm">
                    Êtes-vous sûr de vouloir retirer <span class="font-semibold text-gray-900">{{ friendToDelete.username }}</span> de vos amis ?
                </p>
                <div class="flex justify-end space-x-3">
                    <button type="button" @click="closeDeleteFriendModal" :disabled="isDeletingFriend"
                        class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 font-medium transition-colors disabled:opacity-50">
                        Annuler
                    </button>
                    <button type="button" @click="confirmDeleteFriend" :disabled="isDeletingFriend"
                        class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium transition-colors disabled:opacity-50">
                        {{ isDeletingFriend ? 'Suppression...' : 'Confirmer' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>
