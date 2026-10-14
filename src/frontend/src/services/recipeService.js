import { useAuthStore } from '@/authState'

async function fetchRecipeOptions(endpoint, key, errorMessage) {
  const response = await fetch(`/api/${endpoint}`)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || errorMessage)
  }

  return data[key]
}

export function fetchIngredientCategories() {
  return fetchRecipeOptions(
    'ingredient-categories',
    'ingredient_categories',
    'Impossible de récupérer les catégories d’ingrédients.',
  )
}

export function fetchIngredients() {
  return fetchRecipeOptions(
    'ingredients',
    'ingredients',
    'Impossible de récupérer les ingrédients.',
  )
}

export async function createIngredient(token, ingredientData) {
  const response = await fetch('/api/ingredients', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(ingredientData),
  })
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error || data.msg || 'Impossible de créer l’ingrédient.')
  }
  return data.ingredient
}

export function fetchTags() {
  return fetchRecipeOptions(
    'tags',
    'tags',
    'Impossible de récupérer les tags.',
  )
}

/**
 * Fetches the recipe categories available in the database.
 * @returns {Promise<Array<{ id: number, name: string }>>} The categories.
 * @throws {Error} If the request fails.
 */
export async function fetchCategories() {
  const response = await fetch('/api/categories')
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || 'Impossible de récupérer les catégories.')
  }

  return data.categories
}

function getRecipeImageUrl(imagePath) {
  if (!imagePath) {
    return null
  }

  if (
    imagePath.startsWith('/') ||
    imagePath.startsWith('http://') ||
    imagePath.startsWith('https://')
  ) {
    return imagePath
  }

  const encodedPath = imagePath
    .split('/')
    .map((part) => encodeURIComponent(part))
    .join('/')

  return `/api/uploads/${encodedPath}`
}

/**
 * Creates a recipe for the authenticated user.
 * @param {string} token - The user's JWT access token.
 * @param {Object} recipeData - The recipe fields accepted by the API.
 * @returns {Promise<Object>} The newly created recipe data.
 * @throws {Error} If the request fails.
 */
export async function createRecipe(token, recipeData) {
  const response = await fetch('/api/recipes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(recipeData),
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || data.msg || 'Impossible de publier la recette.')
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function updateRecipe(token, id, recipeData) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(id)}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(recipeData),
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error ||
      data.msg ||
      'Impossible de modifier la recette.'
    )
  }

  return data
}

export async function deleteRecipe(token, id) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(id)}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error ||
      data.msg ||
      'Impossible de supprimer la recette.'
    )
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function fetchLatestRecipes() {
  const response = await fetch('/api/recipes/latest')
  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || 'Impossible de récupérer les dernières recettes.'
    )
  }

  return data.recipes.map((recipe) => ({
    id: recipe.id,
    title: recipe.title,
    description: recipe.description,
    cookingTime:
      recipe.cooking_time !== null
        ? `${recipe.cooking_time} min`
        : 'Non renseigné',
    imageUrl: getRecipeImageUrl(recipe.image_url),
    rating: recipe.rating,
  }))
}

export async function fetchRecipeById(id, token = null) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(id)}`,
    {
      headers: token
        ? { Authorization: `Bearer ${token}` }
        : {},
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || 'Impossible de récupérer la recette.'
    )
  }

  const recipe = data.recipe

  return {
    id: recipe.id,
    myRating: recipe.my_rating,
    rating: recipe.rating,
    title: recipe.title,
    description: recipe.description,
    cookingTime: recipe.cooking_time,
    difficulty: recipe.difficulty,
    imageUrl: getRecipeImageUrl(recipe.image_url),
    createdAt: recipe.created_at,
    category: recipe.category,
    author: recipe.author,
    steps: recipe.steps.map((step) => ({
      id: step.id,
      stepNumber: step.step_number,
      description: step.description,
      imageUrl: getRecipeImageUrl(step.image_url),
    })),
    ingredients: recipe.ingredients.map((ingredient) => ({
      id: ingredient.id,
      name: ingredient.name,
      quantity: ingredient.quantity,
    })),
    tags: recipe.tags.map((tag) => ({
      id: tag.id,
      name: tag.name,
    })),
  }
}


/**
 * getRecipes
 *
 * @param {string} search
 * @returns {Promise<Array>}
 */
export async function getRecipes(search = '') {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.append('search', search.trim())
  }

  const queryString = params.toString()

  const url = queryString
    ? `/api/recipes?${queryString}`
    : '/api/recipes'

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch recipes: ${response.status}`)
  }

  const data = await response.json()
console.log('API response:', data)
console.log('Recipe IDs:', data.recipes.map(recipe => recipe.id))
  return data.recipes
}


export async function rateRecipe(token, recipeId, score) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(recipeId)}/ratings`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ score }),
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || data.msg || 'Impossible de noter la recette.',
    )
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function deleteRecipeRating(token, recipeId) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(recipeId)}/ratings`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || data.msg || 'Impossible de supprimer la note.',
    )
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function updateRecipeRating(token, recipeId, score) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(recipeId)}/ratings`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ score }),
    },
  )

  const data = await response.json()

  if (!response.ok) {
    throw new Error(
      data.error || data.msg || 'Impossible de modifier la note.',
    )
  }

  return data
}
