<script setup lang="ts">
import { ref } from "vue";

import { useSidebarStore } from "@/stores/sidebar";

const sidebarStore = useSidebarStore();

const props = defineProps<{
  items: { label: string; route: string }[];
  page: string;
}>();
const items = ref(props.items);

function handleItemClick(index: number) {
  const clickedLabel = props.items[index].label;

  if (sidebarStore.selected === clickedLabel) {
    sidebarStore.selected = "";
    return;
  }

  sidebarStore.selected = clickedLabel;
}
</script>

<template>
  <ul class="mt-4 mb-5.5 flex flex-col gap-2.5 pl-6">
    <template v-for="(childItem, index) in items" :key="index">
      <li>
        <router-link
          :to="childItem.route"
          class="group relative flex items-center gap-2.5 rounded-md px-4 font-medium text-bodydark2 duration-300 ease-in-out hover:text-white"
          :class="{
            '!text-white': childItem.label === sidebarStore.selected,
          }"
          @click="handleItemClick(index)"
        >
          {{ childItem.label }}
        </router-link>
      </li>
    </template>
  </ul>
</template>
