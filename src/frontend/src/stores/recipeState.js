import { defineStore } from 'pinia'

import * as recipeService from '@/services/recipeService.js'

/**
 * 
 * @typedef {import('@/services/recipeService').Recipe} Recipe
 */

export const useRecipeStore = defineStore('recipe', {
    state: () => ({
        /** @type {Recipe[]} */
        recipes: [],
        /** @type {boolean} */
        isLoading: false,
        /** @type {string | null} */
        errorMessage: null
    }),

    actions: {
        /**
         * Loads recipes from the API, optionally filtered by a search query.
         * @param {string} search - The search query (empty by default)
         */
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