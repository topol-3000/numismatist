<template>
  <!-- Top navigation -->
  <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
    <div class="container-fluid">
      <button class="btn btn-primary" id="sidebarToggle" @click="toggleSidebar">
        <i class="fas fa-bars"></i>
      </button>

      <div class="navbar-nav ms-auto">
        <!-- User dropdown -->
        <div class="nav-item dropdown">
          <a
            class="nav-link dropdown-toggle d-flex align-items-center"
            href="#"
            id="navbarDropdown"
            role="button"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <img
              :src="userAvatar"
              class="rounded-circle me-2"
              width="32"
              height="32"
              alt="User Avatar"
            />
            {{ authStore.user?.email || 'User' }}
          </a>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
            <li>
              <router-link class="dropdown-item" :to="{ name: 'profile' }">
                <i class="fas fa-user me-2"></i>
                Profile
              </router-link>
            </li>
            <li>
              <router-link class="dropdown-item" :to="{ name: 'settings' }">
                <i class="fas fa-cog me-2"></i>
                Settings
              </router-link>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li>
              <a class="dropdown-item" href="#" @click="handleLogout">
                <i class="fas fa-sign-out-alt me-2"></i>
                Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// Computed user avatar (placeholder)
const userAvatar = computed(() => {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(
    authStore.user?.email || 'User'
  )}&background=007bff&color=fff&size=32`
})

const toggleSidebar = () => {
  const wrapper = document.getElementById('wrapper')
  if (wrapper) {
    wrapper.classList.toggle('toggled')
  }
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  // Initialize Bootstrap dropdowns
  const { Dropdown } = (window as any).bootstrap || {}
  if (Dropdown) {
    const dropdownElementList = document.querySelectorAll('.dropdown-toggle')
    dropdownElementList.forEach((dropdownToggleEl) => {
      new Dropdown(dropdownToggleEl)
    })
  }
})
</script>

<style scoped>
/* No additional styles needed - using Bootstrap classes */
</style>
