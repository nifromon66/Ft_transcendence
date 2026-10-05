<script setup>
import { toRef } from 'vue'
import AvatarFrame from '@/components/AvatarFrame.vue'
import { useAvatar } from '@/composables/useAvatar'

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
  expanded: {
    type: Boolean,
    default: false,
  }
})

const emit = defineEmits(['activate'])

const { avatarImageSrc, errorMessage } = useAvatar(toRef(props, 'user'))
</script>

<template>
  <span class="relative inline-flex">
    <AvatarFrame :frame="user?.avatar_frame" class="scale-125" />
    <button type="button" class="flex h-10 w-10 scale-125 cursor-pointer items-center justify-center rounded-full border
          border-black text-lg font-bold text-white overflow-hidden" :class="user ? 'bg-primary-light' : 'bg-gray-500'"
      :title="user ? `Connecté en tant que ${user.username}` : 'Non connecté'"
      :aria-label="user ? `Menu de ${user.username}` : 'Menu du compte'" aria-haspopup="menu" :aria-expanded="expanded"
      @click="emit('activate')">
      <img v-if="avatarImageSrc" :src="avatarImageSrc" :alt="`Avatar de ${user.username}`"
        class="h-full w-full object-cover" />

      <span v-else-if="user">
        {{ user?.username ? user.username.charAt(0).toUpperCase() : '?' }}
      </span>

      <span v-else>?</span>
    </button>
  </span>
</template>
