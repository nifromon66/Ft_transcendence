<script setup>
import { useChatStore } from '@/chatState';
import { ref, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/authState';
import FriendAvatar from '@/components/FriendAvatar.vue';

const chatStore = useChatStore()
const authStore = useAuthStore()

const newMessage = ref('')
const friendsList = ref([])
const messagesContainer = ref(null)

onMounted(async () => {
    await chatStore.fetchFriends()
})

const handleSend = () => {
    if (!newMessage.value.trim()) {
        return
    }
    chatStore.sendMessage(newMessage.value)
    newMessage.value = ''
}

watch(() => chatStore.messages.length, async () => {
    await nextTick()
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
})
</script>

<template>
    <div class="flex h-[calc(100vh-10rem)] max-w-7xl mx-auto bg-white shadow-xl rounded-lg overflow-hidden my-4">

        <div class="w-80 border-r border-gray-200 bg-gray-50 flex flex-col">
            <div class="p-4 border-b border-gray-200">
                <h2 class="text-lg font-semibold text-gray-800 dark:text-white">Conversations</h2>
            </div>

            <div class="flex-1 overflow-y-auto p-2 space-y-1">
                <div v-for="friend in chatStore.friendsList" :key="friend.id"
                    @click="chatStore.setActiveContact(friend)"
                    class="flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors group"
                    :class="chatStore.activeContact?.id === friend.id ? 'bg-indigo-100' : 'hover:bg-gray-200'">
                    <div class="flex items-center space-x-3">
                        <div class="relative">
                            <FriendAvatar :user="friend" />
                            <span
                                class="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full inline-block border border-white"
                                :class="friend.is_online ? 'bg-green-500' : 'bg-gray-300'"
                                :title="friend.is_online ? 'En ligne' : 'Hors ligne'">
                            </span>
                        </div>
                        <span class="font-medium text-gray-700 group-hover:text-blue-600 transition-colors">
                            {{ friend.username }}
                        </span>
                    </div>

                    <span v-if="chatStore.unreadCounts[friend.id]"
                        class="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {{ chatStore.unreadCounts[friend.id] }}
                    </span>
                </div>
            </div>
        </div>

        <div class="flex-1 flex flex-col bg-white relative">

            <div v-if="chatStore.chatError"
                class="absolute top-0 w-full bg-red-500 text-white p-2 text-center text-sm z-10 flex justify-between px-4">
                <span>{{ chatStore.chatError }}</span>
                <button @click="chatStore.clearError()" class="font-bold">&times;</button>
            </div>

            <template v-if="chatStore.activeContact">
                <div class="p-4 border-b border-gray-200 flex items-center shadow-sm">
                    <h3 class="text-lg font-bold text-gray-800">{{ chatStore.activeContact.username }}</h3>
                </div>

                <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
                    <div v-for="msg in chatStore.messages" :key="msg.id" class="flex flex-col"
                        :class="msg.sender_id === authStore.user?.id ? 'items-end' : 'items-start'">
                        <div class="max-w-md px-4 py-2 rounded-2xl shadow-sm text-sm"
                            :class="msg.sender_id === authStore.user?.id ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'">
                            {{ msg.content }}
                        </div>
                    </div>

                    <div v-if="chatStore.messages.length === 0" class="text-center text-gray-500 text-sm mt-10">
                        Dites bonjour à {{ chatStore.activeContact.username }} !
                    </div>
                </div>

                <div class="p-4 border-t border-gray-200 bg-gray-50 flex gap-2 items-center shrink-0">
                    <button class="p-2 text-gray-500 hover:text-indigo-600 transitions-colors">
                        📎
                    </button>

                    <input v-model="newMessage" @keyup.enter="handleSend" type="text"
                        placeholder="Écrivez un nessage..."
                        class="flex-1 bg-white border border-gray-300 rounded-full px-4 py-2 text-gray-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus-ring-indigo-500 transition">

                    <button @click="handleSend" :disabled="!newMessage.trim()"
                        class="bg-indigo-600 text-white px-5 py-2 rounded-full font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed">
                        Envoyer
                    </button>
                </div>
            </template>

            <div v-else class="flex-1 flex items-center justify-center text-gray-500">
                <div class="text-center">
                    <div class="text-4xl mb-4">💬</div>
                    <p>Sélectionnez une conversation pour commencer</p>
                </div>
            </div>
        </div>

    </div>
</template>