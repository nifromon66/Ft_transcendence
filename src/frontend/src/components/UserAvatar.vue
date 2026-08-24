<script setup>
import { ref, watch, onMounted } from 'vue'
import { useAuthStore } from '@/authState'

const errorMessage = ref('')

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
  expanded: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['activate'])

const authStore = useAuthStore()

const avatarImageSrc = ref(null)

const loadAvatar = async () => {
  if (!props.user || !props.user.avatar_url) {
    avatarImageSrc.value = null
    return
  }

  try {
    const token = authStore.token

    if (!token) {
      errorMessage.value = "Utilisateur non authentifié"
      avatarImageSrc.value = null
      return
    }

    const baseUrl = import.meta.env.VITE_API_URL

    const response = await fetch(`${baseUrl}${props.user.avatar_url}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) {
      errorMessage.value = "Accès refusé ou fichier introuvable"
      avatarImageSrc.value = null
      return
    }

    const contentType = response.headers.get("content-type")

    if (contentType && contentType.includes("application/json")) {
      const data = await response.json()
      if (data.success === false) {
        errorMessage.value = data.error
        avatarImageSrc.value = null
        return
      }
    }

    if (!contentType || !contentType.includes("image")) {
      avatarImageSrc.value = null
      return
    }

    const blob = await response.blob()
    avatarImageSrc.value = URL.createObjectURL(blob)
  
  } catch (error) {
    avatarImageSrc.value = null
  }
}

onMounted(loadAvatar)
watch(() => props.user, loadAvatar, { deep: true })

</script>

<template>
  <button
    type="button"
    class="flex h-10 w-10 scale-125 cursor-pointer items-center justify-center rounded-full border 
        border-black text-lg font-bold text-white overflow-hidden"
    :class="user ? 'bg-primary-light' : 'bg-gray-500'"
    :title="user ? `Connecté en tant que ${user.username}` : 'Non connecté'"
    :aria-label="user ? `Menu de ${user.username}` : 'Menu du compte'"
    aria-haspopup="menu"
    :aria-expanded="expanded"
    @click="emit('activate')"
  >
    <img
      v-if="avatarImageSrc"
      :src="avatarImageSrc"
      :alt="`Avatar de ${user.username}`"
      class="h-full w-full object-cover"
    />

    <span v-else-if="user">
      {{ user.username.charAt(0).toUpperCase() }}
    </span>

    <span v-else>?</span>
  </button>
</template>