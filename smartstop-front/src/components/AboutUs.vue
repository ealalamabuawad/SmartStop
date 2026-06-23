<script setup>
import { Award, ShieldCheck, HeartHandshake, Eye } from 'lucide-vue-next';
import { ref, onMounted } from 'vue';

const missionData = ref({ title: '', description: '' });
const coreValues = ref([]);
const storyData = ref({ subtitle: '', title: '', paragraphs: [], image: '' });

onMounted(() => {
  missionData.value = {
    title: 'Nuestra Misión',
    description: 'SmartStop nace con el objetivo de democratizar la planificación de viajes inteligentes. Unimos algoritmos avanzados de escalas de larga duración (Stopovers) con la validación rigurosa de reglas IATA.'
  };

  coreValues.value = [
    { id: 1, icon: Award, color: 'blue', title: 'Excelencia Tecnológica', desc: 'Nuestro motor analiza miles de combinaciones de vuelos en tiempo real para encontrar escalas de 24 a 72 horas que no incrementan el costo del pasaje.' },
    { id: 2, icon: ShieldCheck, color: 'indigo', title: 'Motor de Reglas IATA', desc: 'Evitamos sorpresas de equipaje en el mostrador. Calculamos exactamente el volumen y peso de tu equipaje comparándola con las reglas específicas de todas las aerolineas del trayecto.' },
    { id: 3, icon: HeartHandshake, color: 'teal', title: 'Tranquilidad del Viajero', desc: 'Te acompañamos en cada paso con un resumen claro del itinerario, asistencia en línea y alertas de variaciones en la política de tarifas para una experiencia vacacional inigualable.' },
    { id: 4, icon: Eye, color: 'sky', title: 'Transparencia Total', desc: 'Sin tarifas ocultas ni comisiones injustas. Lo que ves en el buscador de SmartStop es exactamente lo que pagas, sin sorpresas finales en CLP.' }
  ];

  storyData.value = {
    subtitle: 'Nuestra Historia',
    title: 'Fundado por Viajeros para Viajeros',
    paragraphs: [
      'Tras pagar cuantiosas multas de exceso de equipaje debido a cambios imprevistos de maletas entre aerolineas asociadas durante una escala en Bogotá, decidimos crear un sistema que automatizara la validación regulatoria y de equipajes.',
      'Hoy, SmartStop asiste a miles de chilenos e hispanohablantes a explorar dos destinos por el precio de uno, garantizando que su maleta siempre cumplirá con las normativas locales de cada operador.'
    ],
    image: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&q=80&w=600'
  };
});
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-12 text-[#03254c]">
    <div class="text-center max-w-2xl mx-auto mb-16">
      <h1 class="text-4xl font-extrabold tracking-tight mb-4 font-sans">{{ missionData.title }}</h1>
      <p class="text-slate-600 leading-relaxed">{{ missionData.description }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
      <div v-for="val in coreValues" :key="val.id" class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex gap-4">
        <div :class="`p-3 bg-${val.color}-50 text-${val.color}-600 rounded-xl h-fit`">
          <component :is="val.icon" class="w-6 h-6" />
        </div>
        <div>
          <h3 class="text-lg font-bold mb-2">{{ val.title }}</h3>
          <p class="text-slate-500 text-sm leading-relaxed">{{ val.desc }}</p>
        </div>
      </div>
    </div>

    <div class="bg-slate-50 rounded-3xl p-8 md:p-12 border border-slate-100 flex flex-col md:flex-row items-center gap-10">
      <div class="flex-1 space-y-4">
        <span class="text-xs font-bold text-blue-600 uppercase tracking-widest">{{ storyData.subtitle }}</span>
        <h2 class="text-2xl font-extrabold tracking-tight">{{ storyData.title }}</h2>
        <p v-for="(paragraph, idx) in storyData.paragraphs" :key="idx" class="text-slate-600 text-sm leading-relaxed">
          {{ paragraph }}
        </p>
      </div>
      <div class="w-full md:w-80 h-64 bg-slate-200 rounded-2xl overflow-hidden relative shadow-sm">
        <img :src="storyData.image" :alt="storyData.title" class="w-full h-full object-cover grayscale opacity-80" referrerpolicy="no-referrer" />
        <div class="absolute inset-0 bg-[#03254c]/20" />
      </div>
    </div>
  </div>
</template>