<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const search = ref('')
const router = useRouter()

function submitSearch() {
  const query = search.value.trim()

  if (!query) {
    return
  }

  router.push({
    path: '/search',
    query: {
      search: query,
    },
  })
}
</script>

<template>
  <form
    class="flex w-full max-w-2xl gap-3"
    @submit.prevent="submitSearch"
  >
    <input
      v-model="search"
      type="search"
      placeholder="Rechercher une recette..."
      aria-label="Rechercher une recette"
      class="flex-1 rounded-lg border border-gray-300 px-4 py-3
             text-gray-900 outline-none
             focus:border-gray-500 focus:ring-2 focus:ring-gray-200"
    />

    <button
      type="submit"
      class="rounded-lg bg-gray-900 px-6 py-3
             font-medium text-white
             hover:bg-gray-700"
    >
      Rechercher
    </button>
  </form>
</template>