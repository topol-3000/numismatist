import './assets/main.css'
// Import Swiper styles
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'jsvectormap/dist/jsvectormap.css'
import 'flatpickr/dist/flatpickr.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import VueApexCharts from 'vue3-apexcharts'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.component('apexchart', VueApexCharts)

// Initialize auth store after pinia is set up
import { useAuthStore } from '@/stores/auth'

// Initialize auth store
const authStore = useAuthStore()
authStore.initialize()

app.mount('#app')
