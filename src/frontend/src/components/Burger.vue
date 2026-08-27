<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['activate'])

</script>

<template>
  <button type="button" :aria-label="label"
    class="flex h-9 w-9 cursor-pointer shrink-0 flex-col items-center justify-center gap-1.5 rounded-lg hover:bg-primary-dark"
    @click="emit('activate')">
    <span class="h-0.5 w-5 bg-white"></span>
    <span class="h-0.5 w-5 bg-white"></span>
    <span class="h-0.5 w-5 bg-white"></span>
  </button>
</template>