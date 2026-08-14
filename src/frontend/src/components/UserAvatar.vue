<script setup>
defineProps({
  user: {
    type: Object,
    default: null,
  },
  expanded: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['activate'])
</script>

<template>
  <button
    type="button"
    class="flex h-10 w-10 scale-125 cursor-pointer items-center justify-center rounded-full border 
        border-black text-lg font-bold text-white"
    :class="user ? 'bg-primary-light' : 'bg-gray-500'"
    :title="user ? `Connecté en tant que ${user.username}` : 'Non connecté'"
    :aria-label="user ? `Menu de ${user.username}` : 'Menu du compte'"
    aria-haspopup="menu"
    :aria-expanded="expanded"
    @click="emit('activate')"
  >
    <span v-if="user">
      {{ user.username.charAt(0).toUpperCase() }}
    </span>

    <span v-else>?</span>
  </button>
</template>