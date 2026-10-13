import { defineStore } from 'pinia'
import { useAuthStore } from '@/stores/authState.js'
import { socket } from '@/services/socketService.js'

import * as friendService from '@/services/friendService'
import * as messageService from '@/services/messageService'

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

            try {
                this.friendsList = await friendService.fetchFriends(authStore.token)
            } catch (error) {
                this.chatError = error.message || "Impossible de charger la liste d'amis."
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
                this.messages = await messageService.fetchConversation(friendId, authStore.token)
            } catch (error) {
                this.chatError = error.message || "Erreur lors du chargement des messages."
            }
        },

        sendMessage(content, fileData = null) {
            if (!this.activeContact) {
                return
            }

            if (!socket) {
                this.chatError = "La connexion au serveur n'est pas encore établie."
                return
            }

            const payload = {
                receiver_id: this.activeContact.id,
                content: content
            }

            if (fileData) {
                Object.assign(payload, fileData)
            }

            socket.emit('send_message', payload)

        },

        initializeSocketListeners() {
            if (!socket) {
                return
            }

            socket.off('receive_message')
            socket.off('message_error')
            socket.off('user_status_changed')
            socket.off('message_deleted')
            socket.off('user_updated')

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

            socket.on('message_deleted', (data) => {
                const messageId = data.message_id
                this.messages = this.messages.filter(m => m.id !== messageId)
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

        async deleteMessage(messageId) {
            const authStore = useAuthStore()
            if (!authStore.token) {
                this.chatError = "Vous n'êtes pas authentifié."
                return
            }

            try {
                await messageService.deleteMessage(messageId, authStore.token)
                this.messages = this.messages.filter(m => m.id !== messageId)
            } catch (error) {
                this.chatError = error.message || "Erreur lors de la suppression du message."
            }
        },

        clearError() {
            this.chatError = null
        }
    }
})