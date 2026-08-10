<script setup>
    import { RouterLink } from 'vue-router'
    import siteLogo from '../assets/path1.svg'

    const emit = defineEmits(['select'])
</script>

<template>
  <RouterLink
    :to="{ name: 'welcome' }"
    class="flex items-center gap-1 rounded-lg px-0.5 py-1 text-lg text-white transition-colors hover:bg-primary-dark"
    @click="emit('select')"
  >
    <img
      :src="siteLogo"
      alt=""
      class="h-8 w-8"
    />

    <span>Nom du Site</span>
  </RouterLink>
</template>