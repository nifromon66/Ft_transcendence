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

        tags: initialRecipe.tags.map((tag) => ({
            ...tag,
        })),
    }
}

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

        tag_ids: recipe.tags.map((tag) => Number(tag.tagId)),
    }

    const stepImageChanges = recipe.steps.map((step) => ({
        persistedId: step.persistedId ?? null,
        file: step.imageFile,
        shouldDelete: step.shouldDeleteImage,
    }))

    return { recipeData, stepImageChanges }
}
