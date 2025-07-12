<template>
  <DashboardLayout>
    <div class="container-fluid px-4">
      <!-- Page Header -->
      <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
        <h1 class="h2">
          <i class="fas fa-user me-2"></i>
          Profile
        </h1>
        <div class="btn-toolbar mb-2 mb-md-0">
          <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary">
              <i class="fas fa-edit me-1"></i>
              Edit Profile
            </button>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Profile Card -->
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-center">
              <img
                :src="userAvatar"
                class="rounded-circle mb-3"
                width="150"
                height="150"
                alt="Profile Picture"
              />
              <h5 class="card-title">{{ (user as any)?.name || 'John Doe' }}</h5>
              <p class="card-text text-muted">{{ (user as any)?.email || 'john.doe@example.com' }}</p>
              <p class="card-text">
                <small class="text-muted">Member since {{ memberSince }}</small>
              </p>
              <button class="btn btn-primary btn-sm">
                <i class="fas fa-camera me-1"></i>
                Change Photo
              </button>
            </div>
          </div>

          <!-- Quick Stats -->
          <div class="card mt-3">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-chart-bar me-2"></i>
                Quick Stats
              </h6>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-4">
                  <h4 class="text-primary">{{ stats.totalItems }}</h4>
                  <small class="text-muted">Items</small>
                </div>
                <div class="col-4">
                  <h4 class="text-success">{{ stats.totalCollections }}</h4>
                  <small class="text-muted">Collections</small>
                </div>
                <div class="col-4">
                  <h4 class="text-warning">{{ stats.totalValue }}</h4>
                  <small class="text-muted">Value</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Details -->
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-info-circle me-2"></i>
                Personal Information
              </h6>
            </div>
            <div class="card-body">
              <form>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="firstName" class="form-label">First Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="firstName"
                      v-model="profile.firstName"
                      readonly
                    />
                  </div>
                  <div class="col-md-6">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="lastName"
                      v-model="profile.lastName"
                      readonly
                    />
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="email" class="form-label">Email</label>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="profile.email"
                      readonly
                    />
                  </div>
                  <div class="col-md-6">
                    <label for="phone" class="form-label">Phone</label>
                    <input
                      type="tel"
                      class="form-control"
                      id="phone"
                      v-model="profile.phone"
                      readonly
                    />
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-12">
                    <label for="bio" class="form-label">Bio</label>
                    <textarea
                      class="form-control"
                      id="bio"
                      rows="3"
                      v-model="profile.bio"
                      readonly
                      placeholder="Tell us about yourself..."
                    ></textarea>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="country" class="form-label">Country</label>
                    <select class="form-select" id="country" v-model="profile.country" disabled>
                      <option value="">Select Country</option>
                      <option value="us">United States</option>
                      <option value="uk">United Kingdom</option>
                      <option value="ca">Canada</option>
                      <option value="au">Australia</option>
                      <option value="de">Germany</option>
                      <option value="fr">France</option>
                    </select>
                  </div>
                  <div class="col-md-6">
                    <label for="timezone" class="form-label">Timezone</label>
                    <select class="form-select" id="timezone" v-model="profile.timezone" disabled>
                      <option value="">Select Timezone</option>
                      <option value="EST">Eastern Standard Time</option>
                      <option value="CST">Central Standard Time</option>
                      <option value="MST">Mountain Standard Time</option>
                      <option value="PST">Pacific Standard Time</option>
                      <option value="GMT">Greenwich Mean Time</option>
                    </select>
                  </div>
                </div>
              </form>
            </div>
          </div>

          <!-- Collecting Preferences -->
          <div class="card mt-3">
            <div class="card-header">
              <h6 class="mb-0">
                <i class="fas fa-heart me-2"></i>
                Collecting Preferences
              </h6>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>Favorite Categories</h6>
                  <div class="d-flex flex-wrap gap-1">
                    <span
                      v-for="category in preferences.favoriteCategories"
                      :key="category"
                      class="badge bg-primary"
                    >
                      {{ category }}
                    </span>
                  </div>
                </div>
                <div class="col-md-6">
                  <h6>Collecting Focus</h6>
                  <div class="d-flex flex-wrap gap-1">
                    <span
                      v-for="focus in preferences.collectingFocus"
                      :key="focus"
                      class="badge bg-secondary"
                    >
                      {{ focus }}
                    </span>
                  </div>
                </div>
              </div>
              <hr />
              <div class="row">
                <div class="col-md-6">
                  <h6>Experience Level</h6>
                  <span class="badge bg-success">{{ preferences.experienceLevel }}</span>
                </div>
                <div class="col-md-6">
                  <h6>Budget Range</h6>
                  <span class="badge bg-warning text-dark">{{ preferences.budgetRange }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

const authStore = useAuthStore()

// Mock user data
const user = computed(() => authStore.user || {})

const profile = ref({
  firstName: 'John',
  lastName: 'Doe',
  email: (user.value as any)?.email || 'john.doe@example.com',
  phone: '+1 (555) 123-4567',
  bio: 'Passionate numismatist with over 10 years of experience collecting rare coins and currency. Specializing in ancient Roman coins and early American currency.',
  country: 'us',
  timezone: 'EST'
})

const stats = ref({
  totalItems: 247,
  totalCollections: 8,
  totalValue: '$12,450'
})

const preferences = ref({
  favoriteCategories: ['Ancient Coins', 'US Currency', 'World Coins'],
  collectingFocus: ['Historical Value', 'Rarity', 'Condition'],
  experienceLevel: 'Advanced',
  budgetRange: '$500 - $2000'
})

const memberSince = computed(() => {
  return new Date(2020, 2, 15).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long'
  })
})

const userAvatar = computed(() => {
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(
    `${profile.value.firstName} ${profile.value.lastName}`
  )}&background=007bff&color=fff&size=150`
})
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.badge {
  font-size: 0.75rem;
}

.form-control:read-only,
.form-select:disabled {
  background-color: #f8f9fa;
}

.gap-1 {
  gap: 0.25rem;
}
</style>
