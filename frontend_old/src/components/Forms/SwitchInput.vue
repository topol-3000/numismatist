<script setup lang="ts">
const model = defineModel<boolean>();
const { title } = defineProps<{ title: string }>();

// Generate a unique label using a random string
const label = `toggle-${Math.random().toString(36).slice(2, 11)}`;
</script>

<template>
  <div>
    <label :for="label" class="flex cursor-pointer select-none items-center">
      <div class="mr-3">{{ title }}</div>
      <div class="relative">
        <input :id="label" v-model="model" type="checkbox" class="sr-only" />
        <div
          :class="model && '!bg-primary'"
          class="block h-8 w-14 rounded-full bg-black"
        />
        <div
          :class="model && '!right-1 !translate-x-full'"
          class="absolute left-1 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-white transition"
        />
      </div>
    </label>
  </div>
</template>
