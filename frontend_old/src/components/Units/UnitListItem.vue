<script setup lang="ts">
import type { Unit } from "@/types/units";

const { unit } = defineProps<{
  unit: Unit;
}>();
</script>

<template>
  <li class="py-3 hover:bg-gray-200 dark:hover:bg-gray-800 duration-300">
    <RouterLink
      :to="{ name: 'Unit', params: { id: unit.id } }"
      class="flex justify-between justify-items-center"
    >
      <div class="flex min-w-0 gap-x-4">
        <div class="min-w-0 px-3 flex-auto">
          <p class="font-semibold">
            {{ unit.name }}
          </p>
          <p class="mt-1 truncate text-sm">
            {{ unit.description }}
          </p>
        </div>
      </div>
      <div class="flex justify-center items-center pr-2">
        <div
          class="flex-none rounded-full p-1"
          :class="unit.is_enabled ? 'bg-emerald-500/20' : 'bg-rose-500/20'"
        >
          <div
            class="size-4 rounded-full"
            :class="unit.is_enabled ? 'bg-emerald-500' : 'bg-rose-500'"
          />
        </div>
      </div>
    </RouterLink>
  </li>
</template>
