<script setup lang="ts">
import { useRoute } from "vue-router";

import { useSidebarStore } from "@/stores/sidebar";

import SidebarDropdown from "./SidebarDropdown.vue";

const sidebarStore = useSidebarStore();

interface SidebarItem {
  label: string;
  route: string;
  icon?: any;
  children?: SidebarItem[];
}

const props = defineProps<{
  item: SidebarItem;
  index: number;
}>();

const currentPage = useRoute().name;

function handleItemClick() {
  const currentPage = sidebarStore.page;
  const itemLabel = props.item.label;

  // Update the page name in the sidebar store
  sidebarStore.page = currentPage === itemLabel ? "" : itemLabel;

  // Check if any child of the clicked item is currently selected
  if (props.item.children) {
    return isChildSelected(props.item.children);
  }
}

function isChildSelected(children: SidebarItem[]): boolean {
  return children.some((child) => sidebarStore.selected === child.label);
}
</script>

<template>
  <li>
    <router-link
      :to="item.route"
      class="group relative flex items-center gap-2.5 rounded-sm py-2 px-4 font-medium text-bodydark1 duration-300 ease-in-out hover:bg-graydark dark:hover:bg-meta-4"
      :class="{
        'bg-graydark dark:bg-meta-4': sidebarStore.page === item.label,
      }"
      @click.prevent="handleItemClick"
    >
      <component v-if="item.icon" :is="item.icon" class="size-5" />

      {{ item.label }}

      <svg
        v-if="item.children"
        class="absolute right-4 top-1/2 -translate-y-1/2 fill-current"
        :class="{ 'rotate-180': sidebarStore.page === item.label }"
        width="20"
        height="20"
        viewBox="0 0 20 20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M4.41107 6.9107C4.73651 6.58527 5.26414 6.58527 5.58958 6.9107L10.0003 11.3214L14.4111 6.91071C14.7365 6.58527 15.2641 6.58527 15.5896 6.91071C15.915 7.23614 15.915 7.76378 15.5896 8.08922L10.5896 13.0892C10.2641 13.4147 9.73651 13.4147 9.41107 13.0892L4.41107 8.08922C4.08563 7.76378 4.08563 7.23614 4.41107 6.9107Z"
          fill=""
        />
      </svg>
    </router-link>

    <!-- Dropdown Menu Start -->
    <div
      v-show="sidebarStore.page === item.label"
      class="translate transform overflow-hidden"
    >
      <SidebarDropdown
        v-if="item.children"
        :items="item.children"
        :current-page="currentPage"
        :page="item.label"
      />
      <!-- Dropdown Menu End -->
    </div>
  </li>
</template>
