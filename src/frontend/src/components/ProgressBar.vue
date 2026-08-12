<script setup>
defineProps({
    progress: {
        type: Number,
        default: 0
    }
})
</script>

<template>
    <div class="mt-4 flex items-center gap-3 w-full max-w-sm">
        <div class="grow h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
                class="h-full bg-blue-500 transition-all duration-200 ease-out"
                :style="{ width: progress + '%' }"
            ></div>
        </div>
        <span class="text-xs font-semibold text-gray-500 w-8 text-right">
            {{ progress }}%
        </span>
    </div>
</template>