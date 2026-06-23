import { createRouter, createWebHistory } from 'vue-router'
import Busqueda from '../views/Busqueda.vue'
import Ingreso from '../views/Ingreso.vue'
import Registro from '../views/Registro.vue'
import Resultados from '../views/Resultados.vue'

const routes = [
  {
    path: "/",
    name: "Busqueda",
    component: Busqueda,
  },
  {
    path: '/ingreso',
    name: 'Ingreso',
    component: Ingreso
  },
  {
    path: '/registro',
    name: 'Registro',
    component: Registro
  },
  {
    path: '/resultados',
    name: 'Resultados',
    component: Resultados
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
      }
    }
    return { top: 0 }
  }
})

export default router
