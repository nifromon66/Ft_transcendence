<script setup>
import { useRouter } from 'vue-router'
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/authState'
import { fetchRecipeById, updateRecipe } from '@/services/recipeService'
import RecipeForm from '@/components/RecipeForm.vue'
import RecipeErrorNotice from '@/components/RecipeErrorNotice.vue'
import {
  deleteRecipeImage,
  deleteRecipeStepImage,
  uploadRecipeImage,
  uploadRecipeStepImage,
} from '@/services/recipeService'
import { optimizeImage } from '@/utils/imageProcessor'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const router = useRouter()
const isSubmitting = ref(false)
const authStore = useAuthStore()
const recipe = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const submitErrorMessage = ref('')
const formRecipe = ref(null)

const loadRecipe = async () => {
  isLoading.value = true
  errorMessage.value = ''
  submitErrorMessage.value = ''
  formRecipe.value = null
  recipe.value = null

  try {
    const loadedRecipe = await fetchRecipeById(props.id)

    const currentUserId = Number(authStore.user?.id)
    const authorId = Number(loadedRecipe.author.id)

    if (!currentUserId || (currentUserId !== authorId && !authStore.can('recipes.edit_any'))) {
      errorMessage.value =
        "Tu n'es pas autorisé à modifier cette recette."
      return
    }

    recipe.value = loadedRecipe

    formRecipe.value = {
      title: loadedRecipe.title,
      categoryId: loadedRecipe.category.id,
      description: loadedRecipe.description || '',
      cookingTime: loadedRecipe.cookingTime,
      difficulty: loadedRecipe.difficulty || '',
      imageUrl: loadedRecipe.imageUrl,

      steps: loadedRecipe.steps.map((step) => ({
        id: step.id,
        persistedId: step.id,
        description: step.description,
        imageUrl: step.imageUrl,
      })),

      ingredients: loadedRecipe.ingredients.map((ingredient) => ({
        id: ingredient.id,
        ingredientId: ingredient.ingredientId,
        categoryId: ingredient.categoryId || '',
        quantity: ingredient.quantity || '',
      })),

      tags: loadedRecipe.tags.map((tag) => ({
        id: tag.id,
        tagId: tag.tagId,
      })),
    }

  } catch (error) {
    errorMessage.value =
      error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isLoading.value = false
  }
}

const submitRecipe = async (
  recipeData,
  recipeImageFile,
  shouldDeleteRecipeImage,
  stepImageChanges = [],
) => {
  if (!authStore.token) {
    submitErrorMessage.value = 'Tu dois être connecté pour modifier cette recette.'
    return
  }

  submitErrorMessage.value = ''
  isSubmitting.value = true

  try {
    const updatedRecipe = await updateRecipe(
      authStore.token,
      props.id,
      recipeData,
    )

    if (recipeImageFile) {
      const optimizedImage = await optimizeImage(
        recipeImageFile,
        1600,
        1600,
        0.82,
      )

      await uploadRecipeImage(
        authStore.token,
        props.id,
        optimizedImage,
      )
    } else if (shouldDeleteRecipeImage) {
      await deleteRecipeImage(
        authStore.token,
        props.id,
      )
    }

    const stepImageRequests = stepImageChanges.map(
      async (imageChange, index) => {
        if (!imageChange.file && !imageChange.shouldDelete) {
          return
        }

        const updatedStep = updatedRecipe.steps[index]

        if (!updatedStep) {
          throw new Error(
            "Impossible d'associer une image à son étape."
          )
        }

        if (imageChange.file) {
          const optimizedImage = await optimizeImage(
            imageChange.file,
            1200,
            1200,
            0.82,
          )

          await uploadRecipeStepImage(
            authStore.token,
            props.id,
            updatedStep.id,
            optimizedImage,
          )
        } else if (imageChange.shouldDelete) {
          await deleteRecipeStepImage(
            authStore.token,
            props.id,
            updatedStep.id,
          )
        }
      },
    )

    await Promise.all(stepImageRequests)

    await router.push({
      name: 'recipe-details',
      params: { id: props.id },
    })
  } catch (error) {
    submitErrorMessage.value =
      error.message || 'Impossible de modifier la recette.'
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    router.push({
      name: 'recipe-details',
      params: { id: props.id },
    })
  }
}

watch(
  () => props.id,
  loadRecipe,
  { immediate: true },
)
</script>

<template>
  <main class="mx-auto min-h-screen w-full max-w-4xl px-6 py-10">
    <p v-if="isLoading">
      Chargement de la recette...
    </p>

    <p v-else-if="errorMessage" role="alert" class="rounded-md bg-red-50 p-4 text-red-700">
      {{ errorMessage }}
    </p>

    <div v-else-if="formRecipe" class="rounded-lg p-6 text-gray-800">
      <h1 class="mb-6 text-3xl font-bold">Modifier la recette</h1>

      <RecipeForm :key="id" :initial-recipe="formRecipe" :is-submitting="isSubmitting"
        submit-label="Enregistrer les modifications" @submit="submitRecipe" @cancel="handleCancel" />

        <RecipeErrorNotice
            :message="submitErrorMessage"
            @close="submitErrorMessage = ''"
        />
      <p v-if="errorMessage" role="alert" class="mt-4 rounded-md bg-red-50 p-3 text-red-700">
        {{ errorMessage }}
      </p>
    </div>
  </main>
</template>
