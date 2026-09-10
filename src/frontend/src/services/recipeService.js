
async function fetchRecipeOptions(endpoint, key, errorMessage) {
  const response = await fetch(`/api/${endpoint}`)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.error || errorMessage)
  }

  return data[key]
}

export function fetchIngredients() {
  return fetchRecipeOptions(
    'ingredients',
    'ingredients',
    'Impossible de récupérer les ingrédients.',
  )
}

export function fetchUtensils() {
  return fetchRecipeOptions(
    'utensils',
    'utensils',
    'Impossible de récupérer les ustensiles.',
  )
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
    likes: recipe.likes,
  }))
}

export async function fetchRecipeById(id) {
  const response = await fetch(
    `/api/recipes/${encodeURIComponent(id)}`
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
    utensils: recipe.utensils.map((utensil) => ({
      id: utensil.id,
      name: utensil.name,
    })),
    tags: recipe.tags.map((tag) => ({
      id: tag.id,
      name: tag.name,
    })),
  }
}


