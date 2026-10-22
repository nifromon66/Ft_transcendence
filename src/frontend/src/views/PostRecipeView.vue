<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authState'
import { createRecipe } from '@/services/recipeService'
import RecipeForm from '@/components/RecipeForm.vue'
import RecipeErrorNotice from '@/components/RecipeErrorNotice.vue'
import {
  uploadRecipeImage,
  uploadRecipeStepImage,
} from '@/services/recipeService'
import { optimizeImage } from '@/utils/imageProcessor'

const router = useRouter()
const authStore = useAuthStore()

const isSubmitting = ref(false)
const errorMessage = ref('')

const submitRecipe = async (
  recipeData,
  recipeImageFile,
  _shouldDeleteRecipeImage,
  stepImageChanges = [],
) => {
  if (!authStore.token) {
    errorMessage.value = 'Tu dois être connecté pour publier une recette.'
    return
  }

  errorMessage.value = ''
  isSubmitting.value = true

  try {
    try {
      await authStore.silentRefresh()
    } catch {
      // Keep current token if silent refresh fails
    }

    const createdRecipe = await createRecipe(authStore.token, recipeData)

    if (recipeImageFile) {
      const optimizedImage = await optimizeImage(
        recipeImageFile,
        1600,
        1600,
        0.82,
      )

      await uploadRecipeImage(
        authStore.token,
        createdRecipe.id,
        optimizedImage,
      )
    }

    const stepUploads = stepImageChanges.map(
      async (imageChange, index) => {
        if (!imageChange.file) {
          return
        }

        const createdStep = createdRecipe.steps[index]

        if (!createdStep) {
          throw new Error(
            "Impossible d'associer une image à son étape."
          )
        }

        const optimizedImage = await optimizeImage(
          imageChange.file,
          1200,
          1200,
          0.82,
        )

        await uploadRecipeStepImage(
          authStore.token,
          createdRecipe.id,
          createdStep.id,
          optimizedImage,
        )
      },
    )

    await Promise.all(stepUploads)

    await router.push({
      name: 'recipe-details',
      params: { id: createdRecipe.id },
    })
  } catch (error) {
    errorMessage.value =
      error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    router.push({ name: 'home' })
  }
}
</script>

<template>
  <main class="mx-auto min-h-screen w-full max-w-4xl px-6 py-10">
    <div class="rounded-lg p-6 text-gray-800">
      <h1 class="mb-6 text-3xl font-bold">Publier une recette</h1>

      <RecipeForm :is-submitting="isSubmitting" submit-label="Publier la recette" @submit="submitRecipe"
        @cancel="handleCancel" />

      <RecipeErrorNotice :message="errorMessage" @close="errorMessage = ''" />
      <p v-if="errorMessage" role="alert" class="mt-4 rounded-md bg-red-50 p-3 text-red-700">
        {{ errorMessage }}
      </p>
    </div>
  </main>
</template>
