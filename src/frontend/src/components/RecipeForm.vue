<script setup>
import { onMounted, ref } from 'vue'
import {
  createIngredient,
  fetchCategories,
  fetchIngredients,
  fetchIngredientCategories,
  fetchTags,
} from '@/services/recipeService.js'
import { useRecipeForm } from '@/composables/useRecipeForm.js'
import { formatRecipeForApi } from '@/utils/recipeMapper.js'
import ImageDropZone from '@/components/ImageDropZone.vue'
import ImagePreview from '@/components/ImagePreview.vue'
import { useAuthStore } from '@/stores/authState'

const authStore = useAuthStore()
const isCreatingIngredient = ref(false)

const saveNewIngredient = async (ingredient) => {
  if (isCreatingIngredient.value || props.isSubmitting) return
  const name = ingredient.newName?.trim()
  if (!name || name.length > 100) {
    ingredient.creationError = 'Saisis un nom de 1 à 100 caractères.'
    return
  }
  ingredient.creationError = ''
  isCreatingIngredient.value = true
  try {
    try {
      await authStore.silentRefresh()
    } catch {
      // Ignore silent refresh failure; createIngredient will handle auth errors
    }
    const data = await createIngredient(authStore.token, {
      name,
      category_id: Number(ingredient.categoryId),
    })

    const newIngredient = data.ingredient || data

    ingredientOptions.value.push(newIngredient)

    ingredient.ingredientId = newIngredient.id

    ingredient.newName = ''
  } catch (error) {
    ingredient.creationError = error.message || 'Impossible de créer l’ingrédient.'
  } finally {
    isCreatingIngredient.value = false
  }
}

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

const emit = defineEmits(['submit', 'cancel'])

const {
  recipe,
  errorMessage,
  recipeImageFile,
  existingRecipeImageUrl,
  shouldDeleteRecipeImage,
  showRecipeImageDropZone,
  handleRecipeImage,
  removeExistingRecipeImage,
  clearRecipeImage,
  addStep,
  removeStep,
  handleStepImage,
  clearStepImage,
  removeExistingStepImage,
  addIngredient,
  removeIngredient,
  isIngredientSelected,
  addTag,
  removeTag,
  isTagSelected
} = useRecipeForm(props.initialRecipe)

const categories = ref([])

const ingredientOptions = ref([])

const ingredientCategories = ref([])

const ingredientsForCategory = (categoryId) => {
  if (!categoryId) return []
  return ingredientOptions.value.filter((option) =>
    Number(option.category_id || option.categoryId) === Number(categoryId)
  )
}

const tagOptions = ref([])

const isLoadingOptions = ref(true)

const fetchErrorMessage = ref('')

const submitForm = () => {
  if (isCreatingIngredient.value || props.isSubmitting) return

  if (recipe.ingredients.some((ingredient) => ingredient.ingredientId === 'new')) {
    errorMessage.value = 'Crée le nouvel ingrédient ou sélectionne un ingrédient existant.'
    return
  }
  errorMessage.value = ''

  if (!recipe.title || !recipe.categoryId) {
    errorMessage.value = "Le titre et la catégorie sont obligatoires."
    return
  }

  if (!recipe.steps || recipe.steps.length === 0 || recipe.steps.some(s => !s.description.trim())) {
    errorMessage.value = "Chaque étape doit avoir une description."
    return
  }

  if (!recipe.ingredients || recipe.ingredients.length === 0 || recipe.ingredients.some(i => !i.ingredientId || !i.quantity.trim())) {
    errorMessage.value = "Tous les ingrédients doivent être sélectionnés et avoir une quantité (ex: '200g')."
    return
  }

  if (!recipe.tags || recipe.tags.some(t => !t.tagId)) {
    errorMessage.value = "Tous les tags doivent être sélectionnés."
    return
  }

  const { recipeData, stepImageChanges } = formatRecipeForApi(recipe)

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
    const loadedCategories = await fetchCategories()
    const [
      loadedIngredients,
      loadedIngredientCategories,
      loadedTags,
    ] = await Promise.all([
      fetchIngredients(),
      fetchIngredientCategories(),
      fetchTags(),
    ])

    categories.value = loadedCategories
    ingredientOptions.value = loadedIngredients
    ingredientCategories.value = loadedIngredientCategories
    tagOptions.value = loadedTags

    for (const ingredient of recipe.ingredients) {
      if (ingredient.ingredientId) {
        const matchedOption = loadedIngredients.find(
          (option) => Number(option.id) === Number(ingredient.ingredientId),
        )

        if (matchedOption) {
          ingredient.categoryId = matchedOption.category_id ?? matchedOption.categoryId ?? ingredient.categoryId ?? ''
        }
      }
    }
  } catch (error) {
    fetchErrorMessage.value =
      error.message || 'Impossible de charger les options du formulaire.'
  } finally {
    isLoadingOptions.value = false
  }
})
</script>

<template>
  <form class="space-y-8" @submit.prevent="submitForm">
    <section aria-labelledby="main-information-title" class="bg-white p-6 rounded-xl shadow-md">
      <h2 id="main-information-title" class="mb-4 text-xl font-semibold">
        Informations principales
      </h2>

      <div class="space-y-4">
        <div>
          <label for="recipe-title" class="mb-1 block font-medium">
            Titre
          </label>
          <input id="recipe-title" name="title" v-model.trim="recipe.title" type="text" required maxlength="150"
            placeholder="Ex. Soupe de légumes" class="w-full resize-none rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200" />
        </div>

        <div>
          <label for="recipe-category" class="mb-1 block font-medium">
            Catégorie
          </label>
          <select id="recipe-category" name="category" v-model="recipe.categoryId" required :disabled="isLoadingOptions"
            class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:cursor-wait
                    disabled:bg-gray-100">
            <option disabled value="">
              {{ isLoadingOptions ? 'Chargement des catégories...' : 'Choisir une catégorie' }}
            </option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div>
          <label for="recipe-description" class="mb-1 block font-medium">
            Description
          </label>
          <textarea id="recipe-description" name="description" v-model.trim="recipe.description" rows="2"
            maxlength="150" @keydown.enter.prevent placeholder="Présente brièvement ta recette..." class="w-full resize-none rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200" />
          <p class="mt-1 text-right text-sm text-gray-500">
            {{ recipe.description.length }}/150 caractères
          </p>
        </div>
        <div>
          <p class="mb-1 block font-medium">
            Image de la recette (facultatif)
          </p>

          <ImagePreview v-if="recipeImageFile" :file="recipeImageFile" :disabled="isSubmitting"
            @clear="clearRecipeImage" />

          <div v-else-if="existingRecipeImageUrl" class="my-4 w-full max-w-sm">
            <img :src="existingRecipeImageUrl" alt="Image actuelle de la recette"
              class="h-48 w-full rounded-lg object-cover" />

            <button type="button" class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
              :disabled="isSubmitting" @click="removeExistingRecipeImage">
              Supprimer l’image
            </button>
          </div>

          <button v-else-if="!showRecipeImageDropZone" type="button" class="rounded-md border border-primary px-3 py-2 font-medium
                    text-primary-dark hover:bg-primary-light" :disabled="isSubmitting"
            @click="showRecipeImageDropZone = true">
            Ajouter une image
          </button>
          <div v-else class="flex items-start gap-3">
            <div>
              <ImageDropZone accept=".png,.jpg,.jpeg,.webp" :disabled="isSubmitting"
                @file-selected="handleRecipeImage" />
              <p class="text-sm text-gray-500">
                PNG, JPEG ou WebP — 10 Mo maximum.
              </p>
            </div>
            <button type="button" class="mt-4 shrink-0 rounded-md px-3 py-2 text-gray-600 hover:bg-gray-100"
              :disabled="isSubmitting" @click="showRecipeImageDropZone = false">
              Annuler
            </button>
          </div>
        </div>
      </div>
    </section>

    <section aria-labelledby="preparation-title" class="bg-white p-6 rounded-xl shadow-md">
      <h2 id="preparation-title" class="mb-4 text-xl font-semibold">
        Préparation
      </h2>

      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label for="recipe-cooking-time" class="mb-1 block font-medium">
            Temps de préparation (minutes)
          </label>
          <input id="recipe-cooking-time" name="cookingTime" v-model.number="recipe.cookingTime" type="number" min="0"
            step="1" placeholder="Ex. 30" class="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200" />
        </div>

        <div>
          <label for="recipe-difficulty" class="mb-1 block font-medium">
            Difficulté
          </label>
          <select id="recipe-difficulty" name="difficulty" v-model="recipe.difficulty" class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200">
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
          <div v-for="(step, index) in recipe.steps" :key="step.id" class="rounded-md border border-gray-200 p-4">
            <label :for="`recipe-step-${step.id}`" class="mb-1 block font-medium">
              Étape {{ index + 1 }}
            </label>

            <textarea :id="`recipe-step-${step.id}`" :name="`recipe-step-${step.id}`" v-model.trim="step.description"
              rows="3" required placeholder="Décris cette étape de la préparation..." class="w-full resize-none rounded-md border border-gray-300 px-3 py-2
                      focus:border-blue-500 focus:outline-none focus:ring-2
                      focus:ring-blue-200" />
            <div class="mt-3">
              <p class="mb-1 text-sm font-medium">
                Image de l’étape (facultatif)
              </p>

              <ImagePreview v-if="step.imageFile" :file="step.imageFile" :disabled="isSubmitting"
                @clear="clearStepImage(step)" />

              <div v-else-if="step.imageUrl" class="my-4 w-full max-w-sm">
                <img :src="step.imageUrl" :alt="`Image actuelle de l'étape ${index + 1}`"
                  class="h-36 w-full rounded-lg object-cover" />

                <button type="button" class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
                  :disabled="isSubmitting" @click="removeExistingStepImage(step)">
                  Supprimer l’image de l’étape
                </button>
              </div>

              <button v-else-if="!step.showImageDropZone" type="button" class="rounded-md border border-primary px-3 py-2 text-sm font-medium
                        text-primary-dark hover:bg-primary-light" :disabled="isSubmitting"
                @click="step.showImageDropZone = true">
                Ajouter une image
              </button>
              <div v-else class="flex items-start gap-3">
                <div>
                  <ImageDropZone accept=".png,.jpg,.jpeg,.webp" :disabled="isSubmitting"
                    @file-selected="handleStepImage(step, $event)" />

                  <p class="text-sm text-gray-500">
                    PNG, JPEG ou WebP — 10 Mo maximum.
                  </p>
                </div>
                <button type="button" class="mt-4 shrink-0 rounded-md px-3 py-2 text-gray-600 hover:bg-gray-100"
                  :disabled="isSubmitting" @click="step.showImageDropZone = false">
                  Annuler
                </button>
              </div>
            </div>

            <button v-if="recipe.steps.length > 1" type="button"
              class="mt-2 rounded-md px-3 py-2 text-red-600 hover:bg-red-50" @click="removeStep(index)">
              Retirer cette étape
            </button>
          </div>
        </div>

        <button type="button" class="mt-3 rounded-md border border-primary px-3 py-2
                    font-medium text-primary-dark hover:bg-primary-light" @click="addStep">
          Ajouter une étape
        </button>
      </div>
    </section>

    <section aria-labelledby="ingredients-title" class="bg-white p-6 rounded-xl shadow-md">
      <h2 id="ingredients-title" class="mb-4 text-xl font-semibold">
        Ingrédients
      </h2>

      <fieldset :disabled="isCreatingIngredient || isSubmitting" class="space-y-3">
        <div v-for="(ingredient, index) in recipe.ingredients" :key="ingredient.id"
          class="grid gap-2 sm:grid-cols-[1fr_1fr_1fr_auto]">
          <select :id="`ingredient-cat-${index}`" :name="`ingredient-cat-${index}`" v-model="ingredient.categoryId"
            required :disabled="isLoadingOptions" :aria-label="`Catégorie de l'ingrédient ${index + 1}`"
            class="rounded-md border border-gray-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-200"
            @change="ingredient.ingredientId = ''; ingredient.creationError = ''">
            <option disabled value="">Choisir une catégorie</option>
            <option v-for="category in ingredientCategories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>

          <select :id="`ingredient-item-${index}`" :name="`ingredient-item-${index}`" v-if="ingredient.categoryId"
            v-model="ingredient.ingredientId" required :aria-label="`Ingrédient ${index + 1}`" class="rounded-md border border-gray-300 bg-white px-3 py-2
                    focus:border-blue-500 focus:outline-none focus:ring-2
                    focus:ring-blue-200">
            <option disabled value="">
              Choisir un ingrédient
            </option>

            <option v-for="ingredientOption in ingredientsForCategory(ingredient.categoryId)" :key="ingredientOption.id"
              :value="ingredientOption.id" :disabled="isIngredientSelected(ingredientOption.id, index)">
              {{ ingredientOption.name }}
            </option>
            <option value="new">Ajouter un nouvel ingrédient</option>
          </select>
          <input :id="`ingredient-qty-${index}`" :name="`ingredient-qty-${index}`" v-model.trim="ingredient.quantity"
            type="text" :aria-label="`Quantité de l'ingrédient ${index + 1}`" placeholder="Ex. 3 ou 250 g" class="rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500
                    focus:outline-none focus:ring-2 focus:ring-blue-200" />
          <button v-if="recipe.ingredients.length > 1" type="button"
            class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50" @click="removeIngredient(index)">
            Retirer
          </button>
          <div v-if="ingredient.ingredientId === 'new'" class="space-y-2 sm:col-span-full">
            <label :for="`new-ingredient-${ingredient.id}`" class="block font-medium">
              Nom du nouvel ingrédient
            </label>
            <div class="flex gap-2">
              <input :id="`new-ingredient-${ingredient.id}`" :name="`new-ingredient-${ingredient.id}`"
                v-model.trim="ingredient.newName" type="text" maxlength="100" placeholder="Ex. Topinambour"
                class="min-w-0 flex-1 rounded-md border border-gray-300 bg-white text-black px-3 py-2"
                @keydown.enter.prevent="saveNewIngredient(ingredient)" />
              <button type="button" class="rounded-md bg-primary px-3 py-2 text-white disabled:opacity-50"
                @click="saveNewIngredient(ingredient)">
                {{ isCreatingIngredient ? 'Création...' : 'Créer' }}
              </button>
            </div>
            <p v-if="ingredient.creationError" role="alert" class="text-sm text-red-600">
              {{ ingredient.creationError }}
            </p>
          </div>
        </div>
      </fieldset>

      <button type="button"
        class="mt-3 rounded-md border border-primary px-3 py-2 font-medium text-primary-dark hover:bg-primary-light"
        @click="addIngredient">
        Ajouter un ingrédient
      </button>
    </section>

    <section aria-labelledby="tags-title" class="bg-white p-6 rounded-xl shadow-md">
      <h2 id="tags-title" class="mb-4 text-xl font-semibold">Tags</h2>

      <div class="space-y-3">
        <div v-for="(tag, index) in recipe.tags" :key="tag.id" class="flex gap-2">
          <select :id="`tag-${index}`" :name="`tag-${index}`" v-model="tag.tagId" required
            :aria-label="`Tag ${index + 1}`" class="min-w-0 flex-1 rounded-md border border-gray-300
                    bg-white px-3 py-2 focus:border-blue-500
                      focus:outline-none focus:ring-2 focus:ring-blue-200">
            <option disabled value="">
              Choisir un tag
            </option>

            <option v-for="tagOption in tagOptions" :key="tagOption.id" :value="tagOption.id"
              :disabled="isTagSelected(tagOption.id, index)">
              {{ tagOption.name }}
            </option>
          </select>

          <button v-if="recipe.tags.length > 1" type="button" class="rounded-md px-3 py-2 text-red-600 hover:bg-red-50"
            @click="removeTag(index)">
            Retirer
          </button>
        </div>
      </div>

      <button type="button" class="mt-3 rounded-md border border-primary px-3 py-2
                font-medium text-primary-dark hover:bg-primary-light" @click="addTag">
        Ajouter un tag
      </button>
    </section>

    <section class="bg-white p-6 rounded-xl shadow-md space-y-3">
      <button type="submit" :disabled="isSubmitting || isLoadingOptions || isCreatingIngredient" class="w-full rounded-md bg-primary px-4 py-3 font-semibold text-white hover:bg-primary-dark
                disabled:cursor-not-allowed disabled:opacity-50">
        {{ isSubmitting ? 'Enregistrement...' : submitLabel }}
      </button>

      <button type="button" class="w-full rounded-md border border-gray-300 px-4 py-3
                  font-semibold text-gray-700 hover:bg-gray-100
                  disabled:cursor-not-allowed disabled:opacity-50" :disabled="isSubmitting" @click="$emit('cancel')">
        Annuler
      </button>

      <p v-if="errorMessage || fetchErrorMessage" role="alert" class="rounded-md bg-red-50 p-3 text-red-700">
        {{ errorMessage || fetchErrorMessage }}
      </p>
    </section>

  </form>
</template>