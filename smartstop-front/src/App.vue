<script setup>
import { ref } from 'vue';

import Navbar from './components/Navbar.vue';
import Footer from './components/Footer.vue';

const userEmail = ref(null);

const handleLogout = () => {
  userEmail.value = null;
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-[#eaf4fc] via-[#f5f8fa] to-[#eef2f6] text-[#03254c] font-sans flex flex-col">
    
    <Navbar :userEmail="userEmail" @logout="handleLogout" />

    <main class="flex-grow w-full mt-6">
      <router-view></router-view>
    </main>

    <Footer />

  </div>
</template>

<style>
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] { -moz-appearance: textfield; }

html { scroll-behavior: smooth; }
</style>
