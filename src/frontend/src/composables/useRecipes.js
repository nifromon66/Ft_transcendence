import { ref } from 'vue'
import { getRecipes } from '@/services/recipeService'

export function useRecipes() {
  const recipes = ref([])

  const loading = ref(false)

  const error = ref(null)

  async function loadRecipes(search = '') {
    loading.value = true
    error.value = null

    try {
      recipes.value = await getRecipes(search)
    } catch (err) {
      console.error('Failed to load recipes:', err)

      error.value = 'Impossible de charger les recettes.'
    } finally {
      loading.value = false
    }
  }

  return {
    recipes,
    loading,
    error,
    loadRecipes,
  }
}
