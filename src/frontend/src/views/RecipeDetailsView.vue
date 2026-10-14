<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
import { fetchRecipeById, deleteRecipe, rateRecipe, updateRecipeRating, deleteRecipeRating } from '@/services/recipeService'
import { useRouter } from 'vue-router'
import StarRating from '@/components/StarRating.vue'
import { useAuthStore } from '@/stores/authState'

const authStore = useAuthStore()
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
})

const isAuthor = computed(() => {
  if (!authStore.user || !recipe.value) {
    return false
  }

  return Number(authStore.user.id) === Number(recipe.value.author.id)
})

const recipe = ref(null)
const canRate = computed(() => {
  return Boolean(
    authStore.token &&
    authStore.user &&
    recipe.value &&
    !isAuthor.value &&
    recipe.value.myRating == null
  )
})

const isLoading = ref(false)
const errorMessage = ref('')
const router = useRouter()
const isDeleting = ref(false)
const deleteError = ref('')
const authorAvatarSrc = ref(null)
const selectedScore = ref(5)
const isRating = ref(false)
const ratingError = ref('')
const isEditingRating = ref(false)

watch(
  [() => recipe.value?.author.avatar_url, () => authStore.token],
  async ([avatarUrl, token], _, onCleanup) => {
    let cancelled = false
    onCleanup(() => { cancelled = true })

    if (authorAvatarSrc.value) {
      URL.revokeObjectURL(authorAvatarSrc.value)
      authorAvatarSrc.value = null
    }

    if (!avatarUrl || !token) return

    try {
      const blob = await fetchAvatarBlob(avatarUrl, token)
      if (!cancelled) {
        authorAvatarSrc.value = URL.createObjectURL(blob)
      }
    } catch {
      // L'absence d'avatar ne bloque pas l'affichage de la recette.

    }
  },
  { immediate: true },
)

onUnmounted(() => {
  if (authorAvatarSrc.value) {
    URL.revokeObjectURL(authorAvatarSrc.value)
  }
})

const startEditingRating = () => {
  selectedScore.value = recipe.value.myRating
  ratingError.value = ''
  isEditingRating.value = true
}

const handleRate = async () => {
  if (
    isRating.value ||
    !(canRate.value || (
      isEditingRating.value &&
      authStore.token &&
      authStore.user &&
      recipe.value &&
      !isAuthor.value &&
      recipe.value.myRating != null
    ))
  ) return

  isRating.value = true
  ratingError.value = ''

  try {
    const saveRating = isEditingRating.value
      ? updateRecipeRating
      : rateRecipe

    const data = await saveRating(
      authStore.token,
      recipe.value.id,
      selectedScore.value,
    )

    recipe.value.myRating = data.score
    isEditingRating.value = false
  } catch (error) {
    ratingError.value = error.message || 'Impossible de noter la recette.'
  } finally {
    isRating.value = false
  }
}

const handleDeleteRating = async () => {
  if (isRating.value || !authStore.token || !authStore.user ||
    !recipe.value || isAuthor.value || recipe.value.myRating == null) return

  isRating.value = true
  ratingError.value = ''
  const ratedRecipe = recipe.value

  try {
    await deleteRecipeRating(authStore.token, ratedRecipe.id)
    ratedRecipe.myRating = null
    isEditingRating.value = false
    selectedScore.value = 5
  } catch (error) {
    ratingError.value = error.message || 'Impossible de supprimer la note.'
  } finally {
    isRating.value = false
  }
}

const handleDelete = async () => {
  if (!isAuthor.value || isDeleting.value)
    return
  if (!window.confirm('Supprimer cette recette ?'))
    return
  isDeleting.value = true
  deleteError.value = ''

  try {
    await deleteRecipe(authStore.token, recipe.value.id)
  } catch (error) {
    deleteError.value =
      error.message || 'Une erreur inattendue est survenue.'
    return
  } finally {
    isDeleting.value = false
  }

  await router.back()
}

const loadRecipe = async () => {
  isLoading.value = true
  errorMessage.value = ''
  recipe.value = null

  try {
    recipe.value = await fetchRecipeById(props.id, authStore.token)
  } catch (error) {
    errorMessage.value =
      error.message || 'Une erreur inattendue est survenue.'
  } finally {
    isLoading.value = false
  }
}

watch(
  [() => props.id,
  () => authStore.token],
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

    <p v-else-if="errorMessage" role="alert" class="rounded-md bg-red-50 p-4 text-center text-red-700">
      {{ errorMessage }}
    </p>

    <article v-else-if="recipe" class="overflow-hidden rounded-xl bg-white shadow-lg">
      <img v-if="recipe.imageUrl" :src="recipe.imageUrl" :alt="`Photo de ${recipe.title}`"
        class="aspect-video w-full object-cover" />

      <div v-else class="flex aspect-video items-center justify-center bg-primary-light
            text-gray-700">
        Image indisponible
      </div>

      <div class="space-y-8 p-6 sm:p-8">
        <header>

          <div class="mb-3 flex items-start justify-between gap-4">
            <span class="flex flex-wrap items-start gap-2 max-w-[50%]">
              <span class="rounded-full bg-primary-light px-3 py-1 text-sm
                    font-medium text-primary-dark">
                {{ recipe.category.name }}
              </span>

              <span v-if="recipe.difficulty" class="rounded-full bg-gray-200 px-3 py-1 text-sm
                    font-medium text-gray-700">
                {{ recipe.difficulty }}
              </span>
              <span v-if="recipe.cookingTime !== null" class="rounded-full bg-gray-200 px-3 py-1 text-sm
                font-medium text-gray-700">
                {{ recipe.cookingTime }} minutes
              </span>
            </span>
            <div class="ml-auto flex max-w-[50%] flex-wrap justify-end gap-2">
              <span v-for="tag in recipe.tags" :key="tag.id" class="rounded-full bg-primary-light px-3 py-1
                    text-sm font-medium text-primary-dark">
                #{{ tag.name }}
              </span>
            </div>
          </div>

          <div v-if="isAuthor" class="rounded-lg text-gray-700 px-3 py-1 text-sm mb-4">
            <span v-if="recipe.rating != null">
              <StarRating :rating="recipe.rating" />
            </span>
            <span v-else>Pas encore notée</span>
          </div>

          <section v-if="!isAuthor" aria-label="Notation de la recette"
            class="rounded-lg text-gray-700 px-3 py-1 text-sm mb-4">
            <form v-if="canRate || isEditingRating" @submit.prevent="handleRate"
              class="flex flex-col items-start gap-2">
              <div>
                {{ isEditingRating ? 'Modifier la note :' : 'Noter cette recette :' }}
              </div>
              <div>
                <StarRating v-model:rating="selectedScore" interactive :disabled="isRating" />
              </div>
              <div class="flex items-center gap-4">
                <button type="submit" :disabled="isRating"
                  class="rounded-full bg-primary-light hover:bg-primary transition-colors text-gray-700 px-3 py-1 text-sm">
                  {{ isRating ? 'Envoi...' : isEditingRating ? 'Enregistrer' : 'Noter' }}
                </button>

                <button v-if="isEditingRating" type="button" :disabled="isRating" @click="isEditingRating = false"
                  class="rounded-full hover:bg-primary-light transition-colors text-gray-700 px-3 py-1 text-sm">
                  Annuler
                </button>
              </div>
            </form>

            <div v-else-if="authStore.user && recipe.myRating != null" class="flex flex-col items-start gap-2">
              <div>
                Tu as noté cette recette:
              </div>
              <div>
                <StarRating :rating="recipe.myRating" />
              </div>
              <div class="flex items-center gap-4">
                <button type="button" @click="startEditingRating" :disabled="isRating"
                  class="rounded-full bg-primary-light text-gray-700 px-3 py-1 text-sm hover:bg-primary transition-colors">
                  Modifier
                </button>
                <button type="button" :disabled="isRating" @click="handleDeleteRating" class="rounded-full bg-red-400 text-gray-700 px-3 py-1 text-sm
                        hover:bg-red-300 transition-colors disabled:cursor-not-allowed disabled:opacity-50">
                  {{ isRating ? 'Suppression...' : 'Supprimer' }}
                </button>
              </div>
            </div>

            <p v-if="ratingError" role="alert" class="mt-2 text-red-700">
              {{ ratingError }}
            </p>
          </section>

          <div class="flex items-start justify-between gap-4">
            <h1 class="text-3xl font-bold text-gray-900 sm:text-4xl">
              {{ recipe.title }}
            </h1>
            <div v-if="isAuthor" class="flex shrink-0 flex-wrap gap-2">
              <RouterLink :to="{
                name: 'recipe-edit',
                params: { id: recipe.id },
              }" class="shrink-0 rounded-md bg-primary px-4 py-2
                    font-semibold text-white hover:bg-primary-dark">
                Modifier
              </RouterLink>
              <button type="button" :disabled="isDeleting" @click="handleDelete" class="rounded-md bg-red-600 px-4 py-2
                  font-semibold text-white hover:bg-red-700
                  disabled:cursor-not-allowed disabled:opacity-50">
                {{ isDeleting ? 'Suppression...' : 'Supprimer' }}
              </button>
              <p v-if="deleteError" role="alert" class="mt-3 text-red-700">
                {{ deleteError }}
              </p>
            </div>
          </div>
          <p v-if="recipe.description" class="mt-4 text-lg text-gray-600">
            {{ recipe.description }}
          </p>
          <div class="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-gray-500">
            <span class="inline-flex items-center gap-2">
              <img v-if="authorAvatarSrc" :src="authorAvatarSrc" :alt="`Avatar de ${recipe.author.username}`"
                class="h-8 w-8 rounded-full object-cover" />
              Par {{ recipe.author.username }}
            </span>
            <time :datetime="recipe.createdAt">
              Publiée le {{ formatDate(recipe.createdAt) }}
            </time>
          </div>
        </header>

        <section v-if="recipe.ingredients.length" aria-labelledby="ingredients-title">
          <h2 id="ingredients-title" class="mb-5 text-2xl font-bold text-gray-900">
            Ingrédients
          </h2>

          <ul class="space-y-0">
            <li v-for="ingredient in recipe.ingredients" :key="ingredient.id" class="flex items-center justify-between gap-4
                  rounded-md bg-gray-50 px-4">
              <span class="font-medium text-gray-800">
                {{ ingredient.name }}
              </span>

              <span v-if="ingredient.quantity" class="text-gray-600">
                {{ ingredient.quantity }}
              </span>
            </li>
          </ul>
        </section>

        <section aria-labelledby="steps-title">
          <h2 id="steps-title" class="mb-5 text-2xl font-bold text-gray-900">
            Étapes de préparation
          </h2>

          <ol class="space-y-5">
            <li v-for="step in recipe.steps" :key="step.id" class="flex gap-4">
              <span class="flex h-9 w-9 shrink-0 items-center justify-center
                    rounded-full bg-primary font-bold text-white">
                {{ step.stepNumber }}
              </span>

              <div class="min-w-0 flex-1">
                <p class="pt-1 leading-relaxed text-gray-700">
                  {{ step.description }}
                </p>

                <img v-if="step.imageUrl" :src="step.imageUrl" :alt="`Illustration de l'étape ${step.stepNumber}`"
                  class="mt-3 max-h-80 rounded-lg object-cover" />
              </div>
            </li>
          </ol>
        </section>
      </div>
    </article>
  </main>
</template>
