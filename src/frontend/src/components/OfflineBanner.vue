<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const isOffline = ref(!navigator.onLine)

const updateOnlineStatus = () => {
    isOffline.value = !navigator.onLine
}

onMounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
})

onUnmounted(() => {
    window.addEventListener('online', updateOnlineStatus)
    window.addEventListener('offline', updateOnlineStatus)
})
</script>

<template>
    <div v-if="isOffline"
        class="bg-red-600 text-white text-center py-2 px-4 text-sm font-medium shadow-md transition-all">
        ⚠️ Vous êtes actuellement hors ligne. Certaines fonctionnalités sont limitées.
    </div>
</template>