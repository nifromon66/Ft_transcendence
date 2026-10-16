<script setup>
defineProps({
  message: {
    type: String,
    required: true,
  },
})

defineEmits(['close'])
</script>

<template>
  <div
    v-if="message"
    role="alert"
    class="fixed bottom-6 right-6 z-50 flex max-h-[50vh] w-[calc(100%-3rem)] max-w-md items-start gap-4 overflow-y-auto rounded-lg border border-red-200 bg-red-50 p-4 text-red-700 shadow-lg"
  >
    <p class="min-w-0 flex-1 wrap-break-words">{{ message }}</p>
    <button
      type="button"
      aria-label="Fermer le message d’erreur"
      class="shrink-0 rounded px-2 font-bold hover:bg-red-100 focus-visible:outline-2 focus-visible:outline-red-700"
      @click="$emit('close')"
    >
      ×
    </button>
  </div>
</template>
