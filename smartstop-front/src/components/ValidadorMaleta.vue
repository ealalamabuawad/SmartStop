<template>
  <div
    class="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 max-w-xl mx-auto"
  >
    <!-- Encabezado -->
    <div class="mb-6">
      <span
        class="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider"
      >
        Motor de Reglas
      </span>
      <h2 class="text-2xl font-extrabold text-[#081c3a] mt-3">
        Validador Preventivo de Equipaje
      </h2>
      <p class="text-gray-500 text-sm mt-1">
        Ingresa las dimensiones reales de tu maleta para evitar cobros
        imprevistos (Ancillary Revenues).
      </p>
    </div>

    <!-- Formulario -->
    <div class="space-y-5">
      <!-- Fila 1: Aerolínea -->
      <div class="flex flex-col">
        <label
          class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 pl-1"
        >
          Aerolínea (Código IATA)
        </label>
        <input
          v-model="aerolinea"
          type="text"
          placeholder="Ej. LA (LATAM), JA (Jetsmart)"
          class="bg-gray-100 text-gray-800 rounded-xl p-3 outline-none focus:ring-2 focus:ring-[#081c3a] transition-all w-full"
        />
      </div>

      <!-- Fila 2: Dimensiones -->
      <div class="grid grid-cols-3 gap-4">
        <div class="flex flex-col">
          <label
            class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 pl-1"
            >Alto (CM)</label
          >
          <input
            v-model.number="alto"
            type="number"
            class="bg-gray-100 text-gray-800 rounded-xl p-3 outline-none focus:ring-2 focus:ring-[#081c3a] transition-all"
          />
        </div>
        <div class="flex flex-col">
          <label
            class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 pl-1"
            >Ancho (CM)</label
          >
          <input
            v-model.number="ancho"
            type="number"
            class="bg-gray-100 text-gray-800 rounded-xl p-3 outline-none focus:ring-2 focus:ring-[#081c3a] transition-all"
          />
        </div>
        <div class="flex flex-col">
          <label
            class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 pl-1"
            >Largo (CM)</label
          >
          <input
            v-model.number="largo"
            type="number"
            class="bg-gray-100 text-gray-800 rounded-xl p-3 outline-none focus:ring-2 focus:ring-[#081c3a] transition-all"
          />
        </div>
      </div>

      <!-- Fila 3: Peso y Botón -->
      <div class="grid grid-cols-2 gap-4 items-end">
        <div class="flex flex-col">
          <label
            class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1 pl-1"
            >Peso (KG)</label
          >
          <input
            v-model.number="peso"
            type="number"
            class="bg-gray-100 text-gray-800 rounded-xl p-3 outline-none focus:ring-2 focus:ring-[#081c3a] transition-all"
          />
        </div>
        <button
          @click="validarEquipaje"
          class="bg-[#081c3a] hover:bg-[#122b54] text-white font-semibold rounded-xl p-3 transition-colors flex items-center justify-center gap-2"
        >
          <span>Validar Equipaje</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M14 5l7 7m0 0l-7 7m7-7H3"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Alertas de Resultados (Renderizado Condicional) -->
    <transition name="fade">
      <div v-if="resultado" class="mt-6">
        <!-- Alerta de Éxito -->
        <div
          v-if="resultado.estado === 'exito'"
          class="bg-green-50 border border-green-200 p-4 rounded-xl flex gap-3 items-start"
        >
          <svg
            class="h-6 w-6 text-green-500 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div>
            <h4 class="text-green-800 font-bold">Equipaje Aprobado</h4>
            <p class="text-green-600 text-sm mt-1">{{ resultado.mensaje }}</p>
          </div>
        </div>

        <!-- Alerta de Multa (Error) -->
        <div
          v-if="resultado.estado === 'error'"
          class="bg-red-50 border border-red-200 p-4 rounded-xl flex gap-3 items-start"
        >
          <svg
            class="h-6 w-6 text-red-500 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div>
            <h4 class="text-red-800 font-bold">Alerta de Sobrecosto</h4>
            <p class="text-red-600 text-sm mt-1">{{ resultado.mensaje }}</p>
            <div
              class="mt-2 bg-red-100 text-red-800 px-3 py-2 rounded-lg font-bold text-sm inline-block"
            >
              Multa Estimada: ${{
                resultado.multaEstimada.toLocaleString("es-CL")
              }}
              CLP
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from "vue";

const aerolinea = ref("");
const alto = ref("");
const ancho = ref("");
const largo = ref("");
const peso = ref("");
const resultado = ref(null);

const validarEquipaje = async () => {
  // Aquí es donde simulamos la petición para que puedas ver cómo reacciona el diseño
  // Dependiendo de lo que escribas, forzaremos un error o un éxito visual.

  if (
    !aerolinea.value ||
    !alto.value ||
    !ancho.value ||
    !largo.value ||
    !peso.value
  ) {
    return; // No hacer nada si faltan datos
  }

  // Simulador temporal para diseño: Si el peso es mayor a 10, tira multa.
  if (peso.value > 10) {
    resultado.value = {
      estado: "error",
      mensaje:
        "Las dimensiones o el peso superan el contrato de transporte de la aerolínea seleccionada.",
      multaEstimada: 45000,
    };
  } else {
    resultado.value = {
      estado: "exito",
      mensaje:
        "Tu maleta cumple con las resoluciones de la IATA. Viajas sin sorpresas.",
    };
  }
};
</script>

<style scoped>
/* Animación suave para la aparición de las alertas */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
