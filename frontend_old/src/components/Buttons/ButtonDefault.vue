<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

const props = defineProps<{
  label: string;
  route: RouteLocationRaw;
  customClasses?: string;
}>();
</script>

<template>
  <router-link
    :to="props.route"
    class="inline-flex items-center justify-center gap-2.5 py-4 px-10 text-center font-medium hover:bg-opacity-90 lg:px-8 xl:px-10"
    :class="props.customClasses"
  >
    <slot />
    {{ props.label }}
  </router-link>
</template>
