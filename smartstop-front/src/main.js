import { createApp } from 'vue'
import App from './App.vue'
import router from './router/indice.js' 
import './assets/estilos.css'

const app = createApp(App)
app.use(router)
app.mount('#app')