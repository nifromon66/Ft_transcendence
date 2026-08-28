<script setup>
import { ref } from 'vue'
import DocumentUpload from '@/components/DocumentUpload.vue'
import { uploadDocument } from '@/services/uploadService'

const currentDocument = ref(null)
const progress = ref(0)
const isUploading = ref(false)
const uploadMessage = ref('')
const isSuccess = ref(false)

const handleDocumentReady = (file) => {
    currentDocument.value = file
    uploadMessage.value = ''
    progress.value = 0
}

const handleUploadToServer = async () => {
    if (!currentDocument.value) {
        return
    }

    const token = localStorage.getItem('token')
    if (!token) {
        uploadMessage.value = "Veuillez vous connecter pour envoyer un document."
        isSuccess.value = false
        return
    }

    isUploading.value = true
    uploadMessage.value = ''
    progress.value = 0

    try {
        const result = await uploadDocument(token, currentDocument.value, (p) => {
            progress.value = p
        })
        uploadMessage.value = `Document envoyé sur le serveur : ${result.filename}`
        isSuccess.value = true
    } catch (error) {
        uploadMessage.value = error.message
        isSuccess.value = false
    } finally {
        isUploading.value = false
    }
}

</script>

<template>
    <main class="flex-1 px-6 py-8">
        <div class="mx-auto mt-10 max-w-xl rounded-xl bg-white p-8 shadow-lg">
            <h1 class="mb-6 border-b pb-4 text-2xl font-bold text-gray-800">Test - Composant Document</h1>

            <p class="mb-6 text-sm text-gray-600">
                Sélectionnez un PDF.
            </p>

            <DocumentUpload @document-ready="handleDocumentReady"></DocumentUpload>

            <div v-if="currentDocument" class="mt-8 rounded-lg bg-green-50 p-4 border border-green-200">
                <h2 class="text-sm font-bold text-green-800 mb-2">Prêt pour l'envoi sur le serveur :</h2>
                <ul class="text-sm text-green-700 space-y-1">
                    <li><strong>Nom :</strong> {{ currentDocument.name }}</li>
                    <li><strong>Type :</strong> {{ currentDocument.type }}</li>
                    <li><strong>Taille :</strong> {{ currentDocument.size }} octets</li>
                </ul>
            </div>

            <div v-if="isUploading || progress > 0" class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    :style="{ width: `${progress}%` }"></div>
            </div>
            <div v-if="isUploading" class="text-xs text-right text-gray-500">{{ progress }}%</div>

            <button v-if="currentDocument" @click="handleUploadToServer" :disabled="isUploading"
                class="w-full py-2 px-4 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
                {{ isUploading ? "Envoi en cours..." : "Envoyer le pdf sur le serveur" }}
            </button>
        </div>

        <div v-if="uploadMessage"
            :class="isSuccess ? 'text-green-600 bg-green-50 border-green-200' : 'text-red-600 bg-red-50 border-red-200'"
            class="mt-4 p-3 rounded-lg border text-sm font-medium">
            {{ uploadMessage }}
        </div>
    </main>
</template>