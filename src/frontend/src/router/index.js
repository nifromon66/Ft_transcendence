import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import OAuthSuccessView from '@/views/OAuthSuccessView.vue'
import { useAuthStore } from '@/stores/authState.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/admin/users", name: "admin-users", component: () => import("@/views/AdminUsersView.vue"), meta: { requiresAuth: true, permission: "users.read" } },
    { path: "/moderation", name: "moderation", component: () => import("@/views/ModerationView.vue"), meta: { requiresAuth: true, permission: "content.moderate" } },
    { path: "/forbidden", name: "forbidden", component: () => import("@/views/ForbiddenView.vue") },
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/UserProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },
    {
      path: '/friends',
      name: 'friends',
      component: () => import('@/views/FriendsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue'),
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: () => import('../views/PrivacyView.vue'),
    },
    {
      path: '/recipe/:id',
      name: 'recipe-details',
      component: () => import('../views/RecipeDetailsView.vue'),
      props: true,
    },
    {
      path: '/postRecipe',
      name: 'postRecipe',
      component: () => import('../views/PostRecipeView.vue'),
      props: true,
      meta: { requiresAuth: true, permission: 'recipes.create' },
    },
    {
      path: '/recipe/:id/edit',
      name: 'recipe-edit',
      component: () => import('../views/EditRecipeView.vue'),
      props: true,
      meta: { requiresAuth: true, refreshPermissions: true },
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchResultsView.vue'),
    },
    {
      path: '/user/:id',
      name: 'public-profile',
      component: () => import('@/views/PublicProfileView.vue'),
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/views/ChatView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/oauth-success',
      name: 'OAuthSuccess',
      component: OAuthSuccessView
    }
  ],
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' }
  }
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (!authStore.isInitialized) {
    if (!authStore.token) {
      try {
        await authStore.silentRefresh()
      } catch {
      }
    }
    authStore.isInitialized = true
  }

  const isAuthenticated = !!authStore.token

  if (to.meta.requiresAuth && !isAuthenticated) {
    return { name: 'login' }
  }

  if (to.meta.permission || to.meta.refreshPermissions) {
    try {
      await authStore.fetchUser()
    } catch {
      return { name: 'login' }
    }
    if (to.meta.permission && !authStore.can(to.meta.permission)) {
      return { name: 'forbidden' }
    }
  }

  const guestOnlyRoutes = ['login', 'register']
  if (guestOnlyRoutes.includes(to.name) && isAuthenticated) {
    return { name: 'welcome' }
  }
})

const isChunkLoadFailed = (error) => {
  return error.name === 'ChunkLoadError' || (error.name === 'TypeError' && error.message.includes('dynamically imported module'))
}


router.onError((error, to) => {
  if (!navigator.onLine) {
    return
  }

  if (isChunkLoadFailed(error)) {
    window.location.href = to.fullPath
    return
  }

  throw error
})

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    window.location.reload()
  })
}

export default router
