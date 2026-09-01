<script setup>
import { ref, watch } from 'vue'
import { fetchRecipeById } from '@/services/recipeService'

const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const recipe = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

const loadRecipe = async () => {
  isLoading.value = true
  errorMessage.value = ''
  recipe.value = null

  try {
    recipe.value = await fetchRecipeById(props.id)
  } catch (error) {
    errorMessage.value =
      error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isLoading.value = false
  }
}

watch(
  () => props.id,
  loadRecipe,
  { immediate: true },
)

const formatDate = (date) => {
  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'long',
  }).format(new Date(date))
}

</script>

<template>
  <main class="mx-auto min-h-screen w-full max-w-4xl px-6 py-10">
    <p v-if="isLoading" class="text-center text-gray-600">
      Chargement de la recette...
    </p>

    <p
      v-else-if="errorMessage"
      role="alert"
      class="rounded-md bg-red-50 p-4 text-center text-red-700"
    >
      {{ errorMessage }}
    </p>

    <article
      v-else-if="recipe"
      class="overflow-hidden rounded-xl bg-white shadow-lg"
    >
      <img
        v-if="recipe.imageUrl"
        :src="recipe.imageUrl"
        :alt="`Photo de ${recipe.title}`"
        class="aspect-video w-full object-cover"
      />

      <div
        v-else
        class="flex aspect-video items-center justify-center bg-primary-light
            text-gray-700"
      >
        Image indisponible
      </div>

      <div class="space-y-8 p-6 sm:p-8">
        <header>
          <div class="mb-3 flex flex-wrap items-start gap-2">
            <span
              class="rounded-full bg-primary-light px-3 py-1 text-sm
                  font-medium text-primary-dark"
            >
              {{ recipe.category.name }}
            </span>

            <span
              v-if="recipe.difficulty"
              class="rounded-full bg-gray-100 px-3 py-1 text-sm
                  font-medium text-gray-700"
            >
              {{ recipe.difficulty }}
            </span>
            <div class="ml-auto flex max-w-[50%] flex-wrap justify-end gap-2">
              <span
                v-for="tag in recipe.tags"
                :key="tag.id"
                class="rounded-full bg-primary-light px-3 py-1
                    text-sm font-medium text-primary-dark"
              >
                #{{ tag.name }}
              </span>
            </div> 
          </div>          

          <h1 class="text-3xl font-bold text-gray-900 sm:text-4xl">
            {{ recipe.title }}
          </h1>

          <p v-if="recipe.description" class="mt-4 text-lg text-gray-600">
            {{ recipe.description }}
          </p>

          <div
            class="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-500"
          >
            <span>
              Par {{ recipe.author.username }}
            </span>

            <span v-if="recipe.cookingTime !== null">
              {{ recipe.cookingTime }} minutes
            </span>

            <time :datetime="recipe.createdAt">
              Publiée le {{ formatDate(recipe.createdAt) }}
            </time>
          </div>
        </header>

        <section
          v-if="recipe.ingredients.length"
          aria-labelledby="ingredients-title"
        >
          <h2
            id="ingredients-title"
            class="mb-5 text-2xl font-bold text-gray-900"
          >
            Ingrédients
          </h2>

          <ul class="space-y-0">
            <li
              v-for="ingredient in recipe.ingredients"
              :key="ingredient.id"
              class="flex items-center justify-between gap-4
                  rounded-md bg-gray-50 px-4"
            >
              <span class="font-medium text-gray-800">
                {{ ingredient.name }}
              </span>

              <span
                v-if="ingredient.quantity"
                class="text-gray-600"
              >
                {{ ingredient.quantity }}
              </span>
            </li>
          </ul>
        </section>

        <section
          v-if="recipe.utensils.length"
          aria-labelledby="utensils-title"
        >
          <h2
            id="utensils-title"
            class="mb-4 text-2xl font-bold text-gray-900"
          >
            Ustensiles conseillés
          </h2>

          <ul class="flex flex-wrap gap-2">
            <li
              v-for="utensil in recipe.utensils"
              :key="utensil.id"
              class="rounded-full bg-gray-100 px-3 py-1.5
                  text-sm font-medium text-gray-700"
            >
              {{ utensil.name }}
            </li>
          </ul>
        </section>

        <section aria-labelledby="steps-title">
          <h2
            id="steps-title"
            class="mb-5 text-2xl font-bold text-gray-900"
          >
            Étapes de préparation
          </h2>

          <ol class="space-y-5">
            <li
              v-for="step in recipe.steps"
              :key="step.id"
              class="flex gap-4"
            >
              <span
                class="flex h-9 w-9 shrink-0 items-center justify-center
                    rounded-full bg-primary font-bold text-white"
              >
                {{ step.stepNumber }}
              </span>

              <div class="min-w-0 flex-1">
                <p class="pt-1 leading-relaxed text-gray-700">
                  {{ step.description }}
                </p>

                <img
                  v-if="step.imageUrl"
                  :src="step.imageUrl"
                  :alt="`Illustration de l'étape ${step.stepNumber}`"
                  class="mt-3 max-h-80 rounded-lg object-cover"
                />
              </div>
            </li>
          </ol>
        </section>
      </div>
    </article>
  </main>
</template>