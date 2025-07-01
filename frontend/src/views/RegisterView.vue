<template>
  <div class="container-fluid vh-100">
    <div class="row h-100">
      <!-- Left side - Hero Section -->
      <div
        class="col-lg-6 d-none d-lg-flex align-items-center justify-content-center bg-success text-white"
      >
        <div class="text-center">
          <i class="fas fa-user-plus fa-5x mb-4 opacity-75"></i>
          <h1 class="display-4 fw-bold mb-3">Join Numismatist</h1>
          <p class="lead mb-4">
            Start your numismatic journey today. Create an account to organize your collection and
            connect with fellow collectors.
          </p>
          <div class="row text-center">
            <div class="col-4">
              <i class="fas fa-shield-alt fa-2x mb-2"></i>
              <p class="small">Secure</p>
            </div>
            <div class="col-4">
              <i class="fas fa-users fa-2x mb-2"></i>
              <p class="small">Community</p>
            </div>
            <div class="col-4">
              <i class="fas fa-mobile-alt fa-2x mb-2"></i>
              <p class="small">Mobile Ready</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right side - Register Form -->
      <div class="col-lg-6 d-flex align-items-center justify-content-center">
        <RegisterForm />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import RegisterForm from '@/components/RegisterForm.vue'
</script>

<style scoped>
.vh-100 {
  min-height: 100vh;
}

.bg-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
}
</style>
