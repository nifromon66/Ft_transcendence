<script setup>
import { toRef } from 'vue'
import { useAvatar } from '@/composables/useAvatar'

const props = defineProps({
    user: {
        type: Object,
        required: true,
    }
})

const { avatarImageSrc } = useAvatar(toRef(props, 'user'))
</script>

<template>
    <div
        class="h-10 w-10 rounded-full overflow-hidden bg-gray-200 flex items-center justify-center font-bold text-gray-600 shrink-0 border border-gray-200">
        <img v-if="avatarImageSrc" :src="avatarImageSrc" :alt="user.username" class="h-full w-full object-cover" />
        <span v-else> {{ user.username?.charAt(0).toUpperCase() }}</span>
    </div>
</template>