import { reactive, ref } from 'vue'
import { createFormRecipe } from '@/utils/recipeMapper.js'
import { validateRecipeImage } from '@/utils/fileValidators.js'

export function useRecipeForm(initialRecipe) {
    const recipe = reactive(createFormRecipe(initialRecipe))

    const errorMessage = ref('')

    const recipeImageFile = ref(null)

    const existingRecipeImageUrl = ref(initialRecipe?.imageUrl || null)

    const shouldDeleteRecipeImage = ref(false)
    const showRecipeImageDropZone = ref(false)

    let nextStepId = Math.max(0, ...recipe.steps.map((step) => Number(step.id))) + 1
    let nextIngredientId = Math.max(0, ...recipe.ingredients.map((ingredient) => Number(ingredient.id))) + 1
    let nextTagId = Math.max(0, ...recipe.tags.map((tag) => Number(tag.id))) + 1

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

    const removeExistingRecipeImage = () => {
        existingRecipeImageUrl.value = null
        shouldDeleteRecipeImage.value = true
    }

    const clearRecipeImage = () => {
        recipeImageFile.value = null
        showRecipeImageDropZone.value = false
    }

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

    const removeStep = (index) => {
        if (recipe.steps.length > 1) {
            recipe.steps.splice(index, 1)
        }
    }

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

    const clearStepImage = (step) => {
        step.imageFile = null
        step.showImageDropZone = false
    }

    const removeExistingStepImage = (step) => {
        step.imageUrl = null
        step.shouldDeleteImage = true
    }

    const addIngredient = () => {
        recipe.ingredients.push({ id: nextIngredientId, categoryId: '', ingredientId: '', quantity: '' })
        nextIngredientId += 1
    }

    const removeIngredient = (index) => {
        recipe.ingredients.splice(index, 1)
    }

    const isIngredientSelected = (ingredientId, currentIndex) => {
        return recipe.ingredients.some((ingredient, index) => {
            return (
                index !== currentIndex &&
                String(ingredient.ingredientId) === String(ingredientId)
            )
        })
    }

    const addTag = () => {
        recipe.tags.push({
            id: nextTagId,
            tagId: '',
        })
        nextTagId += 1
    }

    const removeTag = (index) => {
        if (recipe.tags.length > 1) {
            recipe.tags.splice(index, 1)
        }
    }

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
