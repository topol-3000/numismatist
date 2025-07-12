<template>
  <DashboardLayout>
    <div class="container-fluid p-4">
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-0">Dealers</h1>
              <p class="text-muted">Find and manage trusted coin dealers</p>
            </div>
            <button class="btn btn-primary">
              <i class="fas fa-plus me-2"></i>
              Add Dealer
            </button>
          </div>
        </div>
      </div>

    <!-- Search and Filters -->
    <div class="row mb-4">
      <div class="col-lg-4">
        <div class="input-group">
          <span class="input-group-text"><i class="fas fa-search"></i></span>
          <input
            v-model="searchQuery"
            type="text"
            class="form-control"
            placeholder="Search dealers..."
          />
        </div>
      </div>
      <div class="col-lg-3">
        <select v-model="locationFilter" class="form-select">
          <option value="">All Locations</option>
          <option value="local">Local</option>
          <option value="online">Online</option>
          <option value="show">Coin Shows</option>
        </select>
      </div>
      <div class="col-lg-3">
        <select v-model="specialtyFilter" class="form-select">
          <option value="">All Specialties</option>
          <option value="us-coins">US Coins</option>
          <option value="world-coins">World Coins</option>
          <option value="ancient">Ancient Coins</option>
          <option value="bullion">Bullion</option>
        </select>
      </div>
      <div class="col-lg-2">
        <select v-model="ratingFilter" class="form-select">
          <option value="">All Ratings</option>
          <option value="5">5 Stars</option>
          <option value="4">4+ Stars</option>
          <option value="3">3+ Stars</option>
        </select>
      </div>
    </div>

    <!-- Dealers Grid -->
    <div class="row">
      <div v-for="dealer in filteredDealers" :key="dealer.id" class="col-lg-6 col-xl-4 mb-4">
        <div class="card shadow h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <div
                  class="dealer-avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3"
                  style="width: 50px; height: 50px"
                >
                  <i class="fas fa-store"></i>
                </div>
                <div>
                  <h5 class="card-title mb-1">{{ dealer.name }}</h5>
                  <div class="d-flex align-items-center">
                    <div class="text-warning me-2">
                      <i
                        v-for="star in 5"
                        :key="star"
                        class="fas fa-star"
                        :class="star <= dealer.rating ? 'text-warning' : 'text-muted'"
                      ></i>
                    </div>
                    <span class="text-muted small">({{ dealer.reviewCount }} reviews)</span>
                  </div>
                </div>
              </div>
              <span class="badge" :class="getTypeBadgeClass(dealer.type)">
                {{ dealer.type }}
              </span>
            </div>

            <p class="text-muted small mb-3">{{ dealer.description }}</p>

            <div class="mb-3">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted">
                  <i class="fas fa-map-marker-alt me-1"></i>
                  Location:
                </span>
                <span>{{ dealer.location }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center mb-2">
                <span class="text-muted">
                  <i class="fas fa-tags me-1"></i>
                  Specialty:
                </span>
                <span>{{ dealer.specialty }}</span>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <span class="text-muted">
                  <i class="fas fa-phone me-1"></i>
                  Contact:
                </span>
                <span>{{ dealer.phone }}</span>
              </div>
            </div>

            <div class="d-flex gap-2">
              <button class="btn btn-primary btn-sm flex-fill">
                <i class="fas fa-eye me-1"></i>
                View Details
              </button>
              <button class="btn btn-outline-success btn-sm">
                <i class="fas fa-heart"></i>
              </button>
              <button class="btn btn-outline-primary btn-sm">
                <i class="fas fa-phone"></i>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="filteredDealers.length === 0" class="col-12">
        <div class="text-center py-5">
          <i class="fas fa-store fa-4x text-muted mb-4"></i>
          <h3>No Dealers Found</h3>
          <p class="text-muted mb-4">
            {{ searchQuery ? 'No dealers match your search criteria' : 'Add your first trusted dealer' }}
          </p>
          <button class="btn btn-primary btn-lg">
            <i class="fas fa-plus me-2"></i>
            Add First Dealer
          </button>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="filteredDealers.length > 0" aria-label="Dealers pagination" class="mt-4">
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
          <a class="page-link" href="#">Next</a>
        </li>
      </ul>
    </nav>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

// Reactive data
const searchQuery = ref('')
const locationFilter = ref('')
const specialtyFilter = ref('')
const ratingFilter = ref('')

// Mock data - replace with actual API calls
const dealers = ref([
  {
    id: 1,
    name: 'Heritage Auctions',
    description: 'Leading numismatic auction house with worldwide reach',
    location: 'Dallas, TX',
    type: 'Online',
    specialty: 'US Coins',
    phone: '(800) 872-6467',
    rating: 5,
    reviewCount: 1250,
  },
  {
    id: 2,
    name: 'Stack\'s Bowers',
    description: 'Premier rare coin auction company since 1935',
    location: 'New York, NY',
    type: 'Local',
    specialty: 'US Coins',
    phone: '(800) 566-2580',
    rating: 5,
    reviewCount: 980,
  },
  {
    id: 3,
    name: 'APMEX',
    description: 'America\'s largest online precious metals dealer',
    location: 'Oklahoma City, OK',
    type: 'Online',
    specialty: 'Bullion',
    phone: '(800) 375-9006',
    rating: 4,
    reviewCount: 2100,
  },
  {
    id: 4,
    name: 'Local Coin Shop',
    description: 'Friendly neighborhood coin dealer with fair prices',
    location: 'Springfield, IL',
    type: 'Local',
    specialty: 'US Coins',
    phone: '(217) 555-0123',
    rating: 4,
    reviewCount: 85,
  },
  {
    id: 5,
    name: 'Ancient Coin Gallery',
    description: 'Specialists in ancient Greek and Roman coins',
    location: 'Los Angeles, CA',
    type: 'Online',
    specialty: 'Ancient',
    phone: '(310) 555-0789',
    rating: 5,
    reviewCount: 340,
  },
  {
    id: 6,
    name: 'World Coins Direct',
    description: 'International dealer with coins from every continent',
    location: 'London, UK',
    type: 'Coin Shows',
    specialty: 'World Coins',
    phone: '+44 20 7555 0456',
    rating: 4,
    reviewCount: 520,
  },
])

// Computed filtered dealers
const filteredDealers = computed(() => {
  let filtered = dealers.value

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(
      (dealer) =>
        dealer.name.toLowerCase().includes(query) ||
        dealer.description.toLowerCase().includes(query) ||
        dealer.location.toLowerCase().includes(query)
    )
  }

  // Filter by location type
  if (locationFilter.value) {
    filtered = filtered.filter((dealer) => 
      dealer.type.toLowerCase().includes(locationFilter.value.toLowerCase())
    )
  }

  // Filter by specialty
  if (specialtyFilter.value) {
    filtered = filtered.filter((dealer) => 
      dealer.specialty.toLowerCase().includes(specialtyFilter.value.toLowerCase())
    )
  }

  // Filter by rating
  if (ratingFilter.value) {
    const minRating = parseInt(ratingFilter.value)
    filtered = filtered.filter((dealer) => dealer.rating >= minRating)
  }

  return filtered
})

// Helper functions
const getTypeBadgeClass = (type: string) => {
  const typeMap: Record<string, string> = {
    'Local': 'bg-success',
    'Online': 'bg-primary',
    'Coin Shows': 'bg-warning',
  }
  return typeMap[type] || 'bg-secondary'
}
</script>

<style scoped>
.dealer-avatar {
  flex-shrink: 0;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.fas.fa-star {
  font-size: 0.8rem;
}
</style>
