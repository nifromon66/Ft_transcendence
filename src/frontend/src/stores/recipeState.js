import { defineStore } from 'pinia'

import * as recipeService from '@/services/recipeService.js'

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
                const result = await recipeService.getRecipes(search)
                this.recipes = Array.isArray(result) ? result : (result?.recipes || [])
            } catch (error) {
                console.error('Failed to load recipes:', error)
                this.errorMessage = error.message || 'Impossible de charger les recettes.'
                this.recipes = []
            } finally {
                this.isLoading = false
            }
        }
    }
})