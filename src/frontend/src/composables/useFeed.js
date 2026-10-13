import { ref, computed, onMounted } from 'vue'

import { fetchLatestRecipes } from '@/services/recipeService.js'

import tartePommeImage from '@/assets/temp_assets/DSC01764.jpg'
import carboImage from '@/assets/temp_assets/carbonara-e1521461363147-1024x670.jpg'
import soupeLegumeImage from '@/assets/temp_assets/Soupe_jardiniere_aux_legumes.png.1200x627_q64.jpg'
import soupePoissonImage from '@/assets/temp_assets/poissonsoupe.jpg'

/**
 * @typedef {import('@/services/recipeService.js').RecipePreview} RecipePreview
 */

/**
 * Composable to manage the recipe feed data.
 * @returns {Object} Feed state and computed properties.
 */
export function useFeed() {
    /** @type {RecipePreview[]} */
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

    const isLoading = ref(true)
    const errorMessage = ref('')

    onMounted(async () => {
        try {
            latestRecipes.value = await fetchLatestRecipes()
        } catch (error) {
            errorMessage.value = error.message || 'Une erreur inattendue est survenue.'
        } finally {
            isLoading.value = false
        }
    })

    return {
        recipes,
        mostLikedRecipes,
        latestRecipes,
        isLoading,
        errorMessage
    }
}