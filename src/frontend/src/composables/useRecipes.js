import { ref } from 'vue'
import { getRecipes } from '@/services/recipeService'

export function useRecipes() {
  const total = ref(0)

  const recipes = ref([])

  const loading = ref(false)

  const error = ref(null)

  async function loadRecipes(filters = []) {
    loading.value = true
    error.value = null

    try {
      const data = await getRecipes(filters)
      recipes.value = data.recipes
      total.value = data.total
    } catch {
      error.value = 'Impossible de charger les recettes.'
    } finally {
      loading.value = false
    }
  }

  return {
    recipes,
    loading,
    error,
    total,
    loadRecipes,
  }
}
