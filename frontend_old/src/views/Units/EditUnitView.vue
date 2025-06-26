<script setup lang="ts">
import { ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import EditUnitCard from "@/components/Units/EditUnitCard.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";

const pageTitle = ref("Edit Unit");
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <EditUnitCard />
    </div>
  </DefaultLayout>
</template>
