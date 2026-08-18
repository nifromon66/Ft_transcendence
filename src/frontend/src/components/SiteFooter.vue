<script>
import { RouterLink } from 'vue-router'
</script>

<template>
  <footer class="bg-primary px-6 py-4 text-center text-sm text-white">
    <div class="flex flex-col items-center justify-between gap-3 sm:flex-row">
      <p>© 2026 ft_transcendence</p>

      <nav aria-label="Liens légaux" class="flex flex-col gap-2">
        <RouterLink
          :to="{ name: 'terms' }"
          class="hover:underline"
        >
          Conditions Générales d'Utilisation
        </RouterLink>

        <RouterLink
          :to="{ name: 'privacy' }"
          class="hover:underline"
        >
          Politique de confidentialité
        </RouterLink>
      </nav>
    </div>
  </footer>
</template>