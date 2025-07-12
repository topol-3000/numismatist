<template>
  <DashboardLayout>
    <div class="container-fluid p-4">
      <!-- Welcome Header -->
      <div class="row mb-4">
        <div class="col-12">
          <h1 class="h3 mb-0">
            Welcome back, {{ authStore.user?.email?.split('@')[0] || 'User' }}!
          </h1>
          <p class="text-muted">Here's an overview of your numismatic collection</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col me-2">
                  <div class="text-xs fw-bold text-primary text-uppercase mb-1">
                    Total Collections
                  </div>
                  <div class="h5 mb-0 fw-bold text-gray-800">{{ stats.totalCollections }}</div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-folder fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col me-2">
                  <div class="text-xs fw-bold text-success text-uppercase mb-1">Total Items</div>
                  <div class="h5 mb-0 fw-bold text-gray-800">{{ stats.totalItems }}</div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-coins fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col me-2">
                  <div class="text-xs fw-bold text-info text-uppercase mb-1">Estimated Value</div>
                  <div class="h5 mb-0 fw-bold text-gray-800">${{ stats.estimatedValue }}</div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-dollar-sign fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col me-2">
                  <div class="text-xs fw-bold text-warning text-uppercase mb-1">
                    Trusted Dealers
                  </div>
                  <div class="h5 mb-0 fw-bold text-gray-800">{{ stats.trustedDealers }}</div>
                </div>
                <div class="col-auto">
                  <i class="fas fa-store fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Content Row -->
      <div class="row">
        <!-- Recent Items -->
        <div class="col-lg-6 mb-4">
          <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
              <h6 class="m-0 fw-bold text-primary">Recent Items</h6>
              <router-link :to="{ name: 'items' }" class="btn btn-primary btn-sm">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="recentItems.length > 0">
                <div
                  v-for="item in recentItems"
                  :key="item.id"
                  class="d-flex align-items-center py-2 border-bottom"
                >
                  <div class="me-3">
                    <i class="fas fa-coins fa-2x text-primary"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-bold">{{ item.name }}</div>
                    <div class="text-muted small">{{ item.description }}</div>
                  </div>
                  <div class="text-end">
                    <div class="fw-bold">${{ item.value }}</div>
                    <div class="text-muted small">{{ item.year }}</div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <i class="fas fa-coins fa-3x text-muted mb-3"></i>
                <p class="text-muted">No items added yet</p>
                <router-link :to="{ name: 'items' }" class="btn btn-primary">Add Your First Item</router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Collections Overview -->
        <div class="col-lg-6 mb-4">
          <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
              <h6 class="m-0 fw-bold text-primary">Collections</h6>
              <router-link :to="{ name: 'collections' }" class="btn btn-primary btn-sm">
                View All
              </router-link>
            </div>
            <div class="card-body">
              <div v-if="collections.length > 0">
                <div
                  v-for="collection in collections"
                  :key="collection.id"
                  class="d-flex align-items-center py-2 border-bottom"
                >
                  <div class="me-3">
                    <i class="fas fa-folder fa-2x text-success"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="fw-bold">{{ collection.name }}</div>
                    <div class="text-muted small">{{ collection.description }}</div>
                  </div>
                  <div class="text-end">
                    <div class="fw-bold">{{ collection.itemCount }} items</div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4">
                <i class="fas fa-folder fa-3x text-muted mb-3"></i>
                <p class="text-muted">No collections created yet</p>
                <router-link :to="{ name: 'collections' }" class="btn btn-primary">
                  Create Your First Collection
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row">
        <div class="col-12">
          <div class="card shadow">
            <div class="card-header py-3">
              <h6 class="m-0 fw-bold text-primary">Quick Actions</h6>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3 mb-3">
                  <router-link :to="{ name: 'items' }" class="btn btn-outline-primary btn-lg w-100">
                    <i class="fas fa-plus fa-2x mb-2 d-block"></i>
                    Add Item
                  </router-link>
                </div>
                <div class="col-md-3 mb-3">
                  <router-link :to="{ name: 'collections' }" class="btn btn-outline-success btn-lg w-100">
                    <i class="fas fa-folder-plus fa-2x mb-2 d-block"></i>
                    New Collection
                  </router-link>
                </div>
                <div class="col-md-3 mb-3">
                  <router-link :to="{ name: 'dealers' }" class="btn btn-outline-info btn-lg w-100">
                    <i class="fas fa-search fa-2x mb-2 d-block"></i>
                    Find Dealers
                  </router-link>
                </div>
                <div class="col-md-3 mb-3">
                  <router-link :to="{ name: 'profile' }" class="btn btn-outline-warning btn-lg w-100">
                    <i class="fas fa-chart-line fa-2x mb-2 d-block"></i>
                    View Reports
                  </router-link>
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
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

const authStore = useAuthStore()

// Mock data - replace with actual API calls later
const stats = ref({
  totalCollections: 12,
  totalItems: 284,
  estimatedValue: '15,420',
  trustedDealers: 8,
})

const recentItems = ref([
  {
    id: 1,
    name: '1909-S VDB Lincoln Penny',
    description: 'Very Fine condition',
    value: '750.00',
    year: '1909',
  },
  {
    id: 2,
    name: '1916-D Mercury Dime',
    description: 'Extremely Fine',
    value: '1,200.00',
    year: '1916',
  },
  {
    id: 3,
    name: '1893-S Morgan Dollar',
    description: 'About Uncirculated',
    value: '2,500.00',
    year: '1893',
  },
])

const collections = ref([
  {
    id: 1,
    name: 'Lincoln Pennies',
    description: 'Complete wheat penny collection',
    itemCount: 45,
  },
  {
    id: 2,
    name: 'Mercury Dimes',
    description: 'Silver dimes 1916-1945',
    itemCount: 32,
  },
  {
    id: 3,
    name: 'Morgan Dollars',
    description: 'Classic silver dollars',
    itemCount: 18,
  },
])
</script>

<style scoped>
.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}

.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}

.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}

.text-gray-800 {
  color: #5a5c69 !important;
}

.text-gray-300 {
  color: #dddfeb !important;
}

.text-xs {
  font-size: 0.7rem;
}
</style>
