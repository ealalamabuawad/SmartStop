<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { Plane } from 'lucide-vue-next';

const router = useRouter();
const registerForm = reactive({ name: '', email: '', password: '' });

const handleRegister = () => {
  console.log("Registrando usuario:", registerForm.name);
  router.push('/');
};
</script>

<template>
  <div class="max-w-md mx-auto mt-20 p-8 bg-white rounded-3xl shadow-xl border border-slate-100">
    <div class="flex items-center justify-center gap-2 mb-8">
      <div class="w-10 h-10 rounded-full bg-[#03254c] flex items-center justify-center text-white">
        <Plane class="w-5 h-5 -rotate-45" />
      </div>
      <span class="text-2xl font-black text-[#03254c]">SmartStop</span>
    </div>

    <h2 class="text-xl font-extrabold text-slate-900 mb-2">Crear nueva Cuenta</h2>
    <p class="text-xs text-slate-500 mb-6">Regístrate hoy y disfruta de alertas Premium de vuelos IATA.</p>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div>
        <label class="block text-xs font-bold text-slate-600 mb-1">Nombre Completo</label>
        <input type="text" required v-model="registerForm.name" placeholder="Sebastián Silva" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#03254c]" />
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-600 mb-1">Correo electrónico</label>
        <input type="email" required v-model="registerForm.email" placeholder="ejemplo@correo.cl" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#03254c]" />
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-600 mb-1">Contraseña</label>
        <input type="password" required v-model="registerForm.password" placeholder="••••••••" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#03254c]" />
      </div>
      <button type="submit" class="w-full bg-[#03254c] hover:bg-[#001c3d] text-white font-bold py-3 rounded-xl text-sm transition active:scale-95">Registrarse</button>
    </form>
    
    <div class="mt-6 text-center text-xs text-slate-500 font-medium">
      ¿Ya tienes cuenta? <router-link to="/ingreso" class="text-blue-600 hover:underline">Inicia sesión</router-link>
    </div>
  </div>
</template>