<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import RecipeCard from '@/components/RecipeCard.vue'
import { useRecipes } from '@/composables/useRecipes'

const route = useRoute()

const {
  recipes,
  loading,
  error,
  loadRecipes,
} = useRecipes()

const search = ref(route.query.search || '')

onMounted(() => {
  loadRecipes(search.value)
})
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

      <p
        v-else-if="error"
        class="text-red-500"
      >
        {{ error }}
      </p>

      <p
        v-else-if="recipes.length === 0"
        class="text-gray-500"
      >
        Aucune recette trouvée.
      </p>

      <section
        v-else
        class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        <RecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
        />
      </section>

    </div>
  </main>
</template>