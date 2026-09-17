import { defineStore } from 'pinia'

export const useChatStore = defineStore('chat', {
    state: () => ({
        activeContact: null,
        messages: [
            { id: 1, senderId: 2, recipientId: 1, content: 'Salut ! Prêt pour le chat ?', createdAt: '10:00' },
            { id: 1, senderId: 1, recipientId: 2, content: 'Salut ! Prêt pour le chat !', createdAt: '10:00' }
        ]
    }),
    actions: {
        setActiveContact(contact) {
            this.activeContact = contact
        },
        sendMessage(content) {
            if (!this.activeContact) {
                return
            }

            const newMessage = {
                id: Date.now(),
                senderId: 1,
                recipientId: this.activeContact.id,
                content: content,
                createdAt: new Date().toLocaleDateString([], { hour: '2-digit', minute: '2-digit' })
            }
            this.messages.push(newMessage)
        }
    }
})