import router from '@/router/index.js'
import { useAuthStore } from '@/stores/authState.js'
import { uploadFileToServer } from '@/services/uploadService.js'

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

  await useAuthStore().refreshRewards()
  return data
}

export function uploadRecipeImage(token, recipeId, file, onProgress) {
  return uploadFileToServer(token, file, `/api/recipes/${encodeURIComponent(recipeId)}/image`, "l'image de la recette", onProgress)
}

export function uploadRecipeStepImage(token, recipeId, stepId, file, onProgress) {
  return uploadFileToServer(token, file, `/api/recipes/${encodeURIComponent(recipeId)}/steps/${encodeURIComponent(stepId)}/image`, "l'image de l'étape", onProgress)
}

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

export async function deleteRecipe(token, id) {
  if (!navigator.onLine) {
    throw new Error("Impossible de supprimer la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de supprimer la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(id)}`, {
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
    throw new Error("Accès refusé. Tu ne peux supprimer que ta propre recette.")
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
      "Impossible de supprimer la recette.",
    )
  }

  await useAuthStore().refreshRewards()
  return data
}

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

export async function getRecipes(filters = {}) {
  if (!navigator.onLine) {
    throw new Error("Impossible de récupérer les recettes : vous êtes hors ligne.")
  }

  const opts = typeof filters === 'string' ? { search: filters } : (filters || {})
  const baseUrl = import.meta.env.VITE_API_URL || ''

  const params = new URLSearchParams()

  if (opts.search?.trim()) {
    params.set('search', opts.search.trim())
  }

  if (opts.category) {
    params.set('category', opts.category)
  }

  if (opts.difficulty) {
    params.set('difficulty', opts.difficulty)
  }

  if (opts.page) {
    params.set('page', String(opts.page))
  }

  if (opts.per_page) {
    params.set('per_page', String(opts.per_page))
  }

  if (opts.sort_by) {
    params.set('sort_by', opts.sort_by)
  }

  if (opts.sort_order) {
    params.set('sort_order', opts.sort_order)
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

  const mappedRecipes = (data.recipes || []).map((recipe) => ({
    id: recipe.id,
    title: recipe.title,
    description: recipe.description,
    cookingTime:
      recipe.cooking_time !== null && recipe.cooking_time !== undefined
        ? `${recipe.cooking_time} min`
        : 'Non renseigné',
    difficulty: recipe.difficulty,
    imageUrl: getRecipeImageUrl(recipe.image_url),
    rating: recipe.rating ?? null,
    category: recipe.category,
    author: recipe.author,
  }))

  return {
    recipes: mappedRecipes,
    total: typeof data.total === 'number' ? data.total : mappedRecipes.length,
    page: data.page || 1,
    perPage: data.per_page || 20,
  }
}

export function fetchDifficulties() {
  return [
    { value: 'facile', label: 'Facile' },
    { value: 'moyen', label: 'Moyen' },
    { value: 'difficile', label: 'Difficile' },
  ]
}

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
    rating: recipe.rating,
  }))
}

export async function fetchRecipeById(id, token = null) {
  if (!navigator.onLine) {
    throw new Error("Impossible de récupérer la recette : vous êtes hors ligne.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(id)}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
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
    myRating: recipe.my_rating,
    rating: recipe.rating,
    title: recipe.title,
    description: recipe.description,
    cookingTime: recipe.cooking_time,
    difficulty: recipe.difficulty,
    imageUrl: getRecipeImageUrl(recipe.image_url),
    createdAt: recipe.created_at,
    category: recipe.category,
    categoryId: (recipe.category && recipe.category.id) ? recipe.category.id : (recipe.category_id || ''),
    author: recipe.author,
    steps: recipe.steps.map((step) => ({
      id: step.id,
      stepNumber: step.step_number,
      description: step.description,
      imageUrl: getRecipeImageUrl(step.image_url),
    })),
    ingredients: recipe.ingredients.map((ingredient, index) => ({
      id: index + 1,
      ingredientId: ingredient.ingredient_id || ingredient.id,
      categoryId: ingredient.category_id || '',
      name: ingredient.name,
      quantity: ingredient.quantity,
    })),
    tags: recipe.tags.map((tag, index) => ({
      id: index + 1,
      tagId: tag.id,
      name: tag.name,
    })),
  }
}

export async function rateRecipe(token, recipeId, score) {
  if (score < 1 || score > 5) {
    throw new Error("La note doit être comprise entre 1 et 5.")
  }

  if (!navigator.onLine) {
    throw new Error("Impossible de noter la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de noter la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(recipeId)}/ratings`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ score }),
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
    throw new Error(data.error || "Impossible de noter la recette.")
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function deleteRecipeRating(token, recipeId) {
  if (!navigator.onLine) {
    throw new Error("Impossible de modifier la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de modifier la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(recipeId)}/ratings`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json'
      },
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
    throw new Error(data.error || "Impossible de supprimer la note de la recette.")
  }

  await useAuthStore().refreshRewards()
  return data
}

export async function updateRecipeRating(token, recipeId, score) {
  if (!navigator.onLine) {
    throw new Error("Impossible de modifier la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de modifier la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/recipes/${encodeURIComponent(recipeId)}/ratings`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ score }),
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
    throw new Error(data.error || "Impossible de modifier la note de la recette.")
  }

  return data
}

export async function fetchCategories() {
  return fetchRecipeOptions(
    'recipes/categories',
    'categories',
    'Impossible de récupérer les catégories.',
  )
}


export function fetchIngredients() {
  return fetchRecipeOptions(
    'ingredients',
    'ingredients',
    'Impossible de récupérer les ingrédients.',
  )
}

export function fetchTags() {
  return fetchRecipeOptions(
    'recipes/tags',
    'tags',
    'Impossible de récupérer les tags.',
  )
}

export function fetchIngredientCategories() {
  return fetchRecipeOptions(
    'ingredient-categories',
    'ingredient_categories',
    "Impossible de récupérer les catégories d'ingrédients.",
  )
}

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

export async function createIngredient(token, ingredientData) {
  if (!navigator.onLine) {
    throw new Error("Impossible de publier la recette : vous êtes hors ligne.")
  }

  if (!token) {
    throw new Error("Impossible de publier la recette : vous n'êtes pas authentifié.")
  }

  const baseUrl = import.meta.env.VITE_API_URL || ''

  let response
  try {
    response = await fetch(`${baseUrl}/api/ingredients`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(ingredientData),
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
    throw new Error(data.error || "Impossible de créer l'ingrédient.")
  }

  return data
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
  const baseUrl = import.meta.env.VITE_API_URL || ''
  const cleanBaseUrl = baseUrl.replace(/\/$/, '')

  return `${cleanBaseUrl}${imagePath}`
}
