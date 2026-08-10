<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const avatarFile = ref(null)

const MAX_UPLOAD_SIZE = 10 * 1024 * 1024
const ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp']
const ALLOWED_MIMETYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

const onFileSelected = (event) => {
  errorMessage.value = ''
  const file = event.target.files[0]

  if (!file) {
    avatarFile.value = null
    return
  }

  const fileName = file.name
  const hasExtension = fileName.includes('.')
  const fileExtension = hasExtension ? fileName.split('.').pop().toLowerCase() : ''

  if (!hasExtension || !ALLOWED_EXTENSIONS.includes(fileExtension)) {
    errorMessage.value = "L'extension du fichier n'est pas autorisée (.png, .jpg, .jpeg, .gif, ou .webp uniquement)."
    event.target.value = ''
    avatarFile.value = null
    return
  }

  if (!ALLOWED_MIMETYPES.includes(file.type)) {
    errorMessage.value = "Le format du fichier n'est pas reconnu comme une image valide."
    event.target.value = ''
    avatarFile.value = null
    return
  }

  if (file.size > MAX_UPLOAD_SIZE) {
    errorMessage.value = "Le fichier dépasse la taille autorisée (10 Mo max)."
    event.target.value = ''
    avatarFile.value = null
    return
  }

  avatarFile.value = file
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

      const uploadRes = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (uploadRes.status >= 500) {
        errorMessage.value = "Erreur interne du serveur. Veuillez réessayer."
        return
      }

      if (!uploadRes.ok ) {
        const uploadError = await uploadRes.json()
        errorMessage.value = uploadError.error || "Une erreur est survenue lors du transfert de l'image."
        return
      }
    }

    router.push('/login')
  } catch (error) {
    errorMessage.value = "Une erreur réseau est survenue. Veuillez vérifier votre connexion."
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
        <br>
        <input
          id="avatar"
          type="file"
          accept=".png, .jpg, .jpeg, .gif, .webp"
          @change="onFileSelected"
        />
      </div>
      <button type="submit">S'inscrire</button>
    </form>
    <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
  </div>
</template>
