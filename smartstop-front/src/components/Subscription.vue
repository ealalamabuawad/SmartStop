<script setup>
import { ref, onMounted } from 'vue';
import { Check, Sparkles, AlertCircle } from 'lucide-vue-next';

const billingPeriod = ref('mensual');
const headerContent = ref({ title: '', subtitle: '', disclaimerTitle: '', disclaimerText: '' });
const subscriptionPlans = ref([]);

onMounted(() => {
  headerContent.value = {
    title: 'Planes de Suscripción',
    subtitle: 'Desbloquea el poder absoluto del Motor de Reglas IATA y descubre escalas extendidas sin costo adicional.',
    disclaimerTitle: 'Nota de Transparencia de SmartStop:',
    disclaimerText: ' Las membresías simuladas y los cálculos de reglas y restricciones de equipaje actúan conforme a los datos informativos de las aerolíneas reguladas por la IATA en Chile. No representamos legalmente a las aerolíneas oficiales mencionadas.'
  };

  subscriptionPlans.value = [
    {
      id: 'free',
      name: 'Gratuito',
      desc: 'Para viajeros ocasionales',
      price: { mensual: 0, anual: 0 },
      features: ['Buscador de vuelos estándar', 'Validación básica de 1 maleta de mano', 'Visualización de pasajes en CLP', 'Atención de soporte estándar por correo'],
      buttonText: 'Registrarse gratis',
      popular: false
    },
    {
      id: 'frequent',
      name: 'Viajero Frecuente',
      desc: 'Ideal para auditar y conectar stopovers',
      price: { mensual: 4990, anual: 3990 },
      features: ['Búsqueda avanzada de Stopovers (24h-72h)', 'Motor de Reglas IATA ilimitado (hasta 4 maletas)', 'Auditoría y soporte para vuelos de código compartido', 'Alertas Premium instantáneas de baja de precio', 'Soporte prioritario 24/7'],
      buttonText: 'Comenzar periodo de prueba',
      popular: true
    },
    {
      id: 'elite',
      name: 'SmartStop Elite',
      desc: 'Máxima protección para trotamundos',
      price: { mensual: 12990, anual: 9990 },
      features: ['Todo lo de Viajero Frecuente', 'Garantía IATA: Cobertura por multas de exceso de equipaje', 'Sugerencia inteligente de atracciones en escala con IA', 'Sincronización directa con Google Wallet', 'Acceso preferencial a salas Vip aliadas'],
      buttonText: 'Suscribirse a Elite',
      popular: false
    }
  ];
});

defineEmits(['subscribe']);
</script>

<template>
  <div class="max-w-6xl mx-auto px-4 py-12 text-[#03254c]">
    <div class="text-center max-w-2xl mx-auto mb-10">
      <h1 class="text-4xl font-extrabold tracking-tight mb-3">{{ headerContent.title }}</h1>
      <p class="text-slate-600">{{ headerContent.subtitle }}</p>

      <div class="inline-flex bg-slate-100 p-1 rounded-xl mt-8 border border-slate-200">
        <button @click="billingPeriod = 'mensual'" :class="['px-4 py-2 text-xs font-semibold rounded-lg transition-all', billingPeriod === 'mensual' ? 'bg-white shadow-xs text-[#03254c]' : 'text-slate-500 hover:text-slate-700']">
          Mensual
        </button>
        <button @click="billingPeriod = 'anual'" :class="['px-4 py-2 text-xs font-semibold rounded-lg transition-all relative flex items-center gap-1.5', billingPeriod === 'anual' ? 'bg-white shadow-xs text-[#03254c]' : 'text-slate-500 hover:text-slate-700']">
          <span>Anual</span>
          <span class="text-[10px] bg-emerald-100 text-emerald-800 font-extrabold px-1.5 py-0.5 rounded-full">-25%</span>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch mt-6">
      <div v-for="plan in subscriptionPlans" :key="plan.id" :class="['relative rounded-3xl p-8 flex flex-col justify-between transition-all duration-300 border', plan.popular ? 'bg-white border-[#03254c] shadow-md ring-2 ring-[#03254c]/10 scale-105 z-10' : 'bg-white/80 border-slate-200 shadow-xs']">
        <span v-if="plan.popular" class="absolute top-0 right-8 -translate-y-1/2 bg-[#03254c] text-white text-[10px] font-extrabold uppercase py-1 px-3.5 rounded-full tracking-widest flex items-center gap-1">
          <Sparkles class="w-3 h-3" /> Popular
        </span>

        <div>
          <h3 class="text-xl font-bold text-slate-800 mb-1">{{ plan.name }}</h3>
          <p class="text-xs text-slate-500 mb-6">{{ plan.desc }}</p>

          <div class="flex items-baseline gap-1 mb-6">
            <span class="text-4xl font-extrabold text-slate-900">${{ plan.price[billingPeriod].toLocaleString('es-CL') }}</span>
            <span class="text-xs text-slate-400 font-medium font-mono">CLP / mes</span>
          </div>

          <div class="font-medium text-xs text-slate-400 mb-4 uppercase tracking-wider">Características incluidas:</div>

          <ul class="space-y-3.5 mb-8">
            <li v-for="(feat, index) in plan.features" :key="index" class="flex items-start gap-2.5 text-xs text-slate-600 leading-tight">
              <Check class="w-4.5 h-4.5 text-[#03254c] shrink-0" />
              <span>{{ feat }}</span>
            </li>
          </ul>
        </div>

        <button @click="$emit('subscribe', plan.id)" :class="['w-full py-3.5 px-4 rounded-xl text-xs font-bold transition-all duration-200', plan.popular ? 'bg-[#03254c] text-white hover:bg-[#001f3f]' : 'bg-slate-100 hover:bg-slate-200 text-slate-800']">
          {{ plan.buttonText }}
        </button>
      </div>
    </div>

    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 mt-12 flex items-start gap-3 max-w-3xl mx-auto">
      <AlertCircle class="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
      <div class="text-xs text-slate-600">
        <span class="font-bold">{{ headerContent.disclaimerTitle }}</span>{{ headerContent.disclaimerText }}
      </div>
    </div>
  </div>
</template>