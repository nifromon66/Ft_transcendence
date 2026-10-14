import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import OAuthSuccessView from '@/views/OAuthSuccessView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/UserProfileView.vue')
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
      path: '/badges',
      name: 'badges',
      component: () => import('@/views/BadgeView.vue'),
      meta: { requiresAuth: true },
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
    },
    {
      path: '/test-upload',
      name: 'test-upload',
      component: () => import('@/views/TestUploadView.vue'),
    },
    {
      path: '/recipe/:id/edit',
      name: 'recipe-edit',
      component: () => import('../views/EditRecipeView.vue'),
      props: true,
      meta: { requiresAuth: true },
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

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return { name: 'login' }
  }
})

router.onError((error) => {
  if (!navigator.onLine) {
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
