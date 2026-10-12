import router from '@/router/index.js'
import { useAuthStore } from '@/authState.js'
import { uploadFileToServer } from '@/services/uploadService.js'

/**
 * @typedef {Object} GenericResponse
 * @property {boolean} success - Indicates if the operation was successful.
 * @property {string} [message] - Success or error message.
 * @property {string} [error] - Error message if applicable.
 */

/**
 * @typedef {Object} RecipeOption
 * @property {number} id - The option ID.
 * @property {string} name - The option name.
 */

/**
 * @typedef {Object} RecipePayload
 * @property {string} title - The recipe title.
 * @property {number} category_id - The ID of the category.
 * @property {string} description - The recipe description.
 * @property {number} cooking_time - The cooking time in minutes.
 * @property {string} difficulty - The difficulty level.
 * @property {string[]} [step_descriptions] - Descriptions for each step.
 * @property {Array<{id: number|null, description: string}>} [steps] - Steps data.
 * @property {Array<{ingredient_id: number, quantity: string}>} ingredients - List of ingredients.
 * @property {number[]} utensil_ids - Array of utensil IDs.
 * @property {number[]} tag_ids - Array of tag IDs.
 */

/**
 * @typedef {Object} RecipeSummary
 * @property {number} id - The recipe ID.
 * @property {string} title - The recipe title.
 * @property {string} description - The recipe description.
 * @property {number|string} cookingTime - The cooking time.
 * @property {number} [likes] - Number of likes.
 * @property {string} [difficulty] - The difficulty level.
 */

/**
 * @typedef {Object} RecipeDetail
 * @property {number} id - The recipe ID.
 * @property {string} title - The recipe title.
 * @property {string} description - The recipe description.
 * @property {number} cookingTime - The cooking time in minutes.
 * @property {string} difficulty - The difficulty level.
 * @property {string|null} imageUrl - The full URL to the recipe's cover image.
 * @property {string} createdAt - Creation date string.
 * @property {RecipeOption} category - The recipe category.
 * @property {{id: number, username: string}} author - The author's basic info.
 * @property {Array<{id: number, stepNumber: number, description: string, imageUrl: string|null}>} steps - The recipe steps.
 * @property {RecipeOption[]} utensils - The recipe utensils.
 * @property {RecipeOption[]} tags - The recipe tags.
 */

/**
 * @typedef {Object} RecipePreview
 * @property {number} id - Recipe unique identifier.
 * @property {string} title - Recipe title.
 * @property {string} description - Short description.
 * @property {string} cookingTime - Cooking time.
 * @property {number} likes - Total number of likes.
 * @property {string} imageUrl - URL of the recipe image.
 */

/**
 * Creates a recipe for the authenticated user.
 * @param {string} token - The user's JWT access token.
 * @param {RecipePayload} recipeData - The recipe fields accepted by the API.
 * @returns {Promise<{success: boolean, id: number, title: string, steps: Array<{id: number, step_number: number}>}>} The newly created recipe data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function createRecipe(token, recipeData) {
  if (!navigator.onLine) {
    throw new Error("Impossible de publier la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de publier la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(recipeData),
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status === 401) {
    const authStore = useAuthStore()
    authStore.clearAuth()
    router.push({ name: 'login' })
    throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de publier la recette.")
  }

  return data
}

/**
 * Uploads the main cover image for a specific recipe.
 * @param {string} token - The user's JWT access token.
 * @param {number|string} recipeId - The ID of the recipe.
 * @param {File} file - The image file.
 * @param {Function} [onProgress] - Callback function receiving the upload percentage.
 * @returns {Promise<{success: boolean, filename: string, image_url: string}>} The server response data.
 */
export function uploadRecipeImage(token, recipeId, file, onProgress) {
  return uploadFileToServer(token, file, `/api/recipes/${encodeURIComponent(recipeId)}/image`, "l'image de la recette", onProgress)
}

/**
 * Uploads an image for a specific recipe step.
 * @param {string} token - The user's JWT access token.
 * @param {number|string} recipeId - The ID of the recipe.
 * @param {number|string} stepId - The ID of the recipe step.
 * @param {File} file - The image file to upload.
 * @param {Function} [onProgress] - Callback function receiving the upload percentage.
 * @returns {Promise<success: boolean, filename: string, image_url: string>} The server response data.
 */
export function uploadRecipeStepImage(token, recipeId, stepId, file, onProgress) {
  return uploadFileToServer(token, file, `/api/recipes/${encodeURIComponent(recipeId)}/steps/${encodeURIComponent(stepId)}/image`, "l'image de l'étape", onProgress)
}

/**
 * Updates an existing recipe.
 * @param {string} token - The user's JWT access token.
 * @param {string|number} id - The ID of the recipe to update.
 * @param {RecipePayload} recipeData - The updated recipe data.
 * @returns {Promise<{success: boolean, id: number, title: string, steps: Array<{id: number, step_number: number}>}>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function updateRecipe(token, id, recipeData) {
  if (!navigator.onLine) {
    throw new Error("Impossible de modifier la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de modifier la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(recipeData),
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status === 401) {
    const authStore = useAuthStore()
    authStore.clearAuth()
    router.push({ name: 'login' })
    throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de modifier la recette.")
  }

  return data
}

/**
 * Deletes the main cover image of a specific recipe.
 * @param {string} token - The user's JWT access token.
 * @param {number|string} recipeId - The ID of the recipe.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function deleteRecipeImage(token, recipeId) {
  if (!navigator.onLine) {
    throw new Error("Impossible de supprimer l'image de la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de supprimer l'image de la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(recipeId)}/image`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status === 401) {
    const authStore = useAuthStore()
    authStore.clearAuth()
    router.push({ name: 'login' })
    throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
  }

  if (response.status === 403) {
    throw new Error("Accès refusé. Tu ne peux modifier que tes propres recettes.")
  }

  if (response.status === 404) {
    throw new Error("Recette ou image de la recette introuvable.")
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(
      data.error ||
      "Impossible de supprimer l'image de la recette.",
    )
  }

  return data
}

/**
 * Deletes the image of a specific recipe step.
 * @param {string} token - The user's JWT access token.
 * @param {number|string} recipeId - The ID of the recipe.
 * @param {number|string} stepId - The ID of the recipe step.
 * @returns {Promise<GenericResponse>} The server response data.
 * @throws {Error} If the request fails, the user is unauthorized, or a network error occurs.
 */
export async function deleteRecipeStepImage(token, recipeId, stepId) {
  if (!navigator.onLine) {
    throw new Error("Impossible de supprimer l'image de l'étape : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de supprimer l'image de l'étape : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''
  const endpoint = `/api/recipes/${encodeURIComponent(recipeId)}/steps/${encodeURIComponent(stepId)}/image`

  let response
  try {
    response = await fetch(`${baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status === 401) {
    const authStore = useAuthStore()
    authStore.clearAuth()
    router.push({ name: 'login' })
    throw new Error("Votre session a expiré. Veuillez vous reconnecter.")
  }

  if (response.status === 403) {
    throw new Error("Accès refusé. Tu ne peux modifier que tes propres recettes.")
  }

  if (response.status === 404) {
    throw new Error("Recette, étape ou image de l'étape introuvable.")
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de supprimer l'image de l'étape.")
  }

  return data
}

/**
 * Fetches recipes, optionally filtered by a search term.
 * @param {string} [search=''] - The search query.
 * @returns {Promise<RecipeSummary[]>} The list of recipes.
 * @throws {Error} If the request fails or a network error occurs.
 */
export async function getRecipes(search = '') {
  if (!navigator.onLine) {
    throw new Error("Impossible de récupérer les recettes : vous êtes hors ligne.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  const params = new URLSearchParams()

  if (search.trim()) {
    params.append('search', search.trim())
  }

  const queryString = params.toString()

  const url = queryString
    ? `${baseUrl}/api/recipes?${queryString}`
    : `${baseUrl}/api/recipes`

  let response
  try {
    response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de récupérer les recettes.")
  }



  return (data.recipes || []).map((recipe) => ({
    id: recipe.id,
    title: recipe.title,
    description: recipe.description,
    cookingTime: recipe.cooking_time,
    difficulty: recipe.difficulty,
    imageUrl: getRecipeImageUrl(recipe.image_url),
    likes: recipe.likes,
  }))
}

/**
 * Fetches the latest recipes from the server.
 * @returns {Promise<RecipeSummary[]>} The list of the latest recipes.
 * @throws {Error} If the request fails or a network error occurs.
 */
export async function fetchLatestRecipes() {
  if (!navigator.onLine) {
    throw new Error("Impossible de récupérer les dernières recettes : vous êtes hors ligne.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/latest`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de récupérer les dernières recettes.")
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

/**
 * Fetches a specific recipe by its ID.
 * @param {string|number} id - The ID of the recipe.
 * @returns {Promise<RecipeDetail>} The detailed recipe data.
 * @throws {Error} If the request fails or a network error occurs.
 */
export async function fetchRecipeById(id) {
  if (!navigator.onLine) {
    throw new Error("Impossible de récupérer la recette : vous êtes hors ligne.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(id)}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status === 404) {
    throw new Error("Recette introuvable.")
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || "Impossible de récupérer la recette.")
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
    categoryId: recipe.category ? recipe.category.id : '',
    author: recipe.author,
    steps: recipe.steps.map((step) => ({
      id: step.id,
      stepNumber: step.step_number,
      description: step.description,
      imageUrl: getRecipeImageUrl(step.image_url),
    })),
    ingredients: recipe.ingredients.map((ingredient, index) => ({
      id: index + 1,
      ingredientId: ingredient.id,
      name: ingredient.name,
      quantity: ingredient.quantity,
    })),
    utensils: recipe.utensils.map((utensil, index) => ({
      id: index + 1,
      utensilId: utensil.id,
      name: utensil.name,
    })),
    tags: recipe.tags.map((tag, index) => ({
      id: index + 1,
      tagId: tag.id,
      name: tag.name,
    })),
  }
}

/**
 * Fetches the recipe categories available in the database.
 * @returns {Promise<RecipeOption[]>} The categories.
 * @throws {Error} If the request fails or a network error occurs.
 */
export async function fetchCategories() {
  return fetchRecipeOptions(
    'recipes/categories',
    'categories',
    'Impossible de récupérer les catégories.',
  )
}

/**
 * Fetches the list of available ingredients.
 * @returns {Promise<RecipeOption[]>} The list of ingredients.
 */
export function fetchIngredients() {
  return fetchRecipeOptions(
    'recipes/ingredients',
    'ingredients',
    'Impossible de récupérer les ingrédients.',
  )
}

/**
 * Fetches the list of available utensils.
 * @returns {Promise<RecipeOption[]>} The list of utensils.
 */
export function fetchUtensils() {
  return fetchRecipeOptions(
    'recipes/utensils',
    'utensils',
    'Impossible de récupérer les ustensiles.',
  )
}

/**
 * Fetches the list of available tags.
 * @returns {Promise<RecipeOption[]>} The list of tags.
 */
export function fetchTags() {
  return fetchRecipeOptions(
    'recipes/tags',
    'tags',
    'Impossible de récupérer les tags.',
  )
}

/**
 * Generic helper function to fetch recipe options from the server.
 * @param {string} endpoint - the API endpoint suffix.
 * @param {string} key - The data key to extract from the JSON response.
 * @param {string} errorMessage - The fallback error message.
 * @returns {Promise<RecipeOption[]>} The fetched options list.
 * @throws {Error} If the request fails or a network error occurs.
 */
async function fetchRecipeOptions(endpoint, key, errorMessage) {
  if (!navigator.onLine) {
    throw new Error(`${errorMessage.replace(/\.$/, '')} : vous êtes hors ligne.`)
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/${endpoint}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })
  } catch (error) {
    throw new Error("Impossible de contacter le serveur. Vérifiez votre connexion internet.", { cause: error })
  }

  if (response.status >= 500) {
    throw new Error("Erreur interne du serveur. Veuillez réessayer.")
  }

  let data
  try {
    data = await response.json()
  } catch (error) {
    throw new Error("Erreur de communication avec le serveur. Veuillez réessayer plus tard.", { cause: error })
  }

  if (!response.ok || data.success === false) {
    throw new Error(data.error || errorMessage)
  }

  return data[key] || []
}

/**
 * Builds the full URL for a recipe image.
 * @param {string} imagePath - The partial path of the image.
 * @returns {string|null} The full image URL or null
 */
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
  const baseUrl = import.meta.env.VITE_API_URL || ''
  const cleanBaseUrl = baseUrl.replace(/\/$/, '')

  return `${cleanBaseUrl}${imagePath}`
}