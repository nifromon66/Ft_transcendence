<script setup>
import { onMounted, ref } from 'vue'

const badges = ref([])
const errorMessage = ref('')

async function loadBadges() {
  errorMessage.value = ''
  const response = await fetch('/api/badges', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })

  if (!response.ok) {
    errorMessage.value = 'Impossible de charger les badges.'
    return
  }

  badges.value = await response.json()
}

async function claimBadge(badgeId) {
  const response = await fetch('/api/getbadge', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ badge_id: badgeId }),
  })
//   .then(async response => {
//     console.log("status:", response.status);
//     console.log("body:", await response.text());
// });

  if (!response.ok) {
    errorMessage.value = await response.text()
    return
  }

  await loadBadges()
}

onMounted(loadBadges)
</script>

<template>
  <section class="badges">
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <div v-for="badge in badges" :key="badge.id" class="badge">
      <h2>{{ badge.name }}</h2>
      <p>{{ badge.description }}</p>
      <button :disabled="!badge.eligible || badge.owned" @click="claimBadge(badge.id)">
        <span v-if="badge.owned">Already obtained</span>
        <span v-else-if="badge.eligible">Obtain badge</span>
        <span v-else>Not eligible</span>
      </button>
    </div>
  </section>
</template>
