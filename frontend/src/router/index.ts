import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    // Placeholder routes for future implementation
    {
      path: '/collections',
      name: 'collections',
      component: () => import('../views/HomeView.vue'), // Temporary, will create proper component later
    },
    {
      path: '/items',
      name: 'items',
      component: () => import('../views/HomeView.vue'), // Temporary, will create proper component later
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/HomeView.vue'), // Temporary, will create proper component later
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/HomeView.vue'), // Temporary, will create proper component later
    },
  ],
})

export default router
