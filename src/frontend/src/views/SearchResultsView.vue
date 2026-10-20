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

const currentSortLabel = computed(() => {
  const sortBy = route.query.sort_by
  const sortOrder = route.query.sort_order

  if (!sortBy || !sortOrder) {
    return 'Défaut'
  }

  const sortLabels = {
    updated_at: {
      desc: 'Les plus récentes',
      asc: 'Les moins récentes',
    },
    cooking_time: {
      desc: 'Durée : la plus longue',
      asc: 'Durée : la moins longue',
    },
    rating: {
      desc: 'Meilleures notes',
      asc: 'Notes les plus basses',
    },
  }

  return sortLabels[sortBy]?.[sortOrder] || 'Défaut'
})

const isSortMenuOpen = ref(false)

function applySort(sortBy, sortOrder = 'asc') {
  isSortMenuOpen.value = false
  router.push({
    path: '/search',
    query: {
      ...route.query,
      sort_by: sortBy,
      sort_order: sortOrder,
      page: '1',
    },
  })
}
</script>

<template>
  <main class="flex-1 px-6 py-8">
    <div class="mx-auto max-w-7xl">
      <div class="relative mb-6 flex justify-end">
        <button type="button"
          class="rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-700 shadow-sm hover:bg-gray-50"
          :aria-expanded="isSortMenuOpen" aria-haspopup="true" @click="isSortMenuOpen = !isSortMenuOpen">
          Trier par : 
          <span class="font-semibold text-gray-900">
            {{ currentSortLabel }}
          </span>
        </button>

        <div v-if="isSortMenuOpen"
          class="absolute right-0 top-full z-10 mt-2 w-56 rounded-lg border border-gray-200 bg-white py-1 shadow-lg"
          role="menu">
          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('updated_at', 'desc')">
            Les plus récentes
          </button>

          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('updated_at', 'asc')">
            Les moins récentes
          </button>

          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('cooking_time', 'desc')">
            Durée : la plus longue
          </button>

          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('cooking_time', 'asc')">
            Durée : la moins longue
          </button>

          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('rating', 'desc')">
            Meilleures notes
          </button>

          <button type="button" class="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
            role="menuitem" @click="applySort('rating', 'asc')">
            Notes les plus basses
          </button>

        </div>
      </div>

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