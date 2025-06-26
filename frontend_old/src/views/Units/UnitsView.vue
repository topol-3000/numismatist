<script setup lang="ts">
import { onMounted, ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import UnitList from "@/components/Units/UnitList.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import { getAllUnits } from "@/services/units";
import type { Unit } from "@/types/units.ts";
import { unitTypes } from "@/utils/constants.ts";

const pageTitle = ref("Units");

const units = ref<Unit[]>([]);

const fetchUnits = async () => {
  try {
    units.value = await getAllUnits();
  } catch (error) {
    console.error("Error fetching units:", error);
  }
};

onMounted(async () => {
  await fetchUnits();
});
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <UnitList
        v-for="unitType in unitTypes"
        :key="unitType.value"
        :title="unitType.plural_text"
        :units="units.filter((unit) => unit.type === unitType.value)"
        :unit-type="unitType.value"
      />
    </div>
  </DefaultLayout>
</template>
