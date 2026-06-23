<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { Plane } from 'lucide-vue-next';

const router = useRouter();
const loginForm = reactive({ email: '', password: '' });

const handleLogin = () => {
  console.log("Ingresando con:", loginForm.email);
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

    <h2 class="text-xl font-extrabold text-slate-900 mb-2">Iniciar Sesión</h2>
    <p class="text-xs text-slate-500 mb-6">Accede a tu cuenta para auditar equipajes y guardar tus reservas.</p>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <div>
        <label class="block text-xs font-bold text-slate-600 mb-1">Correo electrónico</label>
        <input type="email" required v-model="loginForm.email" placeholder="ejemplo@correo.cl" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#03254c]" />
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-600 mb-1">Contraseña</label>
        <input type="password" required v-model="loginForm.password" placeholder="••••••••" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#03254c]" />
      </div>
      <button type="submit" class="w-full bg-[#03254c] hover:bg-[#001c3d] text-white font-bold py-3 rounded-xl text-sm transition active:scale-95">Ingresar</button>
    </form>
    
    <div class="mt-6 text-center text-xs text-slate-500 font-medium">
      ¿No tienes cuenta? <router-link to="/registro" class="text-blue-600 hover:underline">Regístrate aquí</router-link>
    </div>
  </div>
</template>