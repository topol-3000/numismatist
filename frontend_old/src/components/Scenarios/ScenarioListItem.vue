<script setup lang="ts">
import type { Scenario } from "@/types/scenarios.ts";

const { scenario } = defineProps<{
  scenario: Scenario;
}>();
</script>

<template>
  <li class="py-3 hover:bg-gray-200 dark:hover:bg-gray-800 duration-300">
    <RouterLink
      :to="{ name: 'Scenario', params: { id: scenario.id } }"
      class="flex justify-between justify-items-center"
    >
      <div class="flex min-w-0 gap-x-4">
        <div class="min-w-0 px-3 flex-auto">
          <p class="font-semibold">
            {{ scenario.name }}
          </p>
          <p class="mt-1 truncate text-sm">
            {{ scenario.note }}
          </p>
        </div>
      </div>
      <div class="flex justify-center items-center pr-2">
        <span>{{ scenario.status }}</span>
      </div>
    </RouterLink>
  </li>
</template>
