<script setup>
import { ref, onUnmounted } from 'vue'
import { validateDocument } from '@/utils/fileValidators';

const emit = defineEmits(['document-ready'])
const selectedDocument = ref(null)
const documentError = ref('')
const fileInput = ref(null)
const documentUrl = ref(null)

const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (!file) {
        return
    }

    const { isValid, error } = validateDocument(file)

    if (!isValid) {
        documentError.value = error
        clearSelection()
        return
    }

    documentError.value = ''
    selectedDocument.value = file

    if (documentUrl.value)
        URL.revokeObjectURL(documentUrl.value)

    documentUrl.value = URL.createObjectURL(file)

    emit('document-ready', file)
}

const clearSelection = () => {
    selectedDocument.value = null
    documentError.value = ''
    if (fileInput.value) {
        fileInput.value.value = ''
    }

    if (documentUrl.value) {
        URL.revokeObjectURL(documentUrl.value)
        documentUrl.value = null
    }

    emit('document-ready', null)
}

onUnmounted(() => {
    if (documentUrl.value) {
        URL.revokeObjectURL(documentUrl.value)
    }
})
</script>

<template>
    <div class="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-4 shadow-sm">

        <div v-if="!selectedDocument" class="flex flex-col items-center">
            <button @click="fileInput.click()"
                class="flex items-center space-x-2 rounded-lg bg-blue-50 px-4 py-2 text-blue-600 transition-colors hover:bg-blue-100">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                <span class="text-sm font-medium">Joindre un PDF</span>
            </button>
            <input type="file" ref="fileInput" class="hidden" accept=".pdf" @change="handleFileSelect" />
        </div>

        <div v-else class="flex items-center justify-between rounded-lg bg-gray-50 p-3 border border-gray-200">
            <div class="flex items-center space-x-3 overflow-hidden">
                <svg class="h-8 w-8 shrink-0 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <path
                        d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z">
                    </path>
                </svg>
                <div class="flex flex-col truncate">
                    <span class="truncate text-sm font-semibold text-gray-700">{{ selectedDocument.name }}</span>
                    <span class="text-xs text-gray-500">{{ (selectedDocument.size / 1024 / 1024).toFixed(2) }} Mo</span>
                </div>
            </div>

            <div class="flex space-x-1 shrink-0 ml-2">
                <a :href="documentUrl" target="_blank" title="Ouvrir le document"
                    class="rounded-full p-1 text-gray-400 hover:bg-blue-100 hover:text-blue-600 transition-colors">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
                    </svg>
                </a>

                <button @click="clearSelection" title="Retirer"
                    class="rounded-full p-1 text-gray-400 hover:bg-red-100 hover:text-red-600 transition-colors">
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12">
                        </path>
                    </svg>
                </button>
            </div>
        </div>

        <p v-if="documentError" class="mt-2 text-center text-xs text-red-500">{{ documentError }}</p>
    </div>
</template>