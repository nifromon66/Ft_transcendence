<script setup>
import { useChatStore } from '@/stores/chatState';
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/authState';
import FriendAvatar from '@/components/FriendAvatar.vue';
import DocumentUpload from '@/components/DocumentUpload.vue';
import { fetchDocumentBlob } from '@/services/fileService';

const chatStore = useChatStore()
const authStore = useAuthStore()

const newMessage = ref('')
const messagesContainer = ref(null)

const showDocumentUpload = ref(false)
const pendingDocument = ref(null)
const uploadKey = ref(0)

const handleDocumentReady = (file) => {
    pendingDocument.value = file
}

const canSend = computed(() => {
    return newMessage.value.trim().length > 0 || pendingDocument.value !== null
})

onMounted(async () => {
    await chatStore.fetchFriends()
})

const handleSend = async () => {
    if (!canSend.value) {
        return
    }

    await chatStore.sendMessage(newMessage.value, pendingDocument.value)

    if (!chatStore.chatError) {
        newMessage.value = ''
        pendingDocument.value = null
        showDocumentUpload.value = false
        uploadKey.value++
    }
}

const downloadFile = async (fileUrl, fileName) => {
    try {
        const token = authStore.token || localStorage.getItem('token')
        const blob = await fetchDocumentBlob(fileUrl, token)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = fileName || 'document'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
    } catch {
        useNotificationStore().addError('Erreur lors du téléchargement')
        alert('Impossible de télécharger le document.')
    }
}

const deleteMessage = (messageId) => {
    if (confirm('Voulez-vous vraiment supprimer ce message ?')) {
        chatStore.deleteMessage(messageId)
    }
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
                    <div v-for="msg in chatStore.messages" :key="msg.id" class="flex flex-col relative group"
                        :class="msg.sender_id === authStore.user?.id ? 'items-end' : 'items-start'">

                        <button v-if="msg.sender_id === authStore.user?.id" @click="deleteMessage(msg.id)"
                            class="absolute -top-2 -left-3 opacity-0 group-hover:opacity-100 bg-red-100 text-red-600 rounded-full p-1 shadow hover:bg-red-200 transition-opacity"
                            title="Supprimer le message">
                            <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>

                        <div class="max-w-md px-4 py-2 rounded-2xl shadow-sm text-sm"
                            :class="msg.sender_id === authStore.user?.id ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'">

                            <p v-if="msg.content" :class="msg.file_url ? 'mb-2' : ''">{{ msg.content }}</p>

                            <div v-if="msg.file_url"
                                class="flex items-center justify-between rounded-lg bg-white p-3 border border-gray-200 w-full min-w-62.5">
                                <div class="flex items-center space-x-3 overflow-hidden">
                                    <svg class="h-8 w-8 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                                        <path
                                            d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z">
                                        </path>
                                    </svg>
                                    <div class="flex flex-col truncate text-gray-800">
                                        <span class="truncate text-sm font-semibold">
                                            {{ msg.file_name || 'Document' }}</span>
                                        <span v-if="msg.file_size" class="text-xs text-gray-500">{{
                                            (msg.file_size / 1024 / 1024).toFixed(2) }} Mo</span>
                                    </div>
                                </div>

                                <div class="flex space-x-1 shrink-0 ml-2">
                                    <a href="#" @click.prevent="downloadFile(msg.file_url, msg.file_name)"
                                        title="Télécharger le document"
                                        class="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors">
                                        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4">
                                            </path>
                                        </svg>
                                    </a>
                                </div>
                            </div>

                        </div>
                    </div>

                    <div v-if="chatStore.messages.length === 0" class="text-center text-gray-500 text-sm mt-10">
                        Dites bonjour à {{ chatStore.activeContact.username }} !
                    </div>
                </div>

                <div v-if="showDocumentUpload" class="px-4 pt-3 bg-gray-50 border-t border-gray-200">
                    <DocumentUpload :key="uploadKey" @document-ready="handleDocumentReady" />
                </div>

                <div class="p-4 bg-gray-50 flex gap-2 items-center shrink-0"
                    :class="!showDocumentUpload ? 'border-t border-gray-200' : ''">

                    <button @click="showDocumentUpload = !showDocumentUpload"
                        class="p-2 text-gray-500 hover:text-indigo-600 transitions-colors"
                        :class="showDocumentUpload ? 'text-indigo-600' : ''">
                        📎
                    </button>

                    <input id="chat-message" name="chat-message" v-model="newMessage" @keyup.enter="handleSend" type="text"
                        placeholder="Écrivez un message..."
                        class="flex-1 bg-white border border-gray-300 rounded-full px-4 py-2 text-gray-900 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition">

                    <button @click="handleSend" :disabled="!canSend"
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