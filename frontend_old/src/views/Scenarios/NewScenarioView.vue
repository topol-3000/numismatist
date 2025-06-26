<script setup lang="ts">
import { ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import NewScenarioCard from "@/components/Scenarios/NewScenarioCard.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const pageTitle = ref("Create Scenario");
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <NewScenarioCard />
    </div>
  </DefaultLayout>
</template>
