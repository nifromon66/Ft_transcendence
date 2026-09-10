<script setup>

import { ref } from 'vue'

const emit = defineEmits(['file-selected'])

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false,
    },
    accept: {
        type: String,
        default: '.png,.jpg,.jpeg,.gif,.webp',
    },
})

const isDragging = ref(false)

const handleDrop = (event) => {
    isDragging.value = false

    if (props.disabled) {
        return
    }

    const files = event.dataTransfer.files
    if (files.length > 0) {
        emit('file-selected', files[0])
    }
}

const handleFileSelect = (event) => {
    const files = event.target.files
    if (files.length > 0) {
        emit('file-selected', files[0])
        event.target.value = ''
    }
}
</script>

<template>
    <div class="w-full max-w-sm my-4">
        <label for="avatar"
            class="block border-2 border-dashed rounded-lg p-6 text-center transition-colors duration-300" :class="[
                disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
                isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
            ]" @dragenter.prevent @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false"
            @drop.stop.prevent="handleDrop">
            <input type="file" id="avatar" name="avatar" ref="fileInput" class="hidden" @change="handleFileSelect"
                :disabled="disabled" accept=".png, .jpg, .jpeg, .gif, .webp" />

            <div class="text-gray-600">
                <p class="mb-1 text-sm">Glissez-déposez un fichier ici</p>
                <span class="text-blue-600 hover:text-blue-700 underline text-xs font-medium">
                    ou parcourir
                </span>
            </div>
        </label>
    </div>
</template>