<script setup lang="ts">
import { ref } from "vue";

const model = defineModel<string>();
const error = ref("");
const periods = [
  { id: "day", text: "Day", value: ["hour", "minute"] },
  { id: "week", text: "Week", value: ["dayOfWeek", "hour", "minute"] },
];

if (error.value) {
  console.error("Error WorkTimePicker:", error.value);
}
</script>

<template>
  <CronLight
    v-model="model"
    :periods="periods"
    @error="error = $event"
  ></CronLight>
</template>
