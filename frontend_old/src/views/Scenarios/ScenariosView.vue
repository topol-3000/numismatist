<script setup lang="ts">
import { onMounted, ref } from "vue";

import BreadcrumbDefault from "@/components/Breadcrumbs/BreadcrumbDefault.vue";
import ScenarioList from "@/components/Scenarios/ScenarioList.vue";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import { getScenarios } from "@/services/scenarios.ts";
import type { Scenario } from "@/types/scenarios.ts";

const pageTitle = ref("Scenarios");

const scenarios = ref<Scenario[]>([]);

const fetchScenarios = async () => {
  try {
    scenarios.value = await getScenarios();
  } catch (error) {
    console.error("Error fetching scenarios:", error);
  }
};

onMounted(async () => {
  await fetchScenarios();
});
</script>

<template>
  <DefaultLayout>
    <div class="mx-auto max-w-270">
      <!-- Breadcrumb Start -->
      <BreadcrumbDefault :page-title="pageTitle" />
      <!-- Breadcrumb End -->
      <!--      <ScenarioList-->
      <!--        v-for="unitType in unitTypes"-->
      <!--        :key="unitType.value"-->
      <!--        :title="unitType.plural_text"-->
      <!--        :units="units.filter((unit) => unit.type === unitType.value)"-->
      <!--        :unit_type="unitType.value"-->
      <!--      />-->
      <ScenarioList :scenarios="scenarios" />
    </div>
  </DefaultLayout>
</template>
