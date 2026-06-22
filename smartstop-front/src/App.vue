<template>
  <div
    class="bg-background text-on-surface font-body-md min-h-screen flex flex-col"
  >
    <nav
      class="fixed top-0 left-0 right-0 z-50 bg-surface-container-lowest/80 backdrop-blur-xl border-b border-white/10 shadow-sm h-20"
    >
      <div
        class="flex justify-between items-center h-full px-margin-desktop max-w-container-max mx-auto"
      >
        <div class="flex items-center gap-12">
          <router-link
            to="/"
            class="text-primary font-bold text-2xl tracking-tight"
            >✈️ SmartStop</router-link
          >

          <div class="hidden md:flex items-center gap-8">
            <!-- Buscar Vuelos -->
            <router-link
              to="/"
              class="text-on-surface-variant hover:text-primary transition-colors pb-1"
              exact-active-class="border-b-2 border-primary text-primary font-bold"
            >
              Buscar Vuelos
            </router-link>

            <!-- Validador de Equipaje -->
            <router-link
              to="/validador"
              class="text-on-surface-variant hover:text-primary transition-colors pb-1"
              active-class="border-b-2 border-primary text-primary font-bold"
            >
              Validador de Equipaje
            </router-link>

            <!-- Alertas Premium -->
            <a
              class="text-on-surface-variant hover:text-primary transition-colors pb-1"
              href="#"
            >
              Alertas Premium
            </a>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <router-link
            to="/ingreso"
            class="px-6 py-2 border-2 border-primary text-primary font-bold rounded-lg hover:bg-primary/5 transition-all"
          >
            Iniciar Sesión
          </router-link>
          <button
            class="px-6 py-2.5 bg-primary text-on-primary font-bold rounded-lg hover:opacity-90 transition-all shadow-md"
          >
            Registrarse
          </button>
        </div>
      </div>
    </nav>

    <main class="flex-grow pt-20">
      <router-view></router-view>
    </main>

    <footer
      class="bg-surface-container-lowest border-t border-outline-variant py-8 mt-auto"
    >
      <div
        class="px-margin-desktop max-w-container-max mx-auto flex flex-col md:flex-row justify-between items-center gap-4"
      >
        <p class="text-on-surface-variant text-sm">
          © 2026 SmartStop TravelTech.
        </p>
        <div class="flex gap-6">
          <a class="text-outline hover:text-primary transition-colors" href="#"
            ><span class="material-symbols-outlined">public</span></a
          >
          <a class="text-outline hover:text-primary transition-colors" href="#"
            ><span class="material-symbols-outlined">mail</span></a
          >
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup></script>
