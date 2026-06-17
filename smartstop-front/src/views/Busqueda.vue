<template>
  <div class="w-full">
    <section class="hero-gradient relative overflow-hidden py-20 md:py-28 px-4">
      <div class="absolute inset-0 opacity-10 pointer-events-none" style="background-image: radial-gradient(#006c49 0.5px, transparent 0.5px); background-size: 24px 24px;"></div>
      <div class="relative max-w-[1280px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        <div class="space-y-6 text-left">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#6cf8bb]/20 border border-[#006c49]/20">
            <span class="w-2 h-2 rounded-full bg-[#006c49] animate-pulse"></span>
            <span class="text-[#00714d] text-xs font-bold uppercase tracking-wider">Nueva Tecnología IATA v2.4</span>
          </div>
          <h1 class="text-4xl md:text-5xl lg:text-6xl text-[#00236f] font-extrabold leading-[1.1] tracking-tight">
            Optimiza tus escalas y viaja sin <span class="text-[#006c49]">multas imprevistas</span>
          </h1>
          <p class="text-base md:text-lg text-[#444651] max-w-xl leading-relaxed">
            Encuentra stopovers inteligentes de 24 a 72 horas y valida tu equipaje en tiempo real con nuestro motor de reglas global.
          </p>
          <div class="flex flex-wrap gap-6 pt-2">
            <div class="flex items-center gap-2 text-[#444651]">
              <span class="material-symbols-outlined text-[#006c49] fill-1">check_circle</span>
              <span class="text-sm font-semibold">Datos IATA oficiales</span>
            </div>
            <div class="flex items-center gap-2 text-[#444651]">
              <span class="material-symbols-outlined text-[#006c49] fill-1">check_circle</span>
              <span class="text-sm font-semibold">Alertas en tiempo real</span>
            </div>
          </div>
        </div>

        <div class="relative hidden lg:block">
          <div class="glass-card rounded-2xl p-4 shadow-2xl bg-white/40">
            <div class="w-full h-[320px] bg-gradient-to-tr from-[#00236f] to-[#006c49] rounded-xl flex items-center justify-center text-white opacity-90">
              <span class="material-symbols-outlined text-6xl animate-pulse">flight_takeoff</span>
            </div>
          </div>
        </div>

      </div>
    </section>

    <section class="-mt-12 relative z-20 px-4 max-w-[1280px] mx-auto">
      <form @submit.prevent="ejecutarBusqueda" class="glass-card p-6 md:p-8 rounded-2xl shadow-xl bg-white border border-gray-100">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          
          <div class="space-y-2 text-left">
            <label class="text-xs font-bold text-[#444651] uppercase tracking-wider block ml-1">Origen (IATA)</label>
            <div class="relative flex items-center border border-gray-200 rounded-xl bg-[#f3f4f6] focus-within:ring-2 focus-within:ring-[#006c49] focus-within:bg-white transition-all">
              <span class="material-symbols-outlined absolute left-4 text-gray-400">flight_takeoff</span>
              <input v-model="formulario.origen" required maxlength="3" class="w-full pl-12 pr-4 py-3 bg-transparent border-none rounded-xl text-[#00236f] font-bold uppercase placeholder:text-gray-400 focus:outline-none" placeholder="SCL" type="text"/>
            </div>
          </div>
          
          <div class="space-y-2 text-left">
            <label class="text-xs font-bold text-[#444651] uppercase tracking-wider block ml-1">Destino (IATA)</label>
            <div class="relative flex items-center border border-gray-200 rounded-xl bg-[#f3f4f6] focus-within:ring-2 focus-within:ring-[#006c49] focus-within:bg-white transition-all">
              <span class="material-symbols-outlined absolute left-4 text-gray-400">flight_land</span>
              <input v-model="formulario.destino" required maxlength="3" class="w-full pl-12 pr-4 py-3 bg-transparent border-none rounded-xl text-[#00236f] font-bold uppercase placeholder:text-gray-400 focus:outline-none" placeholder="MAD" type="text"/>
            </div>
          </div>
          
          <div class="space-y-2 text-left">
            <label class="text-xs font-bold text-[#444651] uppercase tracking-wider block ml-1">Salida</label>
            <div class="relative flex items-center border border-gray-200 rounded-xl bg-[#f3f4f6] focus-within:ring-2 focus-within:ring-[#006c49] focus-within:bg-white transition-all">
              <span class="material-symbols-outlined absolute left-4 text-gray-400">calendar_month</span>
              <input v-model="formulario.fecha_salida" required class="w-full pl-12 pr-4 py-3 bg-transparent border-none rounded-xl text-[#00236f] font-bold focus:outline-none" type="date"/>
            </div>
          </div>
          
          <div class="space-y-2 text-left">
            <label class="text-xs font-bold text-[#444651] uppercase tracking-wider block ml-1">Regreso (Opcional)</label>
            <div class="relative flex items-center border border-gray-200 rounded-xl bg-[#f3f4f6] focus-within:ring-2 focus-within:ring-[#006c49] focus-within:bg-white transition-all">
              <span class="material-symbols-outlined absolute left-4 text-gray-400">calendar_today</span>
              <input v-model="formulario.fecha_retorno" class="w-full pl-12 pr-4 py-3 bg-transparent border-none rounded-xl text-[#00236f] font-bold focus:outline-none" type="date"/>
            </div>
          </div>

        </div>

        <div class="mt-6 pt-6 border-t border-gray-100 flex flex-col md:flex-row items-center justify-between gap-6">
          
          <div class="flex items-center gap-4 text-left">
            <label class="relative inline-flex items-center cursor-pointer select-none">
              <input type="checkbox" v-model="formulario.optimizar_stopovers" class="sr-only peer"/>
              <div class="w-14 h-7 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-[#006c49]"></div>
            </label>
            <div>
              <span class="text-sm font-bold text-[#00236f] block">Optimizar Stopovers (24h - 72h)</span>
              <span class="text-xs text-[#444651]">Agrega una ciudad extra sin costo adicional</span>
            </div>
          </div>

          <button type="submit" class="w-full md:w-auto px-10 py-4 bg-[#00236f] text-white font-bold rounded-xl hover:bg-[#1e3a8a] hover:shadow-lg transition-all flex items-center justify-center gap-3 group active:scale-95">
            Buscar Itinerarios
            <span class="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
          </button>

        </div>
      </form>
    </section>

    <section class="py-16 px-4 max-w-[1280px] mx-auto">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div class="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:border-[#006c49]/40 transition-all text-left space-y-4">
          <div class="w-12 h-12 bg-[#6cf8bb]/20 rounded-xl flex items-center justify-center">
            <span class="material-symbols-outlined text-[#006c49] text-2xl">schedule</span>
          </div>
          <h3 class="text-xl font-bold text-[#00236f]">Stopovers Inteligentes</h3>
          <p class="text-sm text-[#444651] leading-relaxed">
            Descubre ciudades intermedias optimizando tu tiempo de escala. Convierte una espera aburrida en una mini-vacación planificada de 1 a 3 días.
          </p>
        </div>

        <div class="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:border-[#006c49]/40 transition-all text-left space-y-4">
          <div class="w-12 h-12 bg-[#6cf8bb]/20 rounded-xl flex items-center justify-center">
            <span class="material-symbols-outlined text-[#006c49] text-2xl">luggage</span>
          </div>
          <h3 class="text-xl font-bold text-[#00236f]">Motor de Reglas IATA</h3>
          <p class="text-sm text-[#444651] leading-relaxed">
            Valida cm y kg para cada aerolínea de tu trayecto. Evita multas sorpresa por diferencias de criterio entre aerolíneas aliadas o low-cost.
          </p>
        </div>

        <div class="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:border-[#006c49]/40 transition-all text-left space-y-4">
          <div class="w-12 h-12 bg-[#6cf8bb]/20 rounded-xl flex items-center justify-center">
            <span class="material-symbols-outlined text-[#006c49] text-2xl">notifications_active</span>
          </div>
          <h3 class="text-xl font-bold text-[#00236f]">Alertas Premium</h3>
          <p class="text-sm text-[#444651] leading-relaxed">
            Notificaciones push y SMTP en tiempo real sobre cambios de reglas de visado o restricciones de equipaje 24 horas antes de tu vuelo.
          </p>
        </div>

      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const formulario = ref({
  origen: '',
  destino: '',
  fecha_salida: '',
  fecha_retorno: '',
  optimizar_stopovers: true
});

const ejecutarBusqueda = () => {
  console.log('Datos capturados para el backend:', formulario.value);
};
</script>