<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="mx-auto w-full max-w-5xl flex-1 px-6 py-10 text-gray-800 sm:py-16">
    <header class="mb-10 max-w-3xl">
      <p class="mb-3 text-sm font-semibold uppercase tracking-widest text-primary-dark">
        À propos
      </p>
      <h1 class="mb-5 text-3xl font-bold text-gray-900 sm:text-5xl">
        La cuisine se partage.
      </h1>
      <p class="text-lg leading-relaxed">
        Une recette, c'est une idée à essayer, un souvenir à transmettre ou une nouvelle
        découverte. Notre site rassemble les passionnés de cuisine autour du plaisir
        de préparer et de partager de bons plats.
      </p>
      <RouterLink
        :to="{ name: 'welcome' }"
        class="mt-6 inline-flex rounded-lg bg-primary px-5 py-3 font-semibold text-white transition-colors hover:bg-primary-dark focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary-dark"
      >
        Découvrir les recettes
      </RouterLink>
    </header>

    <section aria-labelledby="project-title" class="mb-8 rounded-2xl bg-white p-6 shadow-sm sm:p-8">
      <h2 id="project-title" class="mb-4 text-2xl font-bold text-gray-900">
        Notre projet
      </h2>
      <p class="leading-relaxed">
        Nous souhaitons créer un espace convivial pour trouver l'inspiration en cuisine,
        publier ses recettes et échanger avec d'autres cuisiniers. Que vous prépariez
        votre premier plat ou que vous aimiez déjà expérimenter, chacun peut apporter
        sa touche à la communauté.
      </p>
    </section>

    <section aria-labelledby="features-title" class="mb-10">
      <h2 id="features-title" class="mb-5 text-2xl font-bold text-gray-900">
        À vous de cuisiner
      </h2>
      <div class="grid gap-5 sm:grid-cols-3">
        <article class="rounded-2xl bg-white p-6 shadow-sm">
          <h3 class="mb-3 text-lg font-semibold text-primary-dark">Trouvez l'inspiration</h3>
          <p class="leading-relaxed">
            Explorez les recettes de la communauté et découvrez les dernières publications
            ainsi que les plats les plus appréciés.
          </p>
        </article>
        <article class="rounded-2xl bg-white p-6 shadow-sm">
          <h3 class="mb-3 text-lg font-semibold text-primary-dark">Partagez vos recettes</h3>
          <p class="leading-relaxed">
            Publiez vos idées avec leurs ingrédients, leurs étapes de préparation et
            une photo pour donner envie de passer aux fourneaux.
          </p>
        </article>
        <article class="rounded-2xl bg-white p-6 shadow-sm">
          <h3 class="mb-3 text-lg font-semibold text-primary-dark">Échangez ensemble</h3>
          <p class="leading-relaxed">
            Retrouvez d'autres membres, ajoutez des amis et poursuivez la conversation
            grâce à la messagerie.
          </p>
        </article>
      </div>
    </section>

    <section aria-labelledby="team-title" class="rounded-2xl bg-white p-6 shadow-sm sm:p-8">
      <h2 id="team-title" class="mb-4 text-2xl font-bold text-gray-900">
        L'équipe derrière le projet
      </h2>
      <p class="mb-4 leading-relaxed">
        Nous sommes des étudiants de l'école 42. Ce site est réalisé dans le cadre
        du projet ft_transcendence, qui nous permet de construire une application web
        en équipe et de mettre en pratique nos compétences en développement.
      </p>
      <p class="leading-relaxed">
        De l'interface à la gestion des données, nous apprenons à concevoir un service
        complet avec Vue, Tailwind CSS et Flask, déployé à l'aide de Docker et Nginx.
      </p>
    </section>
  </main>
</template>
