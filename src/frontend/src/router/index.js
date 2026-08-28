import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import HomeView from '../views/HomeView.vue'
import FollowView from '../views/FollowView.vue'
import BadgeView from '../views/BadgeView.vue'

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
      component: () => import('@/views/UserProfile.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },
    {
      path: '/follow',
      name: 'follow',
      component: FollowView,
    },
    {
      path: '/terms',
      name: 'terms',
      component: () => import('../views/TermsView.vue'),
    },
    {
      path: '/privacy',
      name : 'privacy',
      component: () => import('../views/PrivacyView.vue'),
    },
    {
      path: '/badges',
      name: 'badges',
      component: BadgeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/recipe/:id',
      name : 'recipe-details',
      component: () => import('../views/RecipeDetailsView.vue'),
      props: true,
    },
    {
      path: '/postRecipe',
      name : 'postRecipe',
      component: () => import('../views/PostRecipeView.vue'),
      props: true,
    },
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

export default router
