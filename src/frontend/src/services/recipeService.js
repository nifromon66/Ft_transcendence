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
    imageUrl: recipe.image_url,
    likes: recipe.likes,
  }))
}
