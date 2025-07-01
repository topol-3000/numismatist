<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
      <router-link to="/" class="navbar-brand d-flex align-items-center">
        <i class="fas fa-coins me-2"></i>
        <span class="fw-bold">Numismatist</span>
      </router-link>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item">
            <router-link to="/" class="nav-link" active-class="active">
              <i class="fas fa-home me-1"></i>
              Home
            </router-link>
          </li>
          <li v-if="authStore.isAuthenticated" class="nav-item">
            <router-link to="/collections" class="nav-link" active-class="active">
              <i class="fas fa-folder me-1"></i>
              Collections
            </router-link>
          </li>
          <li v-if="authStore.isAuthenticated" class="nav-item">
            <router-link to="/items" class="nav-link" active-class="active">
              <i class="fas fa-coins me-1"></i>
              Items
            </router-link>
          </li>
          <li class="nav-item">
            <router-link to="/about" class="nav-link" active-class="active">
              <i class="fas fa-info-circle me-1"></i>
              About
            </router-link>
          </li>
        </ul>

        <!-- Authentication Links -->
        <ul class="navbar-nav">
          <li v-if="!authStore.isAuthenticated" class="nav-item">
            <router-link to="/login" class="nav-link">
              <i class="fas fa-sign-in-alt me-1"></i>
              Login
            </router-link>
          </li>
          <li v-if="!authStore.isAuthenticated" class="nav-item">
            <router-link to="/register" class="nav-link">
              <i class="fas fa-user-plus me-1"></i>
              Register
            </router-link>
          </li>

          <!-- User Dropdown -->
          <li v-if="authStore.isAuthenticated" class="nav-item dropdown">
            <a
              class="nav-link dropdown-toggle d-flex align-items-center"
              href="#"
              id="navbarDropdown"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <div class="user-avatar me-2">
                <i class="fas fa-user-circle fa-lg"></i>
              </div>
              <span class="d-none d-lg-inline">{{ userDisplayName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="navbarDropdown">
              <li>
                <h6 class="dropdown-header">
                  <i class="fas fa-user me-2"></i>
                  {{ authStore.user?.email }}
                </h6>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <router-link to="/profile" class="dropdown-item">
                  <i class="fas fa-user-edit me-2"></i>
                  Profile
                </router-link>
              </li>
              <li>
                <router-link to="/settings" class="dropdown-item">
                  <i class="fas fa-cog me-2"></i>
                  Settings
                </router-link>
              </li>
              <li v-if="authStore.isAdmin">
                <router-link to="/admin" class="dropdown-item">
                  <i class="fas fa-shield-alt me-2"></i>
                  Admin Panel
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <button class="dropdown-item" @click="handleLogout">
                  <i class="fas fa-sign-out-alt me-2"></i>
                  Logout
                </button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userDisplayName = computed(() => {
  if (!authStore.user) return ''

  // If the user has a first/last name, use that, otherwise use email
  return authStore.user.email.split('@')[0]
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 1.5rem;
}

.user-avatar {
  color: #fff;
}

.dropdown-header {
  font-size: 0.875rem;
  color: #6c757d;
}

.nav-link {
  transition: color 0.2s ease-in-out;
}

.nav-link:hover {
  color: #ffffff !important;
}

.nav-link.active {
  font-weight: 600;
}

@media (max-width: 991.98px) {
  .navbar-nav {
    text-align: center;
  }

  .dropdown-menu {
    position: static !important;
    float: none;
    width: auto;
    margin-top: 0;
    background-color: transparent;
    border: 0;
    box-shadow: none;
  }

  .dropdown-item {
    color: rgba(255, 255, 255, 0.75);
    text-align: center;
  }

  .dropdown-item:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fff;
  }
}
</style>
