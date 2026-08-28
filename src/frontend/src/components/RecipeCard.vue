<script setup>
  import { RouterLink } from 'vue-router'

  defineProps({
    recipe: {
      type: Object,
      required: true,
    },
  })
</script>

<template>
  <RouterLink
    :to="{ name: 'recipe-details', params: { id: recipe.id } }"
    class="block h-full rounded-xl"
  >
    <article class="
      flex h-full flex-col overflow-hidden rounded-xl bg-white shadow-md
      transition duration-200
      hover:-translate-y-1
      hover:shadow-xl
      hover:ring-4
     hover:ring-primary
    ">
      <img
        v-if="recipe.imageUrl"
        :src="recipe.imageUrl"
        :alt="`Photo de ${recipe.title}`"
        class="aspect-video w-full object-cover"
      />

      <div
        v-else
        class="flex aspect-video items-center justify-center bg-primary-light"
      >
        Image indisponible
      </div>

      <div class="flex flex-1 flex-col p-5">
        <h2 class="text-xl font-bold text-gray-900">
          {{ recipe.title }}
        </h2>

        <p class="mt-2 line-clamp-2 text-gray-600">
          {{ recipe.description }}
        </p>

        <div class="mt-auto pt-4 flex justify-between text-sm font-semibold text-primary-dark">
          <span>{{ recipe.cookingTime }}</span>
          <span>{{ recipe.likes }} likes</span>
        </div>
      </div>
    </article>
  </RouterLink>
</template>
