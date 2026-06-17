import { createRouter, createWebHistory } from 'vue-router'
import Busqueda from '../views/Busqueda.vue'
import Ingreso from '../views/Ingreso.vue'

const routes = [
  {
    path: '/',
    name: 'Busqueda',
    component: Busqueda
  },
  {
    path: '/ingreso',
    name: 'Ingreso',
    component: Ingreso
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 