import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/interrupcoes',
      name: 'interrupcoes',
      component: () => import('../views/InterrupcoesView.vue')
    },
    {
      path: '/demandas',
      name: 'demandas',
      component: () => import('../views/DemandasView.vue')
    }
  ]
})

export default router
