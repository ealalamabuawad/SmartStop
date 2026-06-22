import { createRouter, createWebHistory } from "vue-router";
import Busqueda from "../views/Busqueda.vue";
import Ingreso from "../views/Ingreso.vue";
import ValidadorMaleta from "../components/ValidadorMaleta.vue";

const routes = [
  {
    path: "/",
    name: "Busqueda",
    component: Busqueda,
  },
  {
    path: "/ingreso",
    name: "Ingreso",
    component: Ingreso,
  },
  {
    path: "/validador",
    name: "Validador",
    component: ValidadorMaleta,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
