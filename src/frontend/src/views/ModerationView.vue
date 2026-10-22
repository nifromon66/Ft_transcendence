<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { adminRequest } from '@/services/adminService'
import { useAuthStore } from '@/stores/authState'

const auth = useAuthStore()
const kind = ref('recipes')
const items = ref([])
const pagination = ref({ page: 1, per_page: 20, total: 0 })
const busy = ref(false)
const error = ref('')
const itemToRemove = ref(null)

async function load(page = 1) {
  const data = await adminRequest(`/moderation?kind=${kind.value}&page=${page}`)
  items.value = data.items
  pagination.value = data.pagination
}
async function run(action) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try { await action() } catch (err) { error.value = err.message }
  finally { busy.value = false }
}
function remove(item) {
  itemToRemove.value = item
}
async function confirmRemove() {
  const item = itemToRemove.value
  itemToRemove.value = null
  if (!item) return
  await run(async () => {
    if (kind.value === 'recipes') {
      await adminRequest(`/${item.id}`, { method: 'DELETE', prefix: '/recipes' })
    } else {
      await adminRequest(`/comments/${item.id}`, { method: 'DELETE' })
    }
    await load(pagination.value.page)
  })
}
onMounted(() => run(() => load()))
</script>

<template>
  <main class="mx-auto w-full max-w-5xl space-y-6 p-6 text-gray-900">
    <h1 class="text-3xl font-bold">Modération</h1>
    <p v-if="error" role="alert" class="text-red-700">{{ error }}</p>
    <template v-if="auth.can('content.moderate')">
      <label for="moderation-kind">Contenus
        <select id="moderation-kind" name="kind" v-model="kind" :disabled="busy" class="ml-3 rounded border bg-white text-black p-2" @change="run(() => load())">
          <option value="recipes">Recettes</option><option value="comments">Commentaires</option>
        </select>
      </label>
      <p>{{ pagination.total }} contenu(s)</p>
      <ul :aria-busy="busy" class="space-y-3">
        <li v-for="item in items" :key="item.id" class="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-white p-5 shadow">
          <div class="min-w-0 flex-1">
            <RouterLink :to="{ name: 'recipe-details', params: { id: kind === 'recipes' ? item.id : item.recipe_id } }" class="font-semibold underline">
              {{ kind === 'recipes' ? item.title : `Recette #${item.recipe_id}` }}
            </RouterLink>
            <p>Par {{ item.author }}</p><p v-if="kind === 'comments'" class="whitespace-pre-wrap break-words">{{ item.content }}</p>
          </div>
          <button :disabled="busy" class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors text-red-700" @click="remove(item)">{{ kind === 'recipes' ? 'Supprimer' : 'Retirer' }}</button>
        </li>
      </ul>
      <p v-if="!items.length">Aucun contenu à afficher.</p>
      <nav aria-label="Pagination" class="flex gap-4">
        <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" :disabled="busy || pagination.page <= 1" @click="run(() => load(pagination.page - 1))">Précédent</button>
        <span>Page {{ pagination.page }}</span>
        <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" :disabled="busy || pagination.page * pagination.per_page >= pagination.total" @click="run(() => load(pagination.page + 1))">Suivant</button>
      </nav>

      <div v-if="itemToRemove" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4" role="dialog" aria-modal="true">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6 text-gray-900">
          <h3 class="text-xl font-bold text-red-600 mb-4">{{ kind === 'recipes' ? 'Supprimer la recette' : 'Retirer le commentaire' }}</h3>
          <p class="text-gray-700 mb-6 text-sm">
            {{ kind === 'recipes' ? 'Supprimer définitivement cette recette ?' : 'Retirer le contenu de ce commentaire ?' }}
          </p>
          <div class="flex justify-end space-x-3">
            <button type="button" class="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 font-medium transition-colors" @click="itemToRemove = null">Annuler</button>
            <button type="button" class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 font-medium transition-colors" @click="confirmRemove">Confirmer</button>
          </div>
        </div>
      </div>
    </template>
    <p v-else>L’accès à cette page nécessite des droits de modération.</p>
  </main>
</template>
