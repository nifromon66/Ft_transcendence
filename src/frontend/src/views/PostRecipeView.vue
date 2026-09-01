<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/authState'
import { 
  createRecipe, 
  fetchCategories,
  fetchIngredients,
  fetchTags,
  fetchUtensils, 
} from '@/services/recipeService'

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const router = useRouter()
const authStore = useAuthStore()
const categories = ref([])
const ingredientOptions = ref([])
const utensilOptions = ref([])
const tagOptions = ref([])
const isLoadingOptions = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const recipe = reactive({
  title: '',
  categoryId: '',
  description: '',
  cookingTime: null,
  difficulty: '',
  steps: [{ id: 1, description: '' }],
  image: null,
  ingredients: [{  id: 1, ingredientId: '', quantity: '' }],
  utensils: [{ id: 1, utensilId: '', }],
  tags: [{ id: 1, tagId: '', }],
})

let nextStepId = 2

const addStep = () => {
  recipe.steps.push({
    id: nextStepId,
    description: '',
  })

  nextStepId += 1
}

const removeStep = (index) => {
  if (recipe.steps.length > 1) {
    recipe.steps.splice(index, 1)
  }
}

let nextIngredientId = 2
const addIngredient = () => {
  recipe.ingredients.push({ id: nextIngredientId, ingredientId: '', quantity: '' })
  nextIngredientId += 1
}

let nextUtensilId = 2

const addUtensil = () => {
  recipe.utensils.push({
    id: nextUtensilId,
    utensilId: '',
  })

  nextUtensilId += 1
}

const removeUtensil = (index) => {
  if (recipe.utensils.length > 1) {
    recipe.utensils.splice(index, 1)
  }
}

const isUtensilSelected = (utensilId, currentIndex) => {
  return recipe.utensils.some((utensil, index) => {
    return (
      index !== currentIndex &&
      utensil.utensilId === utensilId
    )
  })
}

let nextTagId = 2

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
  return recipe.tags.some((tag, index) => {
    return (
      index !== currentIndex &&
      tag.tagId === tagId
    )
  })
}

const removeIngredient = (index) => {
  recipe.ingredients.splice(index, 1)
}

const isIngredientSelected = (ingredientId, currentIndex) => {
  return recipe.ingredients.some((ingredient, index) => {
    return (
      index !== currentIndex &&
      ingredient.ingredientId === ingredientId
    )
  })
}

const selectImage = (event) => {
  recipe.image = event.target.files[0] ?? null
}

onMounted(async () => {
  try {
    const [
      loadedCategories,
      loadedIngredients,
      loadedUtensils,
      loadedTags,
    ] = await Promise.all([
      fetchCategories(),
      fetchIngredients(),
      fetchUtensils(),
      fetchTags(),
    ])

    categories.value = loadedCategories
    ingredientOptions.value = loadedIngredients
    utensilOptions.value = loadedUtensils
    tagOptions.value = loadedTags
  } catch (error) {
    errorMessage.value =
      error.message || 'Impossible de charger les options du formulaire.'
  } finally {
    isLoadingOptions.value = false
  }
})

const submitRecipe = async () => {
  if (!authStore.token) {
    errorMessage.value = 'Tu dois être connecté pour publier une recette.'
    return
  }

  errorMessage.value = ''
  isSubmitting.value = true

  const recipeData = {
    title: recipe.title,
    category_id: recipe.categoryId,
    description: recipe.description || null,
    cooking_time: recipe.cookingTime === '' ? null : recipe.cookingTime,
    difficulty: recipe.difficulty || null,
    steps: recipe.steps.map((step) => ({
      description: step.description.trim(),
    })),
    
    ingredients: recipe.ingredients.map((ingredient) => ({
      ingredient_id: ingredient.ingredientId,
      quantity: ingredient.quantity.trim() || null,
    })),

    utensil_ids: recipe.utensils.map(
      (utensil) => utensil.utensilId
    ),
    
    tag_ids: recipe.tags.map(
      (tag) => tag.tagId
    ),
  }

  try {
    const createdRecipe = await createRecipe(authStore.token, recipeData)
    await router.push({
      name: 'recipe-details',
      params: { id: createdRecipe.id },
    })
  } catch (error) {
    errorMessage.value = error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="mx-auto min-h-screen w-full max-w-4xl px-6 py-10">
    <div class="rounded-lg bg-white p-6 text-gray-800 shadow">
      <h1 class="mb-6 text-3xl font-bold">Publier une recette</h1>

      <form class="space-y-8" @submit.prevent="submitRecipe">
        <section aria-labelledby="main-information-title">
          <h2 id="main-information-title" class="mb-4 text-xl font-semibold">
            Informations principales
          </h2>

          <div class="space-y-4">
            <div>
              <label for="recipe-title" class="mb-1 block font-medium">
                Titre
              </label>
              <input
                id="recipe-title"
                v-model.trim="recipe.title"
                type="text"
                required
                maxlength="150"
                placeholder="Ex. Soupe de légumes"
                class="w-full resize-none rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label for="recipe-category" class="mb-1 block font-medium">
                Catégorie
              </label>
              <select
                id="recipe-category"
                v-model="recipe.categoryId"
                required
                :disabled="isLoadingOptions"
                class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:cursor-wait
                    disabled:bg-gray-100"
              >
                <option disabled value="">
                  {{ isLoadingOptions ? 'Chargement des catégories...' : 'Choisir une catégorie' }}
                </option>
                <option
                  v-for="category in categories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </option>
              </select>
            </div>

            <div>
              <label for="recipe-description" class="mb-1 block font-medium">
                Description
              </label>
              <textarea
                id="recipe-description"
                v-model.trim="recipe.description"
                rows="2"
                maxlength="100"
                @keydown.enter.prevent
                placeholder="Présente brièvement ta recette..."
                class="w-full resize-none rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <p class="mt-1 text-right text-sm text-gray-500">
                {{ recipe.description.length }}/100 caractères
              </p>
            </div>
          </div>
        </section>

        <section aria-labelledby="preparation-title">
          <h2 id="preparation-title" class="mb-4 text-xl font-semibold">
            Préparation
          </h2>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label for="recipe-cooking-time" class="mb-1 block font-medium">
                Temps de préparation (minutes)
              </label>
              <input
                id="recipe-cooking-time"
                v-model.number="recipe.cookingTime"
                type="number"
                min="0"
                step="1"
                placeholder="Ex. 30"
                class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
            </div>

            <div>
              <label for="recipe-difficulty" class="mb-1 block font-medium">
                Difficulté
              </label>
              <select
                id="recipe-difficulty"
                v-model="recipe.difficulty"
                class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <option value="">Choisir une difficulté</option>
                <option value="facile">Facile</option>
                <option value="moyen">Moyen</option>
                <option value="difficile">Difficile</option>
              </select>
            </div>
          </div>

          <div class="mt-4">
            <h3 class="mb-3 font-medium">Étapes de préparation</h3>

            <div class="space-y-4">
              <div
                v-for="(step, index) in recipe.steps"
                :key="step.id"
                class="rounded-md border border-gray-200 p-4"
              >
                <label
                  :for="`recipe-step-${step.id}`"
                  class="mb-1 block font-medium"
                >
                  Étape {{ index + 1 }}
                </label>

                <textarea
                  :id="`recipe-step-${step.id}`"
                  v-model.trim="step.description"
                  rows="3"
                  required
                  placeholder="Décris cette étape de la préparation..."
                  class="w-full resize-none rounded-md border border-gray-300 px-3 py-2
                      focus:border-blue-500 focus:outline-none focus:ring-2
                      focus:ring-blue-200"
                />

                <button
                  v-if="recipe.steps.length > 1"
                  type="button"
                  class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                  @click="removeStep(index)"
                >
                  Retirer cette étape
                </button>
              </div>
            </div>

            <button
              type="button"
              class="mt-3 rounded-md border border-primary px-3 py-2
                    font-medium text-primary-dark hover:bg-primary-light"
              @click="addStep"
            >
              Ajouter une étape
            </button>
          </div>
        </section>

        <section aria-labelledby="ingredients-title">
          <h2 id="ingredients-title" class="mb-4 text-xl font-semibold">
            Ingrédients
          </h2>

          <div class="space-y-3">
            <div
              v-for="(ingredient, index) in recipe.ingredients"
              :key="ingredient.id"
              class="grid gap-2 sm:grid-cols-[1fr_1fr_auto]"
            >
              <select
                v-model="ingredient.ingredientId"
                required
                :aria-label="`Ingrédient ${index + 1}`"
                class="rounded-md border border-gray-300 bg-white px-3 py-2
                    focus:border-blue-500 focus:outline-none focus:ring-2
                    focus:ring-blue-200"
              >
                <option disabled value="">
                  Choisir un ingrédient
                </option>

                <option
                  v-for="ingredientOption in ingredientOptions"
                  :key="ingredientOption.id"
                  :value="ingredientOption.id"
                  :disabled="isIngredientSelected(ingredientOption.id, index)"
                >
                  {{ ingredientOption.name }}
                </option>
              </select>
              <input
                v-model.trim="ingredient.quantity"
                type="text"
                :aria-label="`Quantité de l'ingrédient ${index + 1}`"
                placeholder="Ex. 3 ou 250 g"
                class="rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <button
                v-if="recipe.ingredients.length > 1"
                type="button"
                class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                @click="removeIngredient(index)"
              >
                Retirer
              </button>
            </div>
          </div>

          <button
            type="button"
            class="mt-3 rounded-md border border-primary px-3 py-2 font-medium text-primary-dark hover:bg-primary-light"
            @click="addIngredient"
          >
            Ajouter un ingrédient
          </button>
        </section>

        <section aria-labelledby="utensils-title">
          <h2 id="utensils-title" class="mb-4 text-xl font-semibold">
            Ustensiles
          </h2>

          <div class="space-y-3">
            <div
              v-for="(utensil, index) in recipe.utensils"
              :key="utensil.id"
              class="flex gap-2"
            >
              <select
                v-model="utensil.utensilId"
                required
                :aria-label="`Ustensile ${index + 1}`"
                class="min-w-0 flex-1 rounded-md border border-gray-300
                    bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <option disabled value="">
                  Choisir un ustensile
                </option>

                <option
                  v-for="utensilOption in utensilOptions"
                  :key="utensilOption.id"
                  :value="utensilOption.id"
                  :disabled="isUtensilSelected(utensilOption.id, index)"
                >
                  {{ utensilOption.name }}
                </option>
              </select>

              <button
                v-if="recipe.utensils.length > 1"
                type="button"
                class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                @click="removeUtensil(index)"
              >
                Retirer
              </button>
            </div>
          </div>

          <button
            type="button"
            class="mt-3 rounded-md border border-primary px-3 py-2
                font-medium text-primary-dark hover:bg-primary-light"
            @click="addUtensil"
          >
            Ajouter un ustensile
          </button>
        </section>

        <section aria-labelledby="tags-title">
          <h2 id="tags-title" class="mb-4 text-xl font-semibold">Tags</h2>

          <div class="space-y-3">
            <div
              v-for="(tag, index) in recipe.tags"
              :key="tag.id"
              class="flex gap-2"
            >
              <select
                v-model="tag.tagId"
                required
                :aria-label="`Tag ${index + 1}`"
                class="min-w-0 flex-1 rounded-md border border-gray-300
                    bg-white px-3 py-2 focus:border-blue-500
                      focus:outline-none focus:ring-2 focus:ring-blue-200"
              >
                <option disabled value="">
                  Choisir un tag
                </option>

                <option
                  v-for="tagOption in tagOptions"
                  :key="tagOption.id"
                  :value="tagOption.id"
                  :disabled="isTagSelected(tagOption.id, index)"
                >
                  {{ tagOption.name }}
                </option>
              </select>

              <button
                v-if="recipe.tags.length > 1"
                type="button"
                class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                @click="removeTag(index)"
              >
                Retirer
              </button>
            </div>
          </div>

          <button
            type="button"
            class="mt-3 rounded-md border border-primary px-3 py-2
                font-medium text-primary-dark hover:bg-primary-light"
            @click="addTag"
          >
            Ajouter un tag
          </button>
        </section>

        <section aria-labelledby="image-title">
          <h2 id="image-title" class="mb-4 text-xl font-semibold">
            Photo de la recette
          </h2>

          <label for="recipe-image" class="mb-1 block font-medium">
            Choisir une image
          </label>
          <input
            id="recipe-image"
            type="file"
            accept="image/png,image/jpeg,image/gif,image/webp"
            class="block w-full rounded-md border border-gray-300 bg-white px-3 py-2
                file:mr-4 file:rounded-md file:border-0 file:bg-primary-light file:px-3 file:py-2
                file:font-medium file:text-primary-dark"
            @change="selectImage"
          />
          <p v-if="recipe.image" class="mt-2 text-sm text-gray-600">
            Image sélectionnée : {{ recipe.image.name }}
          </p>
        </section>

        <button
          type="submit"
          :disabled="isSubmitting || isLoadingOptions"
          class="w-full rounded-md bg-primary px-4 py-3 font-semibold text-white hover:bg-primary-dark
              disabled:cursor-not-allowed disabled:opacity-50"
        >
          {{ isSubmitting ? 'Publication...' : 'Publier la recette' }}
        </button>

        <p
          v-if="errorMessage"
          role="alert"
          class="rounded-md bg-red-50 p-3 text-red-700"
        >
          {{ errorMessage }}
        </p>

      </form>
    </div>
  </main>
</template>
