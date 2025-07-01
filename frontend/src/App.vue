<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'

const authStore = useAuthStore()

onMounted(() => {
  // Initialize authentication state on app startup
  authStore.initializeAuth()
})
</script>

<template>
  <div id="app">
    <!-- Navigation -->
    <AppNavbar />

    <!-- Main content -->
    <main class="flex-grow-1">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="bg-light py-4 mt-5">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <p class="mb-0">&copy; 2025 Numismatist. All rights reserved.</p>
          </div>
          <div class="col-md-6 text-end">
            <p class="mb-0">Manage your coin collections with ease</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar-brand {
  font-weight: bold;
}

.nav-link.router-link-active {
  color: #fff !important;
  font-weight: bold;
}
</style>
