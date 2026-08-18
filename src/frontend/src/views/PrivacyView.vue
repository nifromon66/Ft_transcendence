<script setup>
import privacyText from '../assets/temp_assets/Privacy.txt?raw'
</script>

<template>
  <main class="mx-auto w-full max-w-4xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-black">
      Politique de confidentialité
    </h1>

    <div class="whitespace-pre-line rounded-lg bg-white p-6 leading-relaxed text-gray-800 shadow">
      {{ privacyText }}
    </div>
  </main>
</template>