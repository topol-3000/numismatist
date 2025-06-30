<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-coins me-2"></i>
          Numismatist
        </router-link>
        
        <button 
          class="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/about">About</router-link>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

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
