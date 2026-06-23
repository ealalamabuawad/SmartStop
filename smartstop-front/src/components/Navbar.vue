<script setup>
import { Plane, User, X } from 'lucide-vue-next';
import { ref, onMounted } from 'vue';

defineProps({
  userEmail: {
    type: String,
    default: null
  }
});

defineEmits(['logout']);

const navLinks = ref([]);

onMounted(() => {
  navLinks.value = [
    { text: 'Buscador', to: '/' },
    { text: 'Acerca de nosotros', to: '/#acerca' },
    { text: 'Suscripción', to: '/#suscripcion' }
  ];
});
</script>

<template>
  <header class="w-full max-w-7xl mx-auto px-4 pt-6 pb-2 shrink-0">
    <div class="bg-white/90 backdrop-blur-md rounded-2xl shadow-md border border-slate-100 px-6 py-4 flex items-center justify-between">
      <router-link to="/" class="flex items-center gap-2 cursor-pointer group">
        <div class="w-10 h-10 rounded-full bg-[#03254c] flex items-center justify-center text-white transition-all duration-300 group-hover:rotate-12">
          <Plane class="w-5 h-5 -rotate-45" />
        </div>
        <span class="text-xl font-extrabold tracking-tight text-[#03254c]">SmartStop</span>
      </router-link>

      <nav class="hidden md:flex items-center gap-6">
        <router-link 
          v-for="link in navLinks" 
          :key="link.text" 
          :to="link.to" 
          class="text-sm font-medium text-slate-500 hover:text-[#03254c] transition-colors"
        >
          {{ link.text }}
        </router-link>
      </nav>

      <div class="flex items-center gap-3">
        <div v-if="userEmail" class="flex items-center gap-3 bg-slate-50 border border-slate-100 rounded-xl py-1.5 pl-3 pr-2">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-blue-100 text-[#03254c] flex items-center justify-center">
              <User class="w-3.5 h-3.5" />
            </span>
            <span class="text-xs font-semibold text-slate-700 max-w-[120px] truncate">{{ userEmail }}</span>
          </div>
          <button @click="$emit('logout')" class="p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors">
            <X class="w-4 h-4" />
          </button>
        </div>
        <template v-else>
          <router-link to="/ingreso" class="px-4 py-2 text-xs font-semibold text-[#03254c] bg-white border border-slate-200 hover:border-[#03254c] hover:bg-[#03254c]/5 rounded-lg active:scale-95 transition-all">
            Iniciar Sesión
          </router-link>
          <router-link to="/registro" class="px-4 py-2 text-xs font-semibold text-white bg-[#03254c] hover:bg-[#001f3f] rounded-lg active:scale-95 transition-all shadow-sm">
            Registro
          </router-link>
        </template>
      </div>
    </div>
  </header>
</template>