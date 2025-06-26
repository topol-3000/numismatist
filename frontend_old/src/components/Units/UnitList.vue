<script setup lang="ts">
import { PlusIcon } from "@heroicons/vue/24/outline";
import type { RouteLocationRaw } from "vue-router";

import ButtonDefault from "@/components/Buttons/ButtonDefault.vue";
import ListItem from "@/components/Units/UnitListItem.vue";
import type { Unit } from "@/types/units.ts";

const { title, units, unitType } = defineProps<{
  title: string;
  units: Unit[];
  unitType: string;
}>();

const route: RouteLocationRaw = {
  name: "NewUnit",
  query: { unitType },
};
</script>

<template>
  <div class="flex flex-col my-10">
    <div class="flex justify-between">
      <h3 class="text-title-lg font-bold mb-3">
        {{ title }}
      </h3>
      <div class="">
        <ButtonDefault
          :route="route"
          label="New"
          custom-classes="border border-meta-3 hover:bg-meta-3 text-meta-3 hover:text-white rounded-md duration-500"
        >
          <span>
            <PlusIcon class="size-6" />
          </span>
        </ButtonDefault>
      </div>
    </div>

    <ul role="list" class="divide-y divide-gray-400 dark:divide-gray-500 py-3">
      <ListItem v-for="unit in units" :key="unit.id" :unit="unit" />
    </ul>
  </div>
</template>
