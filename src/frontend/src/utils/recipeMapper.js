/**
 * @typedef {Object} InitialStep
 * @property {number} [id]
 * @property {number} [persistedId]
 * @property {string} [description]
 * @property {string|null} [imageUrl]
 */

/**
 * @typedef {Object} InitialIngredient
 * @property {number} [id]
 * @property {string|number} ingredientId
 * @property {string} [quantity]
 */

/**
 * @typedef {Object} InitialUtensil
 * @property {number} [id]
 * @property {string|number} utensilId
 */

/**
 * @typedef {Object} InitialTag
 * @property {number} [id]
 * @property {string|number} tagId
 */

/**
 * @typedef {Object} InitialRecipe
 * @property {string} title
 * @property {string|number} categoryId
 * @property {string} [description]
 * @property {number|string|null} [cookingTime]
 * @property {string} [difficulty]
 * @property {InitialStep[]} steps
 * @property {InitialIngredient[]} ingredients
 * @property {InitialUtensil[]} utensils
 * @property {InitialTag[]} tags
 */

/**
 * @typedef {Object} FormStep
 * @property {number} id
 * @property {number} [persistedId]
 * @property {string} description
 * @property {string|null} imageUrl
 * @property {File|null} imageFile
 * @property {boolean} shouldDeleteImage
 * @property {boolean} showImageDropZone
 */

/**
 * @typedef {Object} FormIngredient
 * @property {number} id
 * @property {string|number} ingredientId
 * @property {string} quantity
 */

/**
 * @typedef {Object} FormRecipe
 * @property {string} title
 * @property {string|number} categoryId
 * @property {string} description
 * @property {number|string|null} cookingTime
 * @property {string} difficulty
 * @property {FormStep[]} steps
 * @property {FormIngredient[]} ingredients
 * @property {Array<{id: number, utensilId: string|number}>} utensils
 * @property {Array<{id: number, tagId: string|number}>} tags
 */

/**
 * Creates the initial state for the recipe form.
 * @param {InitialRecipe|null} initialRecipe
 * @returns {FormRecipe}
 */
export const createFormRecipe = (initialRecipe) => {
    if (!initialRecipe) {
        return {
            title: '',
            categoryId: '',
            description: '',
            cookingTime: null,
            difficulty: '',
            steps: [
                {
                    id: 1,
                    description: '',
                    imageUrl: null,
                    imageFile: null,
                    shouldDeleteImage: false,
                    showImageDropZone: false,
                },
            ],
            ingredients: [
                {
                    id: 1,
                    ingredientId: '',
                    quantity: '',
                },
            ],
            utensils: [
                {
                    id: 1,
                    utensilId: '',
                },
            ],
            tags: [
                {
                    id: 1,
                    tagId: '',
                },
            ],
        }
    }

    return {
        title: initialRecipe.title,
        categoryId: initialRecipe.categoryId,
        description: initialRecipe.description || '',
        cookingTime: initialRecipe.cookingTime,
        difficulty: initialRecipe.difficulty || '',

        steps: initialRecipe.steps.map((step) => ({
            ...step,
            persistedId: step.id,
            imageUrl: step.imageUrl || null,
            imageFile: null,
            shouldDeleteImage: false,
            showImageDropZone: false,
        })),

        ingredients: initialRecipe.ingredients.map((ingredient) => ({
            ...ingredient,
            categoryId: ingredient.categoryId ?? '',
        })),

        utensils: initialRecipe.utensils.map((utensil) => ({
            ...utensil,
        })),

        tags: initialRecipe.tags.map((tag) => ({
            ...tag,
        })),
    }
}

/**
 * Formats the reactive recipe state for the API payload.
 * @param {FormRecipe} recipe
 * @returns {{ recipeData: Object, stepImageChanges: Array<{persistedId: number|null, file: File|null, shouldDelete: boolean}> }}
 */
export const formatRecipeForApi = (recipe) => {
    const recipeData = {
        title: recipe.title,
        category_id: recipe.categoryId === '' ? null : Number(recipe.categoryId),
        description: recipe.description || null,
        cooking_time: recipe.cookingTime === '' || recipe.cookingTime === null ? null : Number(recipe.cookingTime),
        difficulty: recipe.difficulty || null,

        steps: recipe.steps.map((step) => ({
            id: step.persistedId ?? null,
            description: step.description.trim(),
        })),

        ingredients: recipe.ingredients.map((ingredient) => ({
            ingredient_id: Number(ingredient.ingredientId),
            quantity: ingredient.quantity.trim() || null,
        })),

        utensil_ids: recipe.utensils.map((utensil) => Number(utensil.utensilId)),

        tag_ids: recipe.tags.map((tag) => Number(tag.tagId)),
    }

    const stepImageChanges = recipe.steps.map((step) => ({
        persistedId: step.persistedId ?? null,
        file: step.imageFile,
        shouldDelete: step.shouldDeleteImage,
    }))

    return { recipeData, stepImageChanges }
}