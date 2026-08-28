<script setup>

  import RecipeCard from '@/components/RecipeCard.vue'
  import { computed, onMounted, ref } from 'vue'
  import { fetchLatestRecipes } from '@/services/recipeService'

  import tartePommeImage from '../assets/temp_assets/DSC01764.jpg'
  import carboImage from '../assets/temp_assets/carbonara-e1521461363147-1024x670.jpg'
  import soupeLegumeImage from '../assets/temp_assets/Soupe_jardiniere_aux_legumes.png.1200x627_q64.jpg'
  import soupePoissonImage from '../assets/temp_assets/poissonsoupe.jpg'
  const recipes = [
    {
      id: 1,
      title: 'Tarte aux pommes',
      description: 'Une tarte simple et rapide à préparer.',
      cookingTime: '45 min',
      likes: 12,
      imageUrl: tartePommeImage,
    },
    {
      id: 2,
      title: 'Pâtes carbonara',
      description: 'Une recette italienne généreuse.',
      cookingTime: '25 min',
      likes: 34,
      imageUrl: carboImage,
    },
    {
      id: 3,
      title: 'Soupe de légumes',
      description: 'Une soupe maison avec des légumes de saison.',
      cookingTime: '40 min',
      likes: 22,
      imageUrl: soupeLegumeImage,
    },
    {
      id: 4,
      title: 'Soupe de poisson',
      description: 'Une soupe maison.',
      cookingTime: '1 heure',
      likes: 9,
      imageUrl: soupePoissonImage,
    },
  ]

  const mostLikedRecipes = computed(() => {
    return [...recipes]
      .sort((firstRecipe, secondRecipe) => secondRecipe.likes - firstRecipe.likes)
      .slice(0, 4)
  })

  const latestRecipes = ref([])
  const isLoadingLatestRecipes = ref(true)
  const latestRecipesError = ref('')

  onMounted(async () => {
    try {
      latestRecipes.value = await fetchLatestRecipes()
    } catch (error) {
      latestRecipesError.value =
        error.message || 'Une erreur inattendue est survenue.'
    } finally {
      isLoadingLatestRecipes.value = false
    }
  })

</script>

<template>
  <main class="flex-1 px-6 py-8">
    <div class="mx-auto max-w-7xl">
      <h1 class="mb-8 text-3xl font-bold text-gray-900">
        Découvrez nos recettes
      </h1>

      <section class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <RecipeCard
          v-for="recipe in recipes"
          :key="recipe.id"
          :recipe="recipe"
        />
      </section>

      <section class="mt-16">
        <h2 class="mb-8 text-3xl font-bold text-gray-900">
          Les plus appréciées
        </h2>

        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <RecipeCard
            v-for="recipe in mostLikedRecipes"
            :key="recipe.id"
            :recipe="recipe"
          />
        </div>
      </section>

      <section class="mt-16">
        <h2 class="mb-8 text-3xl font-bold text-gray-900">
          Les dernières recettes publiées
        </h2>

        <p v-if="isLoadingLatestRecipes">
          Chargement des dernières recettes...
        </p>

        <p
          v-else-if="latestRecipesError"
          class="text-red-600"
          role="alert"
        >
          {{ latestRecipesError }}
        </p>

        <p v-else-if="latestRecipes.length === 0">
          Aucune recette publiée pour le moment.
        </p>

        <div
          v-else
          class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
        >
          <RecipeCard
            v-for="recipe in latestRecipes"
            :key="recipe.id"
            :recipe="recipe"
          />
        </div>
      </section>

    </div>
  </main>
</template>