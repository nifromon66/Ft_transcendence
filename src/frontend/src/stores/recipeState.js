import { defineStore } from 'pinia'
import { getRecipes } from '@/services/recipeService.js'

export const useRecipeStore = defineStore('recipe', {
    state: () => ({
        recipes: [],
        isLoading: false,
        errorMessage: null
    }),

    actions: {
        async loadRecipes(search = '') {
            this.isLoading = true
            this.errorMessage = null

            try {
                const result = await getRecipes(search)
                this.recipes = Array.isArray(result) ? result : (result?.recipes || [])
            } catch (error) {
                this.errorMessage = error.message || 'Impossible de charger les recettes.'
                this.recipes = []
            } finally {
                this.isLoading = false
            }
        }
    }
})
