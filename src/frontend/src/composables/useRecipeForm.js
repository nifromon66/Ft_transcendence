import { reactive, ref } from 'vue'
import { createFormRecipe } from '@/utils/recipeMapper.js'
import { validateRecipeImage } from '@/utils/fileValidators.js'

/**
 * @typedef {import('@/utils/recipeMapper.js').InitialRecipe} InitialRecipe
 * @typedef {import('@/utils/recipeMapper.js').FormRecipe} FormRecipe
 * @typedef {import('@/utils/recipeMapper.js').FormStep} FormStep
 */

/**
 * @param {InitialRecipe|null} initialRecipe
 */
export function useRecipeForm(initialRecipe) {
    const recipe = reactive(createFormRecipe(initialRecipe))

    const errorMessage = ref('')

    /** @type {import('vue').Ref<File | null>} */
    const recipeImageFile = ref(null)

    /** @type {import('vue').Ref<string | null>} */
    const existingRecipeImageUrl = ref(initialRecipe?.imageUrl || null)

    const shouldDeleteRecipeImage = ref(false)
    const showRecipeImageDropZone = ref(false)

    let nextStepId = Math.max(0, ...recipe.steps.map((step) => Number(step.id))) + 1
    let nextIngredientId = Math.max(0, ...recipe.ingredients.map((ingredient) => Number(ingredient.id))) + 1
    let nextTagId = Math.max(0, ...recipe.tags.map((tag) => Number(tag.id))) + 1

    /**
     * @param {File} file 
     * @returns {void}
     */
    const handleRecipeImage = (file) => {
        const { isValid, error } = validateRecipeImage(file)
        if (!isValid) {
            errorMessage.value = error
            return
        }
        errorMessage.value = ''
        recipeImageFile.value = file
        shouldDeleteRecipeImage.value = false
    }

    /**
     * @returns {void}
     */
    const removeExistingRecipeImage = () => {
        existingRecipeImageUrl.value = null
        shouldDeleteRecipeImage.value = true
    }

    /**
     * @returns {void}
     */
    const clearRecipeImage = () => {
        recipeImageFile.value = null
        showRecipeImageDropZone.value = false
    }

    /**
     * @returns {void}
     */
    const addStep = () => {
        recipe.steps.push({
            id: nextStepId,
            description: '',
            imageUrl: null,
            imageFile: null,
            shouldDeleteImage: false,
            showImageDropZone: false,
        })

        nextStepId += 1
    }

    /**
     * @param {number} index
     * @returns {void}
     */
    const removeStep = (index) => {
        if (recipe.steps.length > 1) {
            recipe.steps.splice(index, 1)
        }
    }

    /**
     * @param {FormStep} step
     * @param {File} file
     * @returns {void}
     */
    const handleStepImage = (step, file) => {
        const { isValid, error } = validateRecipeImage(file)
        if (!isValid) {
            errorMessage.value = error
            return
        }
        errorMessage.value = ''
        step.imageFile = file
        step.shouldDeleteImage = false
    }

    /**
     * @param {FromStep} step
     * @returns {void}
     */
    const clearStepImage = (step) => {
        step.imageFile = null
        step.showImageDropZone = false
    }

    /**
     * @param {FormStep} step
     * @returns {void} 
     */
    const removeExistingStepImage = (step) => {
        step.imageUrl = null
        step.shouldDeleteImage = true
    }

    /**
     * @returns {void}
     */
    const addIngredient = () => {
        recipe.ingredients.push({ id: nextIngredientId, categoryId: '', ingredientId: '', quantity: '' })
        nextIngredientId += 1
    }

    /**
     * @param {number} index
     * @returns {void}
     */
    const removeIngredient = (index) => {
        recipe.ingredients.splice(index, 1)
    }

    /**
     * @param {string|number} ingredientId 
     * @param {number} currentIndex 
     * @returns {boolean}
     */
    const isIngredientSelected = (ingredientId, currentIndex) => {
        return recipe.ingredients.some((ingredient, index) => {
            return (
                index !== currentIndex &&
                String(ingredient.ingredientId) === String(ingredientId)
            )
        })
    }

    /**
     * @returns {void}
     */
    const addTag = () => {
        recipe.tags.push({
            id: nextTagId,
            tagId: '',
        })
        nextTagId += 1
    }

    /**
     * @param {number} index 
     * @returns {void}
     */
    const removeTag = (index) => {
        if (recipe.tags.length > 1) {
            recipe.tags.splice(index, 1)
        }
    }

    /**
     * @param {string|number} tagId
     * @param {number} currentIndex
     * @returns {boolean}
     */
    const isTagSelected = (tagId, currentIndex) => {
        return recipe.tags.some((tag, index) =>
            index !== currentIndex &&
            String(tag.tagId) === String(tagId)
        )
    }

    return {
        recipe,
        errorMessage,
        recipeImageFile,
        existingRecipeImageUrl,
        shouldDeleteRecipeImage,
        showRecipeImageDropZone,
        handleRecipeImage,
        removeExistingRecipeImage,
        clearRecipeImage,
        addStep,
        removeStep,
        handleStepImage,
        clearStepImage,
        removeExistingStepImage,
        addIngredient,
        removeIngredient,
        isIngredientSelected,
        addTag,
        removeTag,
        isTagSelected
    }
}
