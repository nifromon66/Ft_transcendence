<script setup>
import termsText from '../assets/terms_&_privacy/Terms.txt?raw'
</script>

<template>
  <main class="mx-auto w-full max-w-4xl px-6 py-10">
    <h1 class="mb-6 text-3xl font-bold text-black">
      Conditions générales d'utilisation
    </h1>

    <div class="whitespace-pre-line rounded-lg bg-white p-6 leading-relaxed text-gray-800 shadow">
      {{ termsText }}
    </div>
  </main>
</template>