<template>
  <DashboardLayout>
    <div class="container-fluid p-4">
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-0">Items</h1>
              <p class="text-muted">Manage your coin collection items</p>
            </div>
            <button class="btn btn-primary">
              <i class="fas fa-plus me-2"></i>
              Add Item
            </button>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="row mb-4">
        <div class="col-lg-6">
          <div class="input-group">
            <span class="input-group-text"><i class="fas fa-search"></i></span>
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search items..."
            />
          </div>
        </div>
        <div class="col-lg-3">
          <select v-model="selectedCollection" class="form-select">
            <option value="">All Collections</option>
            <option value="1">Lincoln Pennies</option>
            <option value="2">Mercury Dimes</option>
            <option value="3">Morgan Dollars</option>
          </select>
        </div>
        <div class="col-lg-3">
          <select v-model="sortBy" class="form-select">
            <option value="name">Sort by Name</option>
            <option value="year">Sort by Year</option>
            <option value="value">Sort by Value</option>
            <option value="condition">Sort by Condition</option>
          </select>
        </div>
      </div>

      <!-- Items Table -->
      <div class="card shadow">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Image</th>
                  <th>Name</th>
                  <th>Year</th>
                  <th>Mint Mark</th>
                  <th>Condition</th>
                  <th>Collection</th>
                  <th>Value</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in filteredItems" :key="item.id">
                  <td>
                    <div
                      class="coin-placeholder bg-light d-flex align-items-center justify-content-center"
                      style="width: 50px; height: 50px; border-radius: 50%"
                    >
                      <i class="fas fa-coins text-muted"></i>
                    </div>
                  </td>
                  <td>
                    <div class="fw-bold">{{ item.name }}</div>
                    <div class="text-muted small">{{ item.description }}</div>
                  </td>
                  <td>{{ item.year }}</td>
                  <td>
                    <span v-if="item.mintMark" class="badge bg-secondary">{{ item.mintMark }}</span>
                    <span v-else class="text-muted">-</span>
                  </td>
                  <td>
                    <span class="badge" :class="getConditionBadgeClass(item.condition)">
                      {{ item.condition }}
                    </span>
                  </td>
                  <td>{{ item.collection }}</td>
                  <td class="fw-bold">${{ item.value }}</td>
                  <td>
                    <div class="btn-group" role="group">
                      <button class="btn btn-sm btn-outline-primary" title="View">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-secondary" title="Edit">
                        <i class="fas fa-edit"></i>
                      </button>
                      <button class="btn btn-sm btn-outline-danger" title="Delete">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty state -->
          <div v-if="filteredItems.length === 0" class="text-center py-5">
            <i class="fas fa-coins fa-4x text-muted mb-4"></i>
            <h3>No Items Found</h3>
            <p class="text-muted mb-4">
              {{ searchQuery ? 'No items match your search criteria' : 'Add your first coin to get started' }}
            </p>
            <button class="btn btn-primary btn-lg">
              <i class="fas fa-plus me-2"></i>
              Add First Item
            </button>
          </div>

          <!-- Pagination -->
          <nav v-if="filteredItems.length > 0" aria-label="Items pagination" class="mt-4">
            <ul class="pagination justify-content-center">
              <li class="page-item disabled">
                <span class="page-link">Previous</span>
              </li>
              <li class="page-item active">
                <span class="page-link">1</span>
              </li>
              <li class="page-item">
                <a class="page-link" href="#">2</a>
              </li>
              <li class="page-item">
                <a class="page-link" href="#">3</a>
              </li>
              <li class="page-item">
                <a class="page-link" href="#">Next</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

// Reactive data
const searchQuery = ref('')
const selectedCollection = ref('')
const sortBy = ref('name')

// Mock data - replace with actual API calls
const items = ref([
  {
    id: 1,
    name: '1909-S VDB Lincoln Penny',
    description: 'Key date wheat penny',
    year: '1909',
    mintMark: 'S',
    condition: 'Very Fine',
    collection: 'Lincoln Pennies',
    value: '750.00',
  },
  {
    id: 2,
    name: '1916-D Mercury Dime',
    description: 'Semi-key date',
    year: '1916',
    mintMark: 'D',
    condition: 'Extremely Fine',
    collection: 'Mercury Dimes',
    value: '1,200.00',
  },
  {
    id: 3,
    name: '1893-S Morgan Dollar',
    description: 'Key date Morgan',
    year: '1893',
    mintMark: 'S',
    condition: 'About Uncirculated',
    collection: 'Morgan Dollars',
    value: '2,500.00',
  },
  {
    id: 4,
    name: '1943 Steel Penny',
    description: 'Wartime composition',
    year: '1943',
    mintMark: '',
    condition: 'Uncirculated',
    collection: 'Lincoln Pennies',
    value: '0.50',
  },
  {
    id: 5,
    name: '1921 Morgan Dollar',
    description: 'Common date high relief',
    year: '1921',
    mintMark: '',
    condition: 'Mint State',
    collection: 'Morgan Dollars',
    value: '45.00',
  },
])

// Computed filtered items
const filteredItems = computed(() => {
  let filtered = items.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query) ||
        item.year.includes(query)
    )
  }

  // Filter by collection
  if (selectedCollection.value) {
    filtered = filtered.filter((item) => item.collection === getCollectionName(selectedCollection.value))
  }

  // Sort items
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'year':
        return parseInt(b.year) - parseInt(a.year)
      case 'value':
        return parseFloat(b.value) - parseFloat(a.value)
      case 'condition':
        return a.condition.localeCompare(b.condition)
      default:
        return a.name.localeCompare(b.name)
    }
  })

  return filtered
})

// Helper functions
const getConditionBadgeClass = (condition: string) => {
  const conditionMap: Record<string, string> = {
    'Poor': 'bg-danger',
    'Fair': 'bg-warning',
    'Good': 'bg-info',
    'Very Good': 'bg-info',
    'Fine': 'bg-primary',
    'Very Fine': 'bg-primary',
    'Extremely Fine': 'bg-success',
    'About Uncirculated': 'bg-success',
    'Uncirculated': 'bg-success',
    'Mint State': 'bg-success',
  }
  return conditionMap[condition] || 'bg-secondary'
}

const getCollectionName = (id: string) => {
  const collections: Record<string, string> = {
    '1': 'Lincoln Pennies',
    '2': 'Mercury Dimes',
    '3': 'Morgan Dollars',
  }
  return collections[id] || ''
}
</script>

<style scoped>
.coin-placeholder {
  border: 2px dashed #dee2e6;
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
}

.btn-group .btn {
  padding: 0.25rem 0.5rem;
}
</style>
