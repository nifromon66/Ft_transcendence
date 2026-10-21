<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchCategories, fetchDifficulties, } from '@/services/recipeService'

const search = ref('')
const route = useRoute()
const router = useRouter()
const difficulty = ref('')
const category = ref('')
const difficulties = ref(fetchDifficulties())
const categories = ref([])

watch(
  () => [route.query.search, route.query.category, route.query.difficulty],
  ([searchQuery, categoryQuery, difficultyQuery]) => {
    search.value = searchQuery || ''
    category.value = categoryQuery || ''
    difficulty.value = difficultyQuery || ''
  },
  { immediate: true },
)

onMounted(async () => {
  categories.value = await fetchCategories()
})

function submitSearch() {
  const query = {}

  if (search.value.trim()) query.search = search.value.trim()
  if (category.value) query.category = category.value
  if (difficulty.value) query.difficulty = difficulty.value

  if (Object.keys(query).length === 0) return

  router.push({
    path: '/search',
    query,
  })
}
</script>

<template>
  <form class="flex w-full max-w-2xl gap-3" @submit.prevent="submitSearch">
    <input id="search-recipe" name="search-recipe" v-model="search" type="search"
      placeholder="Rechercher une recette..." aria-label="Rechercher une recette" class="flex-1 rounded-lg bg-white border border-gray-300 px-4 py-3
             text-gray-900 outline-none
             focus:border-gray-500 focus:ring-2 focus:ring-gray-200" />

    <select id="search-category" name="search-category" v-model="category"
      class="rounded-lg border border-gray-300 bg-white px-3 py-3 text-gray-900 outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200">
      <option value="">Catégorie</option>
      <option v-for="item in categories" :key="item.id" :value="item.name">
        {{ item.name }}
      </option>
    </select>

    <select id="search-difficulty" name="search-difficulty" v-model="difficulty"
      class="rounded-lg border border-gray-300 bg-white px-3 py-3 text-gray-900 outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200">
      <option value="">Difficulté</option>
      <option v-for="option in difficulties" :key="option.value || 'all'" :value="option.value">
        {{ option.label }}
      </option>
    </select>

    <button type="submit" class="rounded-lg bg-primary-dark px-6 py-3
             font-medium text-white
             hover:bg-primary">
      Rechercher
    </button>
  </form>
</template>