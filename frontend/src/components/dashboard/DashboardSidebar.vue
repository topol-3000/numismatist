<template>
  <!-- Sidebar -->
  <div class="border-end bg-white" id="sidebar-wrapper">
    <div class="sidebar-heading border-bottom bg-light">
      <i class="fas fa-coins me-2"></i>
      Numismatist
    </div>
    <div class="list-group list-group-flush">
      <router-link
        :to="{ name: 'dashboard' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'dashboard' }"
      >
        <i class="fas fa-tachometer-alt me-2"></i>
        Dashboard
      </router-link>
      <router-link
        :to="{ name: 'collections' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'collections' }"
      >
        <i class="fas fa-folder me-2"></i>
        Collections
      </router-link>
      <router-link
        :to="{ name: 'items' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'items' }"
      >
        <i class="fas fa-coins me-2"></i>
        Items
      </router-link>
      <router-link
        :to="{ name: 'dealers' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'dealers' }"
      >
        <i class="fas fa-store me-2"></i>
        Dealers
      </router-link>
      <router-link
        :to="{ name: 'profile' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'profile' }"
      >
        <i class="fas fa-user me-2"></i>
        Profile
      </router-link>
      <router-link
        :to="{ name: 'settings' }"
        class="list-group-item list-group-item-action"
        :class="{ active: $route.name === 'settings' }"
      >
        <i class="fas fa-cog me-2"></i>
        Settings
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
// No additional logic needed - just navigation links
</script>

<style scoped>
#sidebar-wrapper {
  min-height: 100vh;
  margin-left: -15rem;
  transition: margin 0.25s ease-out;
  width: 15rem;
  position: fixed;
  z-index: 1000;
}

.sidebar-heading {
  padding: 0.875rem 1.25rem;
  font-size: 1.2rem;
  font-weight: bold;
}

.list-group-item {
  border: none;
  border-radius: 0;
}

.list-group-item.active {
  background-color: #007bff;
  border-color: #007bff;
}

/* Responsive adjustments */
@media (min-width: 768px) {
  #sidebar-wrapper {
    margin-left: 0;
  }
}
</style>
