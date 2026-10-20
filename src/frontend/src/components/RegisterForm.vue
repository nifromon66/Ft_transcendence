<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/authState'
import ImageDropZone from './ImageDropZone.vue'
import ImagePreview from './ImagePreview.vue'
import ProgressBar from './ProgressBar.vue'
import { validateAvatar } from '@/utils/fileValidators'
import { optimizeImage } from '@/utils/imageProcessor'
import { registerUser } from '@/services/authService'
import { uploadAvatar } from '@/services/userService'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const acceptTerms = ref(false)
const acceptPrivacy = ref(false)
const errorMessage = ref('')
const avatarFile = ref(null)

const uploadProgress = ref(0)
const isUploading = ref(false)

const processFile = async (rawFile) => {
  const { isValid, error } = validateAvatar(rawFile)

  if (!isValid) {
    errorMessage.value = error
    avatarFile.value = null
    return
  }

  try {
    const optimizedFile = await optimizeImage(rawFile)

    errorMessage.value = ''
    avatarFile.value = optimizedFile
  } catch {
    errorMessage.value = "Erreur lors du redimensionnement automatique de cette image."
    avatarFile.value = null
  }
}

const clearFile = () => {
  avatarFile.value = null
  errorMessage.value = ''
}

async function register() {
  errorMessage.value = ''

  if (!acceptTerms.value || !acceptPrivacy.value) {
    errorMessage.value = "Veuillez accepter les CGU et la politique de confidentialité."
    return
  }

  try {
    const registerToken = await registerUser({
      username: username.value,
      email: email.value,
      password: password.value,
      accept_terms: acceptTerms.value,
      accept_privacy: acceptPrivacy.value
    })

    if (avatarFile.value) {
      isUploading.value = true
      uploadProgress.value = 0

      await uploadAvatar(registerToken, avatarFile.value, (progress) => {
        uploadProgress.value = progress
      })
    }

    authStore.setAuth(registerToken, null)
    await authStore.fetchUser()
    router.push({ name: 'welcome' })
  } catch (error) {
    errorMessage.value = error.message || "Une erreur inattendue est survenue."
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div class="flex flex-1 items-center justify-center bg-primary-dark">
    <div class="w-full max-w-sm rounded-lg bg-menu-background p-8 shadow-lg">
      <h2 class="mb-6 text-center text-2xl font-bold text-black">Inscription</h2>
      <form @submit.prevent="register" class="flex flex-col gap-0.5">
        <div>
          <input v-model="username" id="username" name="username" placeholder="Nom d'utilisateur" autocomplete="username"
            class="w-full rounded border p-2 bg-white font-semibold text-black" required />
        </div>
        <div>
          <input v-model="email" id="email" name="email" type="email" placeholder="Email" autocomplete="email"
            class="w-full rounded border p-2 bg-white font-semibold text-black" required />
        </div>
        <div>
          <input v-model="password" id="password" name="password" type="password" placeholder="Mot de passe" autocomplete="new-password"
            class="w-full rounded border p-2 bg-white font-semibold text-black" required />
        </div>
        <div style="margin: 15px 0;">
          <label for="avatar">Photo de profil (optionnel)</label>

          <ImageDropZone v-if="!avatarFile" @file-selected="processFile" :disabled="isUploading" />

          <ImagePreview v-if="avatarFile && !isUploading" :file="avatarFile" :disabled="isUploading"
            @clear="clearFile" />

          <ProgressBar v-if="isUploading" :progress="uploadProgress" />
        </div>

        <div class="mb-4 flex flex-col gap-2 text-sm text-gray-800">
          <label for="accept-terms" class="flex items-start gap-2 cursor-pointer">
            <input
              id="accept-terms"
              v-model="acceptTerms"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 shrink-0 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>
              J'ai lu et j'accepte les
              <RouterLink :to="{ name: 'terms' }" class="text-blue-600 underline hover:text-blue-800">
                Conditions générales d'utilisation
              </RouterLink>
            </span>
          </label>

          <label for="accept-privacy" class="flex items-start gap-2 cursor-pointer">
            <input
              id="accept-privacy"
              v-model="acceptPrivacy"
              type="checkbox"
              required
              class="mt-1 h-4 w-4 shrink-0 cursor-pointer rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>
              J'ai pris connaissance de la
              <RouterLink :to="{ name: 'privacy' }" class="text-blue-600 underline hover:text-blue-800">
                Politique de confidentialité
              </RouterLink>
            </span>
          </label>
        </div>

        <button
          type="submit"
          :disabled="isUploading || !acceptTerms || !acceptPrivacy"
          class="w-full rounded bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isUploading ? 'Inscription en cours...' : "S'inscrire" }}
        </button>
      </form>
      <p v-if="errorMessage" class="mt-4 text-center text-sm text-red-600">{{ errorMessage }}</p>
    </div>
  </div>
</template>
