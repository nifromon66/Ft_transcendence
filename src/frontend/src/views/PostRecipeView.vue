<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/authState'
import { createRecipe, fetchCategories } from '@/services/recipeService'

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const router = useRouter()
const authStore = useAuthStore()
const categories = ref([])
const isLoadingCategories = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const recipe = reactive({
  title: '',
  categoryId: '',
  description: '',
  cookingTime: null,
  difficulty: '',
  instructions: '',
  image: null,
  ingredients: [{ name: '', quantity: '' }],
  utensils: [''],
  tags: [''],
})

const addIngredient = () => {
  recipe.ingredients.push({ name: '', quantity: '' })
}

const removeIngredient = (index) => {
  recipe.ingredients.splice(index, 1)
}

const addListItem = (list) => {
  list.push('')
}

const removeListItem = (list, index) => {
  list.splice(index, 1)
}

const selectImage = (event) => {
  recipe.image = event.target.files[0] ?? null
}

onMounted(async () => {
  try {
    categories.value = await fetchCategories()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoadingCategories.value = false
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
    instructions: recipe.instructions || null,
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
                :disabled="isLoadingCategories"
                class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:cursor-wait
                    disabled:bg-gray-100"
              >
                <option disabled value="">
                  {{ isLoadingCategories ? 'Chargement des catégories...' : 'Choisir une catégorie' }}
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
            <label for="recipe-instructions" class="mb-1 block font-medium">
              Instructions
            </label>
            <textarea
              id="recipe-instructions"
              v-model.trim="recipe.instructions"
              rows="8"
              placeholder="Décris les différentes étapes de la préparation..."
              class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                  focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>
        </section>

        <section aria-labelledby="ingredients-title">
          <h2 id="ingredients-title" class="mb-4 text-xl font-semibold">
            Ingrédients
          </h2>

          <div class="space-y-3">
            <div
              v-for="(ingredient, index) in recipe.ingredients"
              :key="index"
              class="grid gap-2 sm:grid-cols-[1fr_1fr_auto]"
            >
              <input
                v-model.trim="ingredient.name"
                type="text"
                :aria-label="`Ingrédient ${index + 1}`"
                placeholder="Ex. Carottes"
                class="rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
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
              :key="index"
              class="flex gap-2"
            >
              <input
                v-model.trim="recipe.utensils[index]"
                type="text"
                :aria-label="`Ustensile ${index + 1}`"
                placeholder="Ex. Casserole"
                class="min-w-0 flex-1 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <button
                v-if="recipe.utensils.length > 1"
                type="button"
                class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                @click="removeListItem(recipe.utensils, index)"
              >
                Retirer
              </button>
            </div>
          </div>

          <button
            type="button"
            class="mt-3 rounded-md border border-primary px-3 py-2 font-medium text-primary-dark hover:bg-primary-light"
            @click="addListItem(recipe.utensils)"
          >
            Ajouter un ustensile
          </button>
        </section>

        <section aria-labelledby="tags-title">
          <h2 id="tags-title" class="mb-4 text-xl font-semibold">Tags</h2>

          <div class="space-y-3">
            <div
              v-for="(tag, index) in recipe.tags"
              :key="index"
              class="flex gap-2"
            >
              <input
                v-model.trim="recipe.tags[index]"
                type="text"
                :aria-label="`Tag ${index + 1}`"
                placeholder="Ex. Végétarien"
                class="min-w-0 flex-1 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200"
              />
              <button
                v-if="recipe.tags.length > 1"
                type="button"
                class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                @click="removeListItem(recipe.tags, index)"
              >
                Retirer
              </button>
            </div>
          </div>

          <button
            type="button"
            class="mt-3 rounded-md border border-primary px-3 py-2 font-medium text-primary-dark hover:bg-primary-light"
            @click="addListItem(recipe.tags)"
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
          :disabled="isSubmitting || isLoadingCategories"
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
