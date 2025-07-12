<template>
  <div class="d-flex" id="wrapper">
    <!-- Sidebar -->
    <DashboardSidebar />

    <!-- Page content wrapper -->
    <div id="page-content-wrapper">
      <!-- Top navigation -->
      <DashboardTopNav />

      <!-- Main content -->
      <main>
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import DashboardSidebar from './DashboardSidebar.vue'
import DashboardTopNav from './DashboardTopNav.vue'
</script>

<style scoped>
#wrapper {
  display: flex;
  min-height: 100vh;
}

#wrapper.toggled #sidebar-wrapper {
  margin-left: 0;
}

#page-content-wrapper {
  min-width: 0;
  width: 100%;
  margin-left: 0;
  transition: all 0.25s ease-out;
}

#wrapper.toggled #page-content-wrapper {
  margin-left: 15rem;
}

/* Responsive adjustments */
@media (min-width: 768px) {
  #page-content-wrapper {
    margin-left: 15rem;
  }

  #wrapper.toggled #sidebar-wrapper {
    margin-left: -15rem;
  }

  #wrapper.toggled #page-content-wrapper {
    margin-left: 0;
  }
}
</style>
