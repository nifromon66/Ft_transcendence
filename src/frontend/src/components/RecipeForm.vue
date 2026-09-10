<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  fetchCategories,
  fetchIngredients,
  fetchTags,
  fetchUtensils,
} from '@/services/recipeService'
import ImageDropZone from '@/components/ImageDropZone.vue'
import ImagePreview from '@/components/ImagePreview.vue'
import { validateRecipeImage } from '@/utils/fileValidators'

const router = useRouter()
const props = defineProps({
  initialRecipe: {
    type: Object,
    default: null,
  },
  isSubmitting: {
    type: Boolean,
    default: false,
  },
  submitLabel: {
    type: String,
    default: 'Publier la recette',
  },
})

const emit = defineEmits(['submit'])
const categories = ref([])
const ingredientOptions = ref([])
const utensilOptions = ref([])
const tagOptions = ref([])
const isLoadingOptions = ref(true)
const errorMessage = ref('')

const recipeImageFile = ref(null)
const existingRecipeImageUrl = ref(props.initialRecipe?.imageUrl || null)
const shouldDeleteRecipeImage = ref(false)
const showRecipeImageDropZone = ref(false)

const handleRecipeImage = (file) => {
  const { isValid, error } = validateRecipeImage(file)

  if (!isValid) {
    errorMessage.value = error
    return
  }

  errorMessage.value = ''
  recipeImageFile.value = file
  shouldDeleteRecipeImage.value = false
}

const removeExistingRecipeImage = () => {
  existingRecipeImageUrl.value = null
  shouldDeleteRecipeImage.value = true
}

const clearRecipeImage = () => {
  recipeImageFile.value = null
  showRecipeImageDropZone.value = false
}

const createFormRecipe = () => {
  if (!props.initialRecipe) {
    return {
      title: '',
      categoryId: '',
      description: '',
      cookingTime: null,
      difficulty: '',
      steps: [
        {
          id: 1,
          description: '',
          imageUrl: null,
          imageFile: null,
          shouldDeleteImage: false,
          showImageDropZone: false,
        },
      ],
      ingredients: [
        {
          id: 1,
          ingredientId: '',
          quantity: '',
        },
      ],
      utensils: [
        {
          id: 1,
          utensilId: '',
        },
      ],
      tags: [
        {
          id: 1,
          tagId: '',
        },
      ],
    }
  }

  return {
    title: props.initialRecipe.title,
    categoryId: props.initialRecipe.categoryId,
    description: props.initialRecipe.description || '',
    cookingTime: props.initialRecipe.cookingTime,
    difficulty: props.initialRecipe.difficulty || '',

    steps: props.initialRecipe.steps.map((step) => ({
      ...step,
      imageUrl: step.imageUrl || null,
      imageFile: null,
      shouldDeleteImage: false,
      showImageDropZone: false,
    })),

    ingredients: props.initialRecipe.ingredients.map((ingredient) => ({
      ...ingredient,
    })),

    utensils: props.initialRecipe.utensils.map((utensil) => ({
      ...utensil,
    })),

    tags: props.initialRecipe.tags.map((tag) => ({
      ...tag,
    })),
  }
}

const recipe = reactive(createFormRecipe())

let nextStepId = Math.max(0, ...recipe.steps.map((step) => Number(step.id))) + 1

const addStep = () => {
  recipe.steps.push({
    id: nextStepId,
    description: '',
    imageUrl: null,
    imageFile: null,
    shouldDeleteImage: false,
    showImageDropZone: false,
  })

  nextStepId += 1
}

const removeStep = (index) => {
  if (recipe.steps.length > 1) {
    recipe.steps.splice(index, 1)
  }
}

const handleStepImage = (step, file) => {
  const { isValid, error } = validateRecipeImage(file)

  if (!isValid) {
    errorMessage.value = error
    return
  }

  errorMessage.value = ''
  step.imageFile = file
  step.shouldDeleteImage = false
}

const clearStepImage = (step) => {
  step.imageFile = null
  step.showImageDropZone = false
}

const removeExistingStepImage = (step) => {
  step.imageUrl = null
  step.shouldDeleteImage = true
}

let nextIngredientId = Math.max( 0, ...recipe.ingredients.map((ingredient) => Number(ingredient.id))) + 1

const addIngredient = () => {
  recipe.ingredients.push({ id: nextIngredientId, ingredientId: '', quantity: '' })
  nextIngredientId += 1
}

let nextUtensilId = Math.max( 0, ...recipe.utensils.map((utensil) => Number(utensil.id))) + 1

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

let nextTagId = Math.max(0, ...recipe.tags.map((tag) => Number(tag.id))) + 1

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

const submitForm = () => {
  const recipeData = {
    title: recipe.title,
    category_id: recipe.categoryId,
    description: recipe.description || null,
    cooking_time: recipe.cookingTime === '' ? null : recipe.cookingTime,
    difficulty: recipe.difficulty || null,

    steps: recipe.steps.map((step) => ({
      id: step.persistedId ?? null,
      description: step.description.trim(),
    })),

    ingredients: recipe.ingredients.map((ingredient) => ({
      ingredient_id: ingredient.ingredientId,
      quantity: ingredient.quantity.trim() || null,
    })),

    utensil_ids: recipe.utensils.map((utensil) => utensil.utensilId),

    tag_ids: recipe.tags.map((tag) => tag.tagId),
  }

  const stepImageChanges = recipe.steps.map((step) => ({
    persistedId: step.persistedId ?? null,
    file: step.imageFile,
    shouldDelete: step.shouldDeleteImage,
  }))

  emit(
    'submit',
    recipeData,
    recipeImageFile.value,
    shouldDeleteRecipeImage.value,
    stepImageChanges,
  )
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

</script>

<template>
  <form class="space-y-8" @submit.prevent="submitForm">
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
            <div>
              <p class="mb-1 block font-medium">
                Image de la recette (facultatif)
              </p>

              <ImagePreview
                v-if="recipeImageFile"
                :file="recipeImageFile"
                :disabled="isSubmitting"
                @clear="clearRecipeImage"
              />

              <div
                v-else-if="existingRecipeImageUrl"
                class="my-4 w-full max-w-sm"
              >
                <img
                  :src="existingRecipeImageUrl"
                  alt="Image actuelle de la recette"
                  class="h-48 w-full rounded-lg object-cover"
                />

                <button
                  type="button"
                  class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                  :disabled="isSubmitting"
                  @click="removeExistingRecipeImage"
                >
                  Supprimer l’image
                </button>
              </div>

              <button
                v-else-if="!showRecipeImageDropZone"
                type="button"
                class="rounded-md border border-primary px-3 py-2 font-medium
                    text-primary-dark hover:bg-primary-light"
                :disabled="isSubmitting"
                @click="showRecipeImageDropZone = true"
              >
                Ajouter une image
              </button>
              <div v-else class="flex items-start gap-3">
                <div>
                  <ImageDropZone
                    
                    accept=".png,.jpg,.jpeg,.webp"
                    :disabled="isSubmitting"
                    @file-selected="handleRecipeImage"
                  />
                  <p class="text-sm text-gray-500">
                    PNG, JPEG ou WebP — 10 Mo maximum.
                  </p>
                </div>
                <button
                      type="button"
                      class="mt-4 shrink-0 rounded-md px-3 py-2 text-gray-600 hover:bg-gray-100"
                      :disabled="isSubmitting"
                      @click="showRecipeImageDropZone = false"
                    >
                      Annuler
                </button>
              </div>
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
                <div class="mt-3">
                  <p class="mb-1 text-sm font-medium">
                    Image de l’étape (facultatif)
                  </p>

                  <ImagePreview
                    v-if="step.imageFile"
                    :file="step.imageFile"
                    :disabled="isSubmitting"
                    @clear="clearStepImage(step)"
                  />

                  <div
                    v-else-if="step.imageUrl"
                    class="my-4 w-full max-w-sm"
                  >
                    <img
                      :src="step.imageUrl"
                      :alt="`Image actuelle de l'étape ${index + 1}`"
                      class="h-36 w-full rounded-lg object-cover"
                    />

                    <button
                      type="button"
                      class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                      :disabled="isSubmitting"
                      @click="removeExistingStepImage(step)"
                    >
                      Supprimer l’image de l’étape
                    </button>
                  </div>

                  <button
                    v-else-if="!step.showImageDropZone"
                    type="button"
                    class="rounded-md border border-primary px-3 py-2 text-sm font-medium
                        text-primary-dark hover:bg-primary-light"
                    :disabled="isSubmitting"
                    @click="step.showImageDropZone = true"
                  >
                    Ajouter une image
                  </button>
                  <div
                    v-else
                    class="flex items-start gap-3"
                  >
                    <div>
                      <ImageDropZone
                        accept=".png,.jpg,.jpeg,.webp"
                        :disabled="isSubmitting"
                        @file-selected="handleStepImage(step, $event)"
                      />
                      
                      <p class="text-sm text-gray-500">
                        PNG, JPEG ou WebP — 10 Mo maximum.
                      </p>
                    </div>
                    <button
                      type="button"
                      class="mt-4 shrink-0 rounded-md px-3 py-2 text-gray-600 hover:bg-gray-100"
                      :disabled="isSubmitting"
                      @click="step.showImageDropZone = false"
                    >
                      Annuler
                    </button>
                  </div>
                </div>

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

        <button
          type="submit"
          :disabled="isSubmitting || isLoadingOptions"
          class="w-full rounded-md bg-primary px-4 py-3 font-semibold text-white hover:bg-primary-dark
              disabled:cursor-not-allowed disabled:opacity-50"
        >
          {{ isSubmitting ? 'Enregistrement...' : submitLabel }}
        </button>

        <button
          type="button"
          class="w-full rounded-md border border-gray-300 px-4 py-3
                font-semibold text-gray-700 hover:bg-gray-100
                disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="isSubmitting"
          @click="router.back()"
        >
          Annuler
        </button>

        <p
          v-if="errorMessage"
          role="alert"
          class="rounded-md bg-red-50 p-3 text-red-700"
        >
          {{ errorMessage }}
        </p>

    </form>
</template>
