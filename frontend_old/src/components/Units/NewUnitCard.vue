<script setup lang="ts">
import {
  UserIcon,
  LinkIcon,
  PencilSquareIcon,
  ChevronUpDownIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/vue/24/outline";
import { reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import SelectGroup from "@/components/Forms/SelectGroup/SelectGroup.vue";
import SwitchInput from "@/components/Forms/SwitchInput.vue";
import { useValidationErrors } from "@/composables/useValidationErrors.ts";
import { createUnit } from "@/services/units.ts";
import type { ApiError } from "@/types/api.ts";
import { unitTypes } from "@/utils/constants.ts";

const router = useRouter();
const route = useRoute();
const unitType = route.query.unitType;

const formData = reactive({
  internal_id: 0,
  name: "",
  type: unitType ? String(unitType) : "",
  description: "",
  config_template: JSON.stringify(
    { private_fields: [], public_fields: [] },
    null,
    4,
  ),
  is_enabled: true,
});

const { validationErrors, parseValidationErrors } = useValidationErrors();

const handleSubmit = async () => {
  const newUnit = {
    internal_id: formData.internal_id,
    name: formData.name,
    type: formData.type,
    description: formData.description,
    is_enabled: formData.is_enabled,
    config_template: JSON.parse(formData.config_template),
  };

  try {
    // Call API to create a scenario
    await createUnit(newUnit);
    alert("Scenario created successfully");
    await router.push({ name: "Units" });
  } catch (error: unknown) {
    const apiError = error as ApiError;
    // If API returns validation errors, populate state
    if (apiError.validationErrors) {
      parseValidationErrors(apiError.validationErrors);
    }
  }
};
</script>

<template>
  <div class="grid grid-cols-5 gap-8">
    <!-- Unit creation Section -->
    <div class="col-span-5 xl:col-span-3">
      <div
        class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark"
      >
        <div class="border-b border-stroke py-4 px-7 dark:border-strokedark">
          <h3 class="font-medium text-black dark:text-white">
            Unit Information
          </h3>
        </div>
        <div class="p-7">
          <form @submit.prevent="handleSubmit">
            <div
              v-if="Object.keys(validationErrors).length > 0"
              class="my-4 text-red-500"
            >
              <p v-for="(error, field) in validationErrors" :key="field">
                {{ field }}: {{ error }}
              </p>
            </div>
            <!-- Name and Type Section -->
            <div class="mb-5.5 flex flex-col gap-5.5 sm:flex-row">
              <div class="w-full sm:w-1/2">
                <label
                  class="mb-3 block text-sm font-medium text-black dark:text-white"
                  for="name"
                  >Name</label
                >
                <div class="relative">
                  <span class="absolute left-4.5 top-4">
                    <UserIcon class="size-5" />
                  </span>
                  <input
                    id="name"
                    v-model="formData.name"
                    class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                    type="text"
                    name="name"
                    placeholder="Write unit name"
                  />
                </div>
              </div>
              <SelectGroup
                v-model="formData.type"
                label="Type"
                :options="[...unitTypes]"
              >
                <template #left-icon>
                  <ChevronUpDownIcon class="size-5" />
                </template>
              </SelectGroup>
            </div>

            <!-- Internal ID Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="internal_id"
                >Internal ID</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <LinkIcon class="size-5" />
                </span>
                <input
                  id="internal_id"
                  v-model="formData.internal_id"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-13 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  type="number"
                  name="internal_id"
                  placeholder="ID to match the unit"
                />
              </div>
            </div>

            <!-- Description Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="bio"
                >Description</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <PencilSquareIcon class="size-5" />
                </span>
                <textarea
                  id="bio"
                  v-model="formData.description"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="bio"
                  rows="6"
                  placeholder="Write unit description here..."
                />
              </div>
            </div>

            <!-- Configuration Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="bio"
                >Configuration</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <WrenchScrewdriverIcon class="size-5" />
                </span>
                <textarea
                  id="config_template"
                  v-model="formData.config_template"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="config_template"
                  rows="6"
                  placeholder="Describe unit configuration options here..."
                />
              </div>
            </div>

            <!-- Save and Cancel Buttons -->
            <div class="flex justify-between gap-4.5">
              <SwitchInput v-model="formData.is_enabled" title="Enabled" />
              <button
                class="flex justify-center rounded bg-primary py-2 px-6 font-medium text-gray hover:bg-opacity-90"
                type="submit"
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}
</style>
