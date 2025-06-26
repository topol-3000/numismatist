<script setup lang="ts">
import { ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import NewUnitCard from "@/components/Units/NewUnitCard.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const pageTitle = ref("Create Unit");
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <NewUnitCard />
    </div>
  </DefaultLayout>
</template>
