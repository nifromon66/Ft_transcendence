<script setup>
import { useChatStore } from '@/chatState';
import { computed, ref } from 'vue'

const chatStore = useChatStore()
const newMessageText = ref('')

const currentMessages = computed(() => {
    if (!chatStore.activeContact) {
        return []
    }
    return chatStore.messages.filter(
        m => m.senderId === chatStore.activeContact.id || m.recipientId === chatStore.activeContact.id
    )
})

const handleSend = () => {
    if (!newMessageText.value.trim()) {
        return
    }
    chatStore.sendMessage(newMessageText.value)
    newMessageText.value = ''
}
</script>

<template>
    <div>TODO</div>
</template>