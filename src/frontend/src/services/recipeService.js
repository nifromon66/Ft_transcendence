
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

