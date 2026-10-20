<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/authState'
import { adminRequest } from '@/services/adminService'

const auth = useAuthStore()
const users = ref([])
const roles = ref(['user', 'moderator', 'admin'])
const pagination = ref({ page: 1, per_page: 20, total: 0 })
const filters = reactive({ q: '', role: '', status: '' })
const busy = ref(false)
const error = ref('')
const message = ref('')
const editing = ref(null)
const creating = ref(false)
const form = reactive({ username: '', email: '', password: '', role: 'user' })

async function load(page = 1) {
  const params = new URLSearchParams({ ...filters, page: String(page) })
  const data = await adminRequest(`/users?${params}`)
  users.value = data.users
  roles.value = data.roles
  pagination.value = data.pagination
}

async function run(action) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  message.value = ''
  try { await action() } catch (err) { error.value = err.message }
  finally { busy.value = false }
}

function openForm(user = null) {
  editing.value = user
  creating.value = !user
  Object.assign(form, { username: user?.username || '', email: user?.email || '', password: '', role: 'user' })
}

function closeForm() {
  editing.value = null
  creating.value = false
  form.password = ''
}

async function save() {
  await run(async () => {
    if (creating.value) {
      await adminRequest('/users', { method: 'POST', body: { ...form } })
    } else {
      await adminRequest(`/users/${editing.value.id}`, {
        method: 'PATCH', body: { username: form.username, email: form.email },
      })
    }
    closeForm()
    message.value = 'Compte enregistré.'
    await load(pagination.value.page)
  })
}

async function changeRole(user, event) {
  const role = event.target.value
  event.target.value = user.role
  if (role === user.role || !window.confirm(`Attribuer le rôle « ${role} » à ${user.username} ?`)) return
  await run(async () => {
    await adminRequest(`/users/${user.id}/role`, { method: 'PATCH', body: { role } })
    if (user.id === auth.user?.id) await auth.fetchUser()
    if (auth.can('users.read')) await load(pagination.value.page)
    message.value = 'Rôle modifié.'
  })
}

async function changeStatus(user) {
  const isActive = user.status !== 'active'
  if (!window.confirm(`${isActive ? 'Réactiver' : 'Suspendre'} le compte de ${user.username} ?`)) return
  await run(async () => {
    await adminRequest(`/users/${user.id}`, { method: 'PATCH', body: { is_active: isActive } })
    if (user.id === auth.user?.id) auth.clearAuth()
    else await load(pagination.value.page)
  })
}

async function remove(user) {
  if (!window.confirm(`Supprimer et anonymiser définitivement le compte de ${user.username} ?`)) return
  await run(async () => {
    await adminRequest(`/users/${user.id}`, { method: 'DELETE' })
    if (user.id === auth.user?.id) auth.clearAuth()
    else await load(pagination.value.page)
  })
}

onMounted(() => run(() => load()))
</script>

<template>
  <main class="mx-auto w-full max-w-6xl flex-1 space-y-6 p-6 text-gray-900">
    <h1 class="text-3xl font-bold">Administration des utilisateurs</h1>
    <p v-if="error" role="alert" class="text-red-700">{{ error }}</p>
    <p v-if="message" role="status">{{ message }}</p>
    <p v-if="!auth.can('users.read')">L’accès à cette page nécessite des droits d’administration.</p>
    <template v-else>
      <form class="flex flex-wrap gap-3" @submit.prevent="run(() => load())">
        <input id="admin-filter-q" name="q" v-model="filters.q" aria-label="Rechercher un pseudo ou email" placeholder="Pseudo ou email" class="rounded border bg-white text-black p-2" />
        <select id="admin-filter-role" name="role" v-model="filters.role" aria-label="Filtrer par rôle" class="rounded border bg-white text-black p-2">
          <option value="">Tous les rôles</option>
          <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
        </select>
        <select id="admin-filter-status" name="status" v-model="filters.status" aria-label="Filtrer par statut" class="rounded border bg-white text-black p-2">
          <option value="">Tous les statuts</option>
          <option value="active">Actifs</option><option value="suspended">Suspendus</option><option value="deleted">Supprimés</option>
        </select>
        <button :disabled="busy" class="enabled:hover:bg-primary-dark transition-colors rounded bg-primary px-4 py-2 text-white">Rechercher</button>
        <button v-if="auth.can('users.create')" type="button" :disabled="busy" class="enabled:hover:bg-primary-dark transition-colors rounded bg-primary px-4 py-2 text-white" @click="openForm()">Créer un compte</button>
      </form>

      <form v-if="creating || editing" class="space-y-3 rounded-xl bg-white p-5 shadow" @submit.prevent="save">
        <h2 class="text-xl font-semibold">{{ creating ? 'Créer un compte' : 'Modifier le compte' }}</h2>
        <label for="admin-form-username" class="block">Pseudo <input id="admin-form-username" name="username" autocomplete="username" v-model.trim="form.username" required maxlength="254" class="rounded border bg-white text-black p-2" /></label>
        <label for="admin-form-email" class="block">Email <input id="admin-form-email" name="email" autocomplete="email" v-model.trim="form.email" type="email" required maxlength="254" class="rounded border bg-white text-black p-2" /></label>
        <template v-if="creating">
          <label for="admin-form-password" class="block">Mot de passe <input id="admin-form-password" name="password" v-model="form.password" type="password" autocomplete="new-password" required maxlength="72" class="rounded border bg-white text-black p-2" /></label>
          <label v-if="auth.can('roles.assign')" for="admin-form-role" class="block">Rôle <select id="admin-form-role" name="role" v-model="form.role" class="rounded border bg-white text-black p-2"><option v-for="role in roles" :key="role">{{ role }}</option></select></label>
        </template>
        <button :disabled="busy" class="enabled:hover:bg-gray-100 transition-colors mr-3 rounded bg-primary-light px-4 py-2">Enregistrer</button>
        <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" type="button" :disabled="busy" @click="closeForm">Annuler</button>
      </form>

      <div class="overflow-x-auto rounded-xl bg-white p-4 shadow" :aria-busy="busy">
        <table class="w-full text-left">
          <caption class="mb-3 text-left">{{ pagination.total }} compte(s)</caption>
          <thead><tr><th scope="col">Pseudo</th><th scope="col">Email</th><th scope="col">Rôle</th><th scope="col">Statut</th><th scope="col">Actions</th></tr></thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="border-t">
              <td class="p-2">{{ user.username }}</td><td class="p-2">{{ user.email }}</td>
              <td class="p-2">
                <select v-if="auth.can('roles.assign') && user.status !== 'deleted'" :id="`user-role-${user.id}`" :name="`user-role-${user.id}`" :value="user.role" :aria-label="`Rôle de ${user.username}`" :disabled="busy" class="rounded border bg-white text-black p-2" @change="changeRole(user, $event)">
                  <option v-for="role in roles" :key="role">{{ role }}</option>
                </select><span v-else>{{ user.role }}</span>
              </td>
              <td class="p-2">{{ { active: 'Actif', suspended: 'Suspendu', deleted: 'Supprimé' }[user.status] }}</td>
              <td class="space-x-3 p-2">
                <template v-if="user.status !== 'deleted'">
                  <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" v-if="auth.can('users.update')" :disabled="busy" @click="openForm(user)">Modifier</button>
                  <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" v-if="auth.can('users.update')" :disabled="busy" @click="changeStatus(user)">{{ user.status === 'active' ? 'Suspendre' : 'Réactiver' }}</button>
                  <button v-if="auth.can('users.delete')" :disabled="busy" class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors text-red-700" @click="remove(user)">Supprimer</button>
                </template>
              </td>
            </tr>
            <tr v-if="!users.length"><td colspan="5" class="p-4">Aucun compte trouvé.</td></tr>
          </tbody>
        </table>
      </div>
      <nav aria-label="Pagination" class="flex items-center gap-4">
        <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" :disabled="busy || pagination.page <= 1" @click="run(() => load(pagination.page - 1))">Précédent</button>
        <span>Page {{ pagination.page }}</span>
        <button class="rounded px-3 py-2 enabled:hover:bg-gray-100 transition-colors" :disabled="busy || pagination.page * pagination.per_page >= pagination.total" @click="run(() => load(pagination.page + 1))">Suivant</button>
      </nav>
    </template>
  </main>
</template>
