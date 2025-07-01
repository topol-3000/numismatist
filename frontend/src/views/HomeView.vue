<script setup lang="ts">
// Home page for the Numismatist application
</script>

<template>
  <div class="container-fluid">
    <!-- Hero Section -->
    <div class="row bg-primary text-white py-5">
      <div class="col-12 text-center">
        <div class="container">
          <h1 class="display-4 fw-bold mb-3">
            <i class="fas fa-coins me-3"></i>
            Welcome to Numismatist
          </h1>
          <p class="lead mb-4">Organize, catalog, and manage your coin collections with ease</p>
          <div class="d-flex justify-content-center gap-3">
            <router-link to="/collections" class="btn btn-light btn-lg">
              <i class="fas fa-folder me-2"></i>
              Browse Collections
            </router-link>
            <router-link to="/register" class="btn btn-outline-light btn-lg">
              <i class="fas fa-user-plus me-2"></i>
              Get Started
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="container py-5">
      <div class="row text-center mb-5">
        <div class="col-12">
          <h2 class="display-6 fw-bold mb-3">Features</h2>
          <p class="lead text-muted">Everything you need to manage your numismatic collection</p>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-folder-open fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Organize Collections</h5>
              <p class="card-text">
                Create and manage multiple collections to organize your coins by theme, era, or
                country.
              </p>
            </div>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-coins fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Catalog Items</h5>
              <p class="card-text">
                Add detailed information about each coin including photos, descriptions, and
                valuations.
              </p>
            </div>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-search fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Search & Filter</h5>
              <p class="card-text">
                Quickly find specific coins using powerful search and filtering capabilities.
              </p>
            </div>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-chart-line fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Track Values</h5>
              <p class="card-text">
                Monitor the value of your collection and track changes over time.
              </p>
            </div>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-share-alt fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Share Collections</h5>
              <p class="card-text">
                Share your collections with fellow collectors and the numismatic community.
              </p>
            </div>
          </div>
        </div>

        <div class="col-lg-4 col-md-6">
          <div class="card h-100 shadow-sm">
            <div class="card-body text-center">
              <i class="fas fa-mobile-alt fa-3x text-primary mb-3"></i>
              <h5 class="card-title">Mobile Friendly</h5>
              <p class="card-text">
                Access your collections anywhere with our responsive, mobile-friendly design.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Call to Action -->
    <div class="bg-light py-5">
      <div class="container text-center">
        <h3 class="mb-3">Ready to start organizing your collection?</h3>
        <p class="lead mb-4">
          Join thousands of collectors who trust Numismatist with their precious collections.
        </p>
        <router-link to="/register" class="btn btn-primary btn-lg">
          <i class="fas fa-rocket me-2"></i>
          Start Your Journey
        </router-link>
      </div>
    </div>
  </div>
</template>
