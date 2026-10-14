<script setup>
defineProps({
  badges: {
    type: Array,
    required: true
  }
})

defineEmits(['claim-badge'])
</script>

<template>
  <section class="badges">
    <div v-for="badge in badges" :key="badge.id" class="badge">
      <h2>{{ badge.name }}</h2>
      <p>{{ badge.description }}</p>
      <button :disabled="!badge.eligible || badge.owned" @click="$emit('claim-badge', badge.id)">
        <span v-if="badge.owned">Already obtained</span>
        <span v-else-if="badge.eligible">Obtain badge</span>
        <span v-else>Not eligible</span>
      </button>
    </div>
  </section>
</template>
