<script setup>

import RecipeCard from '@/components/RecipeCard.vue'
import { onMounted, ref } from 'vue'
import { fetchLatestRecipes, getRecipes } from '@/services/recipeService'
import SearchBar from '@/components/SearchBar.vue'

const latestRecipes = ref([])
const isLoadingLatestRecipes = ref(true)
const latestRecipesError = ref('')

const recipes = ref([])
const isLoadingRecipes = ref(true)
const recipesError = ref('')

const mostLikedRecipes = ref([])
const isLoadingMostLikedRecipes = ref(true)
const mostLikedRecipesError = ref('')

onMounted(async () => {
  try {
    latestRecipes.value = await fetchLatestRecipes()
  } catch (error) {
    latestRecipesError.value =
      error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isLoadingLatestRecipes.value = false
  }

  await Promise.all([
    (async () => {
      try {
        const result = await getRecipes({ per_page: 4, sort_by: 'random' })
        recipes.value = result.recipes
      } catch (error) {
        recipesError.value = error.message || 'Une erreur inattendue est survenue.'
      } finally {
        isLoadingRecipes.value = false
      }
    })(),
    (async () => {
      try {
        const result = await getRecipes({
          per_page: 4,
          sort_by: 'rating',
          sort_order: 'DESC',
        })
        mostLikedRecipes.value = result.recipes
      } catch (error) {
        mostLikedRecipesError.value = error.message || 'Une erreur inattendue est survenue.'
      } finally {
        isLoadingMostLikedRecipes.value = false
      }
    })(),
  ])
})

</script>

<template>
  <main class="flex-1 px-6 py-8">
    <div class="mx-auto max-w-7xl">
      <section class="mb-5 flex justify-center">
        <SearchBar />
      </section>
      <h1 class="mb-8 text-3xl font-bold text-gray-900">
        Découvrez nos recettes
      </h1>

      <p v-if="isLoadingRecipes">Chargement des recettes...</p>
      <p v-else-if="recipesError" class="text-red-600" role="alert">
        {{ recipesError }}
      </p>
      <p v-else-if="recipes.length === 0">Aucune recette publiée pour le moment.</p>

      <section v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <RecipeCard v-for="recipe in recipes" :key="recipe.id" :recipe="recipe" />
      </section>

      <section class="mt-16">
        <h2 class="mb-8 text-3xl font-bold text-gray-900">
          Les plus appréciées
        </h2>

        <p v-if="isLoadingMostLikedRecipes">Chargement des recettes les plus appréciées...</p>
        <p v-else-if="mostLikedRecipesError" class="text-red-600" role="alert">
          {{ mostLikedRecipesError }}
        </p>
        <p v-else-if="mostLikedRecipes.length === 0">Aucune recette publiée pour le moment.</p>

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <RecipeCard v-for="recipe in mostLikedRecipes" :key="recipe.id" :recipe="recipe" />
        </div>
      </section>

      <section class="mt-16">
        <h2 class="mb-8 text-3xl font-bold text-gray-900">
          Les dernières recettes publiées
        </h2>

        <p v-if="isLoadingLatestRecipes">
          Chargement des dernières recettes...
        </p>

        <p v-else-if="latestRecipesError" class="text-red-600" role="alert">
          {{ latestRecipesError }}
        </p>

        <p v-else-if="latestRecipes.length === 0">
          Aucune recette publiée pour le moment.
        </p>

        <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <RecipeCard v-for="recipe in latestRecipes" :key="recipe.id" :recipe="recipe" />
        </div>
      </section>

    </div>
  </main>
</template>
