<script setup>
import { ref, onMounted } from 'vue';
import { Plane, Facebook, Twitter, Instagram, Linkedin } from 'lucide-vue-next';

const appConfig = ref({ brandName: '', brandDesc: '', rights: '' });
const siteMap = ref([]);
const socialMedia = ref([]);

onMounted(() => {
  appConfig.value = {
    brandName: 'SmartStop',
    brandDesc: 'La forma inteligente de buscar vuelos con reglas IATA y stopovers integrados para ahorrar en tu próximo destino.',
    rights: '© 2026 SmartStop TravelTech. Todos los derechos reservados.'
  };

  siteMap.value = [
    {
      id: 'company',
      title: 'Empresa',
      links: [
        { text: 'Acerca de nosotros', href: '/#acerca' },
        { text: 'Suscripción', href: '/#suscripcion' },
        { text: 'Prensa', href: '/#prensa' },
        { text: 'Empleo', href: '/#empleo' }
      ]
    },
    {
      id: 'support',
      title: 'Soporte',
      links: [
        { text: 'Ayuda', href: '/#ayuda' },
        { text: 'Contacto', href: '/#contacto' },
        { text: 'Privacidad', href: '/#privacidad' },
        { text: 'Términos y condiciones', href: '/#terminos' }
      ]
    }
  ];

  socialMedia.value = [
    { id: 'fb', icon: Facebook, url: 'https://facebook.com' },
    { id: 'tw', icon: Twitter, url: 'https://twitter.com' },
    { id: 'ig', icon: Instagram, url: 'https://instagram.com' },
    { id: 'in', icon: Linkedin, url: 'https://linkedin.com' }
  ];
});
</script>

<template>
  <footer class="w-full bg-[#03254c] text-white py-14 mt-20">
    <div class="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-10">
      
      <div class="flex flex-col gap-4">
        <router-link to="/" class="flex items-center gap-2 cursor-pointer">
          <div class="w-8 h-8 rounded-full bg-white flex items-center justify-center text-[#03254c]">
            <Plane class="w-4.5 h-4.5 -rotate-45" />
          </div>
          <span class="text-lg font-extrabold tracking-tight">{{ appConfig.brandName }}</span>
        </router-link>
        <p class="text-xs text-slate-300 leading-relaxed max-w-sm">{{ appConfig.brandDesc }}</p>
      </div>

      <div v-for="section in siteMap" :key="section.id" class="flex flex-col gap-3">
        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest">{{ section.title }}</h4>
        <ul class="flex flex-col gap-2 text-sm text-slate-200">
          <li v-for="link in section.links" :key="link.text">
            <a :href="link.href" class="hover:text-blue-200 transition-colors">{{ link.text }}</a>
          </li>
        </ul>
      </div>

      <div class="flex flex-col gap-4 md:items-end">
        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest md:text-right w-full">Síguenos</h4>
        <div class="flex items-center gap-3">
          <a v-for="network in socialMedia" :key="network.id" :href="network.url" target="_blank" rel="noreferrer" class="w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors">
            <component :is="network.icon" class="w-4.5 h-4.5" />
          </a>
        </div>
      </div>

    </div>

    <div class="max-w-7xl mx-auto px-6 border-t border-slate-700/50 mt-10 pt-6 text-center text-xs text-slate-400">
      {{ appConfig.rights }}
    </div>
  </footer>
</template>