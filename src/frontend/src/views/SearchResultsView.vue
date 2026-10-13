<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import RecipeCard from '@/components/RecipeCard.vue'
import { useRecipes } from '@/composables/useRecipes'

const route = useRoute()
const router = useRouter()

const {
  recipes,
  loading,
  error,
  total,
  loadRecipes,
} = useRecipes()

const search = ref('')

const perPage = 8
const totalPages = computed(() => Math.ceil(total.value / perPage))

watch(
  () => [
    route.query.search,
    route.query.category,
    route.query.difficulty,
    route.query.page,
    route.query.sort_by,
    route.query.sort_order,
  ],
  ([searchQuery, categoryQuery, difficultyQuery, pageQuery, sortBy, sortOrder]) => {
    search.value = searchQuery || ''

    loadRecipes({
      search: searchQuery || '',
      category: categoryQuery || '',
      difficulty: difficultyQuery || '',
      page: Number(pageQuery) || 1,
      per_page: perPage,
      sort_by: sortBy || '',
      sort_order: sortOrder || '',
    })
  },
  { immediate: true },
)
</script>

<template>
  <main class="flex-1 px-6 py-8">
    <div class="mx-auto max-w-7xl">

      <h1 class="mb-8 text-3xl font-bold text-gray-900">
        Résultats de recherche
      </h1>

      <p class="mb-8 text-gray-600">
        Résultats pour :
        <span class="font-semibold">
          "{{ search }}"
        </span>
      </p>

      <p v-if="loading">
        Chargement des recettes...
      </p>

      <p v-else-if="error" class="text-red-500">
        {{ error }}
      </p>

      <p v-else-if="recipes.length === 0" class="text-gray-500">
        Aucune recette trouvée.
      </p>

      <section v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <RecipeCard v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" />
      </section>

      <nav v-if="totalPages > 1" aria-label="page" class="mt-8 flex justify-center gap-2">
        <button v-for="page in totalPages" :key="page" type="button"
          :aria-current="Number(route.query.page || 1) === page ? 'page' : undefined" class="rounded border px-3 py-2"
          @click="router.push({
            path: '/search',
            query: { ...route.query, page: String(page) },
          })">
          {{ page }}
        </button>
      </nav>

    </div>
  </main>
</template>