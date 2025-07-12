<template>
  <DashboardLayout>
    <div class="container-fluid p-4">
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-0">Collections</h1>
              <p class="text-muted">Manage your coin collections</p>
            </div>
            <button class="btn btn-primary">
              <i class="fas fa-plus me-2"></i>
              New Collection
            </button>
          </div>
        </div>
      </div>

      <!-- Collections Grid -->
      <div class="row">
        <div v-for="collection in collections" :key="collection.id" class="col-lg-4 col-md-6 mb-4">
          <div class="card shadow h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="card-title">{{ collection.name }}</h5>
                <div class="dropdown">
                  <button
                    class="btn btn-sm btn-outline-secondary dropdown-toggle"
                    type="button"
                    data-bs-toggle="dropdown"
                  >
                    <i class="fas fa-ellipsis-v"></i>
                  </button>
                  <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#">Edit</a></li>
                    <li><a class="dropdown-item" href="#">Share</a></li>
                    <li><hr class="dropdown-divider" /></li>
                    <li><a class="dropdown-item text-danger" href="#">Delete</a></li>
                  </ul>
                </div>
              </div>
              <p class="card-text text-muted">{{ collection.description }}</p>
              <div class="row text-center mb-3">
                <div class="col-6">
                  <div class="fw-bold">{{ collection.itemCount }}</div>
                  <div class="text-muted small">Items</div>
                </div>
                <div class="col-6">
                  <div class="fw-bold">${{ collection.totalValue }}</div>
                  <div class="text-muted small">Value</div>
                </div>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-primary btn-sm flex-fill">View Items</button>
                <button class="btn btn-outline-primary btn-sm">
                  <i class="fas fa-edit"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="collections.length === 0" class="col-12">
          <div class="text-center py-5">
            <i class="fas fa-folder fa-4x text-muted mb-4"></i>
            <h3>No Collections Yet</h3>
            <p class="text-muted mb-4">
              Create your first collection to start organizing your coins
            </p>
            <button class="btn btn-primary btn-lg">
              <i class="fas fa-plus me-2"></i>
              Create First Collection
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

// Mock data - replace with actual API calls
const collections = ref([
  {
    id: 1,
    name: 'Lincoln Pennies',
    description: 'Complete wheat penny collection from 1909-1958',
    itemCount: 45,
    totalValue: '2,450.00',
  },
  {
    id: 2,
    name: 'Mercury Dimes',
    description: 'Silver dimes 1916-1945 in various conditions',
    itemCount: 32,
    totalValue: '1,850.00',
  },
  {
    id: 3,
    name: 'Morgan Dollars',
    description: 'Classic silver dollars from the late 1800s',
    itemCount: 18,
    totalValue: '8,750.00',
  },
  {
    id: 4,
    name: 'State Quarters',
    description: '50 State Quarters Program collection',
    itemCount: 50,
    totalValue: '125.00',
  },
])
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}
</style>
