<script setup lang="ts">
import { ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import EditScenarioCard from "@/components/Scenarios/EditScenarioCard.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const pageTitle = ref("Edit Scenario");
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <EditScenarioCard />
    </div>
  </DefaultLayout>
</template>
