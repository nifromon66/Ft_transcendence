<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useFriends } from '@/composables/useFriends'
import FriendAvatar from '@/components/FriendAvatar.vue'
import { socket } from '@/services/socketService'

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

const handleSearch = async () => {
    if (searchQuery.value.trim() != '') {
        await performSearch(searchQuery.value)
    }
}

onMounted(async () => {
    await Promise.all([
        loadFriends(),
        loadReceivedRequests(),
        loadSentRequests(),
        loadDiscoverUsers()
    ])

    if (socket) {
        socket.on('user_status_changed', (data) => {
            updateUserStatus(data.user_id, data.is_online)
        })
    }
})

onUnmounted(() => {
    if (socket) {
        socket.off('user_status_changed')
    }
})
</script>

<template>
    <div class="max-w-4xl mx-auto p-4 sm:p-6 space-y-10">
        <header>
            <h1 class="text-3xl font-bold text-gray-800">Gestion des amis</h1>
        </header>

        <div v-if="errorMessage" class="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-sm">
            <p class="font-medium">{{ errorMessage }}</p>
        </div>

        <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Rechercher un utilisateur</h2>

            <div class="flex gap-2 mb-6">
                <input v-model="searchQuery" type="text" placeholder="Entrez un pseudo..."
                    class="flex-1 px-4 py-2 bg-white text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow"
                    @keyup.enter="handleSearch" />
                <button @click="handleSearch" :disabled="isLoading"
                    class="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-colors disabled:opacity-50">
                    {{ isLoading ? 'Recherche en cours...' : 'Rechercher' }}
                </button>
            </div>

            <ul v-if="searchResults.length > 0" class="space-y-3">
                <li v-for="user in searchResults" :key="user.id"
                    class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <div class="flex items-center gap-3">
                        <FriendAvatar :user="user" />
                        <div class="flex items-center gap-2">
                            <span class="font-medium text-gray-700">{{ user.username }}</span>
                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white"
                                :class="user.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="user.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </div>

                    <div class="flex gap-2">
                        <button v-if="user.friendship_status === 'none'" @click="addFriend(user.id)"
                            class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition">Ajouter
                            en ami</button>
                        <button v-if="user.friendship_status === 'pending_sent'" @click="cancelRequest(user.id)"
                            class="px-4 py-2 bg-white text-gray-600 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-100 transition">Annuler
                            la demande d'ami</button>
                        <button v-if="user.friendship_status === 'pending_received'" @click="acceptRequest(user.id)"
                            class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition">Accepter
                            la demande d'ami
                        </button>
                        <button v-if="user.friendship_status === 'accepted'" @click="deleteFriend(user.id)"
                            class="px-4 py-2 bg-white text-red-500 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">Supprimer
                            l'ami
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
                    class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <div class="flex items-center gap-3">
                        <FriendAvatar :user="req" />
                        <div class="flex items-center gap-2">
                            <span class="font-medium text-gray-700">{{ req.username }}</span>

                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white"
                                :class="req.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="req.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </div>

                    <div class="flex gap-2">
                        <button @click="acceptRequest(req.id)"
                            class="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 transition">
                            Accepter la demande d'ami</button>
                        <button @click="denyRequest(req.id)"
                            class="px-4 py-2 bg-white text-red-600 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">
                            Refuser la demande d'ami</button>
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
                    class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">

                    <div class="flex items-center gap-3">
                        <FriendAvatar :user="req" />
                        <div class="flex items-center gap-2">
                            <span class="font-medium text-gray-700">{{ req.username }}</span>

                            <span class="h-2.5 w-2.5 rounded-full inline-block border border-white"
                                :class="req.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="req.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                    </div>

                    <button @click="cancelRequest(req.id)"
                        class="px-4 py-2 bg-white text-gray-600 border border-gray-300 text-sm font-medium rounded-md hover:bg-gray-100 transition">
                        Annuler la demande d'ami</button>
                </li>
            </ul>
        </section>

        <div class="grid md:grid-cols-2 gap-8">
            <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Mes amis</h2>
                <p v-if="friendsList.length === 0" class="text-gray-500 italic text-sm">
                    Vous n'avez pas encore d'amis.
                </p>
                <ul v-else class="space-y-3">
                    <li v-for="friend in friendsList" :key="friend.id"
                        class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">

                        <div class="flex items-center gap-3">
                            <FriendAvatar :user="friend" />
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-gray-700">{{ friend.username }}</span>

                                <span class="h-2.5 w-2.5 rounded-full inline-block border border-white"
                                    :class="friend.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                    :title="friend.is_online ? 'En ligne' : 'Hors ligne'">
                                </span>
                            </div>
                        </div>

                        <button @click="deleteFriend(friend.id)"
                            class="px-3 py-1.5 bg-white text-red-500 border border-red-200 text-sm font-medium rounded-md hover:bg-red-50 transition">Supprimer
                            cet ami</button>
                    </li>
                </ul>
            </section>

            <section class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h2 class="text-xl font-semibold text-gray-800 mb-4">Suggestions d'amis</h2>
                <p v-if="discoverList.length === 0" class="text-gray-500 italic text-sm">Aucune suggestion d'amis pour
                    le moment</p>
                <ul v-else class="space-y-3">
                    <li v-for="user in discoverList" :key="user.id"
                        class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">

                        <div class="flex items-center gap-3">
                            <FriendAvatar :user="user" />
                            <div class="flex items-center gap-2">
                                <span class="font-medium text-gray-700">{{ user.username }}</span>

                                <span class="h-2.5 w-2.5 rounded-full inline-block border border-white"
                                    :class="user.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                    :title="user.is_online ? 'En ligne' : 'Hors ligne'">
                                </span>
                            </div>
                        </div>

                        <button @click="addFriend(user.id)"
                            class="px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 text-sm font-medium rounded-md hover:bg-blue-100 transition">
                            Ajouter cet ami</button>
                    </li>
                </ul>
            </section>
        </div>
    </div>
</template>