<script setup>
defineProps({
  id: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <main class="mx-auto min-h-screen max-w-4xl px-6 py-8">
    <h1 class="text-3xl font-bold">
      Détail de la recette {{ id }}
    </h1>
  </main>
</template>