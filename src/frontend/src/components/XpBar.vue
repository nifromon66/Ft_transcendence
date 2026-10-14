<script setup>
import { computed, ref, useId } from 'vue'

// Progress is supplied by the API: total, level, current, required, next_level_xp.
defineProps({
    progress: {
        type: Object,
        required: true,
    },
})

const tooltipId = useId()
const isHovered = ref(false)
const isFocused = ref(false)
const isDismissed = ref(false)
const showTooltip = computed(() => (isHovered.value || isFocused.value) && !isDismissed.value)

const openOnHover = () => {
    isHovered.value = true
    isDismissed.value = false
}

const openOnFocus = () => {
    isFocused.value = true
    isDismissed.value = false
}
</script>

<template>
    <div class="relative w-full cursor-help rounded-lg text-center focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-indigo-600"
        tabindex="0" role="group" :aria-label="`Expérience : niveau ${progress.level}`"
        :aria-describedby="showTooltip ? tooltipId : undefined" @mouseenter="openOnHover"
        @mouseleave="isHovered = false" @focus="openOnFocus" @blur="isFocused = false"
        @keydown.esc.stop="isDismissed = true">
        <p class="text-sm font-bold text-gray-800">Niveau {{ progress.level }}</p>
        <progress
            class="mt-2 block h-3 w-full overflow-hidden rounded-full [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-indigo-600 [&::-moz-progress-bar]:bg-indigo-600"
            :value="progress.current" :max="progress.required"
            :aria-label="`Progression vers le niveau ${progress.level + 1}`"
            :aria-valuetext="`${progress.current} XP sur ${progress.required}`"></progress>
        <p class="mt-2 text-xs text-gray-600">
            {{ progress.current }} / {{ progress.required }} XP
        </p>
        <p class="mt-1 text-xs text-gray-500">
            {{ progress.total }} XP au total · Niveau {{ progress.level + 1 }} à {{ progress.next_level_xp }} XP
        </p>

        <div v-if="showTooltip" :id="tooltipId" role="tooltip"
            class="absolute bottom-full left-1/2 z-20 w-64 max-w-[calc(100vw-2rem)] -translate-x-1/2 pb-2 text-left">
            <div class="rounded-lg bg-gray-900 p-4 text-xs leading-relaxed text-white shadow-lg">
                <p class="mb-2 font-semibold">Comment gagner de l’expérience ?</p>
                <p>Publier une recette te fait gagner 30xp.</p>
                <p>Noter une recette te fait gagner 5xp.</p>
            </div>
        </div>
    </div>
</template>