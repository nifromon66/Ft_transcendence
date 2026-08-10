<script setup>
import { ref } from 'vue'

const   emit = defineEmits(['file-dropped'])

const   isDragging = ref(false)
const   fileInput = ref(null)

const triggerFileInput = () => fileInput.value.click()

const handleDrop = (event) => {
    isDragging.value = false
    const files = event.dataTransfer.files
    if (files.length > 0)
    {
        emit ('file-dropped', files[0])
    }
}

const handleFileSelect = (event) => {
    const files = event.target.files
    if (files.length > 0) {
        emit('file-dropped', files[0])
        event.target.value = ''
    }
}
</script>

<template>
    <div class="w-full max-w-sm my-4">
        <div
            class="border-2 border-dashed rounded-lg p-6 text-center transition-colors duration-300 cursor-pointer"
            :class="[
                isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
            ]"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
        >
            <input
                type="file"
                ref="fileInput"
                class="hidden"
                @change="handleFileSelect"
            />

            <div class="text-gray-600">
                <p class="mb-1 text-sm">Glissez-déposez un fichier ici</p>
                <span class="text-blue-600 hover:text-blue-700 underline text-xs font-medium">
                    ou parcourir
                </span>
            </div>
        </div>
    </div>
</template>