<script setup>
const badgeLogos = import.meta.glob('../assets/badges/*', {
  eager: true,
  query: '?url',
  import: 'default'
})

const logoFor = (filename) => {
  if (!filename) return undefined
  const entry = Object.entries(badgeLogos).find(([path]) => path.endsWith(`/${filename}`))
  return entry?.[1]
}

defineProps({
  badges: {
    type: Array,
    required: true
  },
  canClaim: {
    type: Boolean,
    default: true
  }
})

defineEmits(['claim-badge'])
</script>

<template>
  <section v-if="badges.length" class="grid gap-4 sm:grid-cols-2">
    <article v-for="badge in badges" :key="badge.id"
      class="flex flex-col justify-between rounded-xl border border-gray-200 bg-gray-50 p-5">
      <div>
        <div class="flex items-center gap-3">
          <img v-if="logoFor(badge.logo_filename)" :src="logoFor(badge.logo_filename)" :alt="`${badge.name} logo`"
            class="h-12 w-12 shrink-0 object-contain" />
          <h3 class="text-lg font-semibold text-gray-800">{{ badge.name }}</h3>
        </div>
        <p class="mt-2 text-sm text-gray-600">{{ badge.description }}</p>
      </div>
      <button :disabled="!canClaim || !badge.eligible || badge.owned" @click="$emit('claim-badge', badge.id)"
        class="mt-5 self-start rounded-lg px-4 py-2 text-sm font-semibold transition-colors disabled:cursor-not-allowed"
        :class="canClaim && badge.eligible && !badge.owned
          ? 'bg-primary text-white hover:bg-primary-dark'
          : 'bg-gray-200 text-gray-500'">
        <span v-if="badge.owned">Déjà obtenu</span>
        <span v-else-if="badge.eligible">Réclamer le badge</span>
        <span v-else>Pas encore débloqué</span>
      </button>
    </article>
  </section>
  <p v-else class="text-sm text-gray-500">Aucun badge disponible pour le moment.</p>
</template>
