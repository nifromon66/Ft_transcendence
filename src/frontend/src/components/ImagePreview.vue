<script setup>
import {ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { formatFileSize } from '@/utils/formatters'

const props = defineProps({
    file: {
        type: File,
        required: true
    },
    disabled: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['clear'])

const previewUrl = ref(null)

onMounted(() => {
    if (props.file) {
        previewUrl.value = URL.createObjectURL(props.file)
    }
})

onBeforeUnmount(() => {
    if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
    }
})

watch(() => props.file, (newFile) => {
    if (previewUrl.value) {
        URL.revokeObjectURL(previewUrl.value)
    }
    if (newFile) {
        previewUrl.value = URL.createObjectURL(newFile)
    } else {
        previewUrl.value = null
    }
})

const handleClear = () => {
    if (!props.disabled) {
        emit('clear')
    }
}

</script>

<template>
    <div class="w-full max-w-sm my-4 flex items-center gap-4 p-3 border border-gray-200 rounded-lg bg-white shadow-sm transition-all">

        <img
            v-if="previewUrl"
            :src="previewUrl"
            alt="Aperçu"
            class="w-12 h-12 object-cover rounded-full border border-gray-300"
        />
        <div class="flex-1 overflow-hidden">
            <p class="text-sm font-medium text-gray-700 truncate">{{ file.name }}</p>
            <p class="text-xs text-gray-500">({{ formatFileSize(file.size) }})</p>
        </div>
        
        <button
            type="button"
            @click="handleClear"
            :disabled="disabled"
            class="p-2 text-gray-400 hover:text-red-500 transition-colors focus:outline-none"
            :class="{ 'opacity-50 cursor-not-allowed hover:text-gray-400': disabled }"
            title="Retirer l'image"
        >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
    </button>

    </div>
</template>