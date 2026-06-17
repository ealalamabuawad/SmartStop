<template>
  <div class="min-h-[70vh] flex items-center justify-center px-4">
    <div class="glass-card p-8 rounded-2xl shadow-2xl bg-white/80 max-w-md w-full space-y-6">
      <div class="text-center space-y-2">
        <h2 class="text-3xl font-bold text-primary">Iniciar Sesión</h2>
        <p class="text-sm text-on-surface-variant">Ingresa tus credenciales para acceder a SmartStop</p>
      </div>
      <form class="space-y-4">
        <div class="space-y-1">
          <label class="text-sm font-bold text-on-surface-variant ml-1">Correo Electrónico</label>
          <input type="email" required class="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-secondary" placeholder="viajero@correo.cl" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-bold text-on-surface-variant ml-1">Contraseña</label>
          <input type="password" required class="w-full px-4 py-3 bg-surface-container-low border-none rounded-xl focus:ring-2 focus:ring-secondary" placeholder="••••••••" />
        </div>
        <button type="submit" class="w-full py-4 bg-primary text-on-primary font-bold rounded-xl hover:shadow-xl transition-all">
          Autenticar
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
</script>