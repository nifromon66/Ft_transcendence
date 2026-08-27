<script setup>
import { ref } from 'vue'
import DocumentUpload from '@/components/DocumentUpload.vue'

const currentDocument = ref(null)

const handleDocumentReady = (file) => {
    currentDocument.value = file
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
        </div>
    </main>
</template>