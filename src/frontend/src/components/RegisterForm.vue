<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import  ImageDropZone from './ImageDropZone.vue'
import ProgressBar from './ProgressBar.vue'
import { validateAvatar } from '@/utils/fileValidators'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const avatarFile = ref(null)

const uploadProgress = ref(0)
const isUploading = ref(false)

const formatFileSize = (bytes) => {
  if (bytes === 0) {
    return '0 Octets'
  }
  
  const k = 1024
  const sizes = ['Octets', 'Ko', 'Mo']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

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
    const registerRes = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        email: email.value,
        password: password.value
      })
    })

    if (registerRes.status >= 500) {
      errorMessage.value = "Erreur interne du serveur. Veuillez réessayer."
      return
    }

    const data = await registerRes.json()

    if (!registerRes.ok) {
      errorMessage.value = data.error || 'Erreur lors de l\'inscription'
      return
    }

    if (avatarFile.value)
    {
      const loginRes = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email.value,
          password: password.value
        })
      })

      if (loginRes.status >= 500) {
        errorMessage.value = "Erreur interne du serveur. Veuillez réessayer."
        return
      }

      if (!loginRes.ok) {
        errorMessage.value = "Votre compte a été créé avec succès. Cependant, une erreur réseau a empêché l'ajout de la photo de profil."
          return
      }

      const loginData = await loginRes.json()
      const token = loginData.access_token

      const formData = new FormData()
      formData.append('file', avatarFile.value)

      isUploading.value = true
      uploadProgress.value = 0

      await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.open('POST', '/api/upload')
        xhr.setRequestHeader('Authorization', `Bearer ${token}`)

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            uploadProgress.value = Math.round((event.loaded / event.total) * 100)
          }
        }

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve()
          } else {
            let errorMsg = "Une erreur est survenue lors du transfert de l'image."
            try {
              const uploadError = JSON.parse(xhr.responseText)
              errorMsg = uploadError.error || errorMsg
            } catch (e) {}
            reject(new Error(errorMsg))
          }
        }

        xhr.onerror = () => reject(new Error("Erreur réseau lors du transfert de l'image."))

        xhr.send(formData)
      })
    }

    router.push('/login')
  } catch (error) {
    errorMessage.value = "Une erreur réseau est survenue. Veuillez vérifier votre connexion."
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

        <p v-if="avatarFile" class="text-sm text-green-600 mt-2 font-medium">
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
