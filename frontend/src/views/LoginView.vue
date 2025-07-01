<template>
  <div class="container-fluid vh-100">
    <div class="row h-100">
      <!-- Left side - Hero Section -->
      <div
        class="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-primary text-white"
      >
        <div class="text-center">
          <i class="fas fa-coins fa-5x mb-4 opacity-75"></i>
          <h1 class="display-4 fw-bold mb-3">Numismatist</h1>
          <p class="lead mb-4">
            Manage your coin collection with ease. Track, organize, and discover new additions to
            your numismatic journey.
          </p>
          <div class="row text-center">
            <div class="col-4">
              <i class="fas fa-search fa-2x mb-2"></i>
              <p class="small">Discover</p>
            </div>
            <div class="col-4">
              <i class="fas fa-list fa-2x mb-2"></i>
              <p class="small">Organize</p>
            </div>
            <div class="col-4">
              <i class="fas fa-chart-line fa-2x mb-2"></i>
              <p class="small">Track Value</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side - Login Form -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center">
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/LoginForm.vue'
</script>

<style scoped>
.vh-100 {
  min-height: 100vh;
}

.bg-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}
</style>
