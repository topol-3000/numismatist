<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

import ButtonDefault from "@/components/Buttons/ButtonDefault.vue";
import ScenarioListItem from "@/components/Scenarios/ScenarioListItem.vue";
import type { Scenario } from "@/types/scenarios.ts";

const { scenarios } = defineProps<{
  scenarios: Scenario[];
}>();

const route: RouteLocationRaw = {
  name: "NewScenario",
};
</script>

<template>
  <div class="flex flex-col my-10">
    <div class="flex justify-between">
      <h3 class="text-title-lg font-bold mb-3">Scenarios</h3>
      <div class="">
        <ButtonDefault
          :route="route"
          label="New"
          custom-classes="border border-meta-3 hover:bg-meta-3 text-meta-3 hover:text-white rounded-md duration-500"
        >
          <span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="size-6"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M12 4.5v15m7.5-7.5h-15"
              />
            </svg>
          </span>
        </ButtonDefault>
      </div>
    </div>

    <ul role="list" class="divide-y divide-gray-400 dark:divide-gray-500 py-3">
      <ScenarioListItem
        v-for="scenario in scenarios"
        :key="scenario.id"
        :scenario="scenario"
      />
    </ul>
  </div>
</template>
