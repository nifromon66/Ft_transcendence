<script setup>
import { ref, onMounted } from 'vue'

const users = ref([])

async function fetchUsers() {
  const response = await fetch('/api/users')
  users.value = await response.json()
}

async function deleteUser(userId) {
  await fetch(`/api/users/${userId}`, {
    method: 'DELETE'
  })
  await fetchUsers()
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div>
    <h2>Liste des utilisateurs</h2>
    <ul>
      <li v-for="user in users" :key="user.id">
        {{ user.username }} (id: {{ user.id }})
        <button @click="deleteUser(user.id)">Supprimer</button>
      </li>
    </ul>
  </div>
</template>
