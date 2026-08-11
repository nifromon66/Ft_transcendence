<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import  ImageDropZone from './ImageDropZone.vue'
import ProgressBar from './ProgressBar.vue'
import { validateAvatar } from '@/utils/fileValidators'
import { formatFileSize } from '@/utils/formatters'
import { registerUser } from '@/services/userService'
import { loginUser } from '@/services/authService'
import { uploadAvatar } from '@/services/uploadService'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const avatarFile = ref(null)

const uploadProgress = ref(0)
const isUploading = ref(false)

const processFile = (rawFile) => {
  const {isValid, error } = validateAvatar(rawFile)

  if (!isValid) {
    errorMessage.value = error
    avatarFile.value = null
    return
  }

  errorMessage.value = ''
  avatarFile.value = rawFile
}

async function register() {
  if (errorMessage.value) {
    return
  }

  errorMessage.value = ''

  try {
    await registerUser({
      username: username.value,
      email: email.value,
      password: password.value
    })

    if (avatarFile.value) {
      const token = await loginUser({
        email: email.value,
        password: password.value
      })

      isUploading.value = true
      uploadProgress.value = 0

      await uploadAvatar(token, avatarFile.value, (progress) => {
        uploadProgress.value = progress
      })
    }

    router.push('/login')
  } catch (error) {
    errorMessage.value = error.message || "Une erreur inattendue est survenue."
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div>
    <h2>Inscription</h2>
    <form @submit.prevent="register">
      <input v-model="username" placeholder="Nom d'utilisateur" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Mot de passe" required />
      
      <div style="margin: 15px 0;">
        <label for="avatar">Photo de profil (optionnel)</label>
        
        <ImageDropZone 
          @file-dropped="processFile"
          :disabled="isUploading"
        />

        <p v-if="avatarFile && !isUploading" class="text-sm text-green-600 mt-2 font-medium">
          <span>{{ avatarFile.name }}</span>
          <span class="text-xs text-gray-400">({{ formatFileSize(avatarFile.size) }})</span>
        </p>

        <ProgressBar
          v-if="isUploading"
          :progress="uploadProgress"
        />
      </div>
      <button type="submit" :disabled="isUploading">S'inscrire</button>
    </form>
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>
