<script setup>
import { onMounted, ref } from 'vue'
import { fetchBadges, claimBadgeApi } from '@/services/badgeService.js'
import BadgeList from '@/components/BadgeList.vue'

const badges = ref([])
const errorMessage = ref('')

async function loadBadges() {
  errorMessage.value = ''
  try {
    badges.value = await fetchBadges()
  } catch (err) {
    errorMessage.value = err.message || 'Une erreur réseau est survenue.'
  }
}

async function claimBadge(badgeId) {
  errorMessage.value = ''
  try {
    await claimBadgeApi(badgeId)
    await loadBadges()
  } catch (err) {
    errorMessage.value = err.message || 'Une erreur est survenue lors de la réclamation du badge.'
  }
}

onMounted(loadBadges)
</script>

<template>
  <main class="p-8">
    <h1 class="mb-6 text-2xl font-bold">Mes badges</h1>
    <p v-if="errorMessage" class="mb-4 text-red-600 font-medium">
      {{ errorMessage }}
    </p>
    <BadgeList :badges="badges" @claim-badge="claimBadge" />
  </main>
</template>
