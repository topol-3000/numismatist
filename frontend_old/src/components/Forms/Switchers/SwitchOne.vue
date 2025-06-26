<script setup lang="ts">
import { ref } from "vue";

const switcherToggle = ref<boolean>(false);
</script>

<template>
  <div>
    <label for="toggle1" class="flex cursor-pointer select-none items-center">
      <div class="relative">
        <input
          id="toggle1"
          type="checkbox"
          class="sr-only"
          @change="switcherToggle = !switcherToggle"
        />
        <div class="block h-8 w-14 rounded-full bg-meta-9 dark:bg-[#5A616B]" />
        <div
          :class="
            switcherToggle &&
            '!right-1 !translate-x-full !bg-primary dark:!bg-white'
          "
          class="absolute left-1 top-1 h-6 w-6 rounded-full bg-white transition"
        />
      </div>
    </label>
  </div>
</template>
