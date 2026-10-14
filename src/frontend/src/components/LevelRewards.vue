<script setup>
import { ref, useId } from 'vue'
import AvatarFrame from '@/components/AvatarFrame.vue'

const props = defineProps({
    rewards: { type: Array, required: true },
    selected: { type: String, default: null },
    editable: { type: Boolean, default: false },
    saving: { type: Boolean, default: false },
    error: { type: String, default: '' },
})
const emit = defineEmits(['select'])
const tooltipId = useId()
const hovered = ref(null)
const focused = ref(null)
const dismissed = ref(false)

function selectReward(event, reward) {
    const next = event.target.checked ? reward.id : null
    event.target.checked = props.selected === reward.id
    emit('select', next)
}
</script>

<template>
    <section class="mx-auto mt-6 max-w-2xl rounded-xl bg-white p-8 shadow-lg" :aria-busy="saving">
        <h2 class="mb-4 border-b pb-4 text-xl font-bold text-gray-800">Récompenses de niveau</h2>
        <p v-if="editable" class="mb-5 text-sm text-gray-500">Choisissez un cercle pour votre avatar. Un seul cercle
            peut être actif.</p>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div v-for="reward in rewards" :key="reward.id"
                class="relative rounded-lg border p-4 focus-visible:outline-2 focus-visible:outline-indigo-600"
                :class="selected === reward.id ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200'" tabindex="0"
                role="group" :aria-label="`Cercle ${reward.name}`" :aria-describedby="`${tooltipId}-${reward.id}`"
                @mouseenter="hovered = reward.id; dismissed = false" @mouseleave="hovered = null"
                @focusin="focused = reward.id; dismissed = false" @focusout="focused = null"
                @keydown.esc.stop="dismissed = true">
                <label class="flex items-center justify-center gap-4"
                    :class="editable && reward.unlocked && !saving ? 'cursor-pointer' : 'cursor-default'">
                    <span class="relative m-1 inline-flex h-12 w-12 shrink-0 rounded-full bg-white">
                        <AvatarFrame :frame="reward.id" :locked="!reward.unlocked" />
                    </span>
                    <input type="checkbox" class="h-4 w-4 accent-indigo-600" :checked="selected === reward.id"
                        :disabled="!editable || !reward.unlocked || saving"
                        :aria-label="`Afficher le cercle ${reward.name}`"
                        :aria-describedby="`${tooltipId}-${reward.id}`" @change="selectReward($event, reward)" />
                </label>
                <p class="mt-3 text-center text-sm font-semibold"
                    :class="reward.unlocked ? 'text-gray-800' : 'text-gray-400'">{{ reward.name }}</p>
                <p class="mt-1 text-center text-xs text-gray-500">{{ reward.unlocked ? 'Débloqué' : `Niveau
                    ${reward.required_level}` }}</p>
                <div :id="`${tooltipId}-${reward.id}`" role="tooltip"
                    :class="!dismissed && (hovered === reward.id || focused === reward.id) ? 'absolute bottom-full left-1/2 z-20 w-max -translate-x-1/2 pb-2' : 'sr-only'">
                    <p class="rounded-lg bg-gray-900 px-3 py-2 text-xs text-white shadow-lg">Débloqué au niveau {{
                        reward.required_level }}</p>
                </div>
            </div>
        </div>
        <p v-if="saving" class="mt-4 text-sm text-gray-500" role="status">Enregistrement…</p>
        <p v-if="error" class="mt-4 text-sm text-red-600" role="alert">{{ error }}</p>
    </section>
</template>
