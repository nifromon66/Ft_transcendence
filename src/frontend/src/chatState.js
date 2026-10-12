import { defineStore } from 'pinia'
import { useAuthStore } from './authState'
import { socket } from './services/socketService'

export const useChatStore = defineStore('chat', {
    state: () => ({
        friendsList: [],
        activeContact: null,
        messages: [],
        unreadCounts: {},
        chatError: null
    }),
    actions: {
        async fetchFriends() {
            const authStore = useAuthStore()
            const token = authStore.token || localStorage.getItem('token')

            try {
                const response = await fetch('/friends', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                const data = await response.json()
                if (response.ok && data.success) {
                    this.friendsList = data.friends
                }
            } catch (error) {

            }
        },

        async setActiveContact(contact) {
            this.activeContact = contact
            this.messages = []
            this.chatError = null

            if (contact) {
                if (this.unreadCounts[contact.id]) {
                    this.unreadCounts[contact.id] = 0
                }
                await this.fetchConversation(contact.id)
            }
        },

        async fetchConversation(friendId) {
            const authStore = useAuthStore()

            const token = authStore.token || localStorage.getItem('token')

            try {
                const response = await fetch(`/api/messages/${friendId}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                })

                const data = await response.json()

                if (response.ok && data.success) {
                    this.messages = data.messages
                }

            } catch (error) {

            }
        },

        async sendMessage(content, fileData = null) {
            if (!this.activeContact) {
                return
            }

            if (!socket) {
                this.chatError = "La connexion au serveur n'est pas encore établie."
                return
            }

            let uploadedFileUrl = null
            let uploadedFileName = null
            let uploadedFileSize = null
            let uploadedFileType = null

            if (fileData) {
                const authStore = useAuthStore()
                const token = authStore.token || localStorage.getItem('token')

                const formData = new FormData()
                formData.append('file', fileData)

                try {
                    const response = await fetch('/api/messages/documents', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        },
                        body: formData
                    })

                    const result = await response.json()

                    if (!response.ok || !result.success) {
                        this.chatError = result.error || "Erreur lors de l'upload du document."
                        return
                    }

                    uploadedFileName = result.filename
                    uploadedFileSize = fileData.size
                    uploadedFileType = fileData.mime_type || fileData.mime_type
                    uploadedFileUrl = `/uploads/${uploadedFileName}`

                } catch (error) {
                    this.chatError = "Erreur réseau lors de l'envoi du document."
                    return
                }
            }

            const payload = {
                receiver_id: this.activeContact.id,
                content: content,
                file_url: uploadedFileUrl,
                file_name: fileData ? fileData.name : null,
                file_type: uploadedFileType,
                file_size: uploadedFileSize
            }

            socket.emit('send_message', payload)
        },

        initializeSocketListeners() {

            if (!socket) {
                return
            }

            socket.off('receive_message')
            socket.off('message_error')

            socket.on('receive_message', (message) => {
                const isRelevantToActiveChat = this.activeContact && (message.sender_id == this.activeContact.id || message.receiver_id === this.activeContact.id)

                if (isRelevantToActiveChat) {
                    this.messages.push(message)
                } else {
                    const authStore = useAuthStore()
                    const myId = authStore.user?.id

                    if (myId && message.sender_id !== myId) {
                        const currentCount = this.unreadCounts[message.sender_id] || 0
                        this.unreadCounts[message.sender_id] = currentCount + 1
                    }
                }
            })

            socket.on('message_error', (data) => {
                this.chatError = data.error

                setTimeout(() => {
                    this.chatError = null
                }, 5000)
            })

            socket.on('user_status_changed', (data) => {
                const friend = this.friendsList.find(f => f.id === data.user_id)
                if (friend) {
                    friend.is_online = data.is_online
                }
                if (this.activeContact && this.activeContact.id === data.user_id) {
                    this.activeContact.is_online = data.is_online
                }
            })

            socket.on('user_updated', (data) => {
                const friend = this.friendsList.find(f => f.id === data.user_id)
                if (friend) {
                    if (data.username) {
                        friend.username = data.username
                    }
                }

                if (this.activeContact && this.activeContact.id === data.user_id) {
                    if (data.username) {
                        this.activeContact.username = data.username
                    }
                }
            })
        },

        clearError() {
            this.chatError = null
        }
    }
})