<script setup>
import { useId } from 'vue'

const groupName = useId()

const props = defineProps({
  rating: {
    type: Number,
    default: 0,
  },
  interactive: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:rating'])

function fillPercentage(index) {
  return Math.max(0, Math.min(1, props.rating - index)) * 100
}
</script>

<template>
    <fieldset v-if="interactive" class="inline-flex gap-1" :disabled="disabled">
        <label v-for="score in 5" :key="score" class="cursor-pointer">
            <input
            type="radio"
            class="peer sr-only"
            :name="groupName"
            :value="score"
            :checked="rating === score"
            :aria-label="`${score} sur 5`"
            @change="emit('update:rating', score)"
            />

            <svg
            viewBox="0 0 24 24"
            stroke="black"
            stroke-width="1"
            stroke-linejoin="round"
            aria-hidden="true"
            class="h-6 w-6 peer-focus-visible:outline-2 peer-focus-visible:outline-primary"
            :class="rating >= score ? 'fill-amber-400' : 'fill-gray-400'"
            >
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
        </label>
    </fieldset>

  <span v-else role="img" :aria-label="`Note : ${rating} sur 5`">
    <span
      v-for="index in 5"
      :key="index"
      aria-hidden="true"
      class="relative inline-block h-6 w-6"
    >
      <svg viewBox="0 0 24 24" 
            class="h-6 w-6 fill-gray-400"
            stroke="black"
            stroke-width="1"
            stroke-linejoin="round"
            aria-hidden="true"
        >
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
      </svg>

      <span
        class="absolute inset-y-0 left-0 overflow-hidden"
        :style="{ width: `${fillPercentage(index - 1)}%` }"
      >
        <svg viewBox="0 0 24 24"
            class="h-6 w-6 fill-amber-400"
            stroke="black"
            stroke-width="1"
            stroke-linejoin="round"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </span>
    </span>
  </span>
</template>

