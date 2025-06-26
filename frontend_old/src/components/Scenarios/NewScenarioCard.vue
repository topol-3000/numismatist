<script setup lang="ts">
import {
  UserIcon,
  PencilSquareIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/vue/24/outline";
import { reactive } from "vue";
import { useRouter } from "vue-router";

import SwitchInput from "@/components/Forms/SwitchInput.vue";
import WorkTimePicker from "@/components/Forms/WorkTimePicker.vue";
import { useValidationErrors } from "@/composables/useValidationErrors";
import { createScenario } from "@/services/scenarios";
import type { ApiError } from "@/types/api.ts";
import type { UnitConfigs } from "@/types/scenarios.ts";

const router = useRouter();

const UnitConfigsTemplate: UnitConfigs = {
  extractors: [
    {
      unit_id: 1,
      config_fields: {},
    },
  ],
  processors: [
    {
      unit_id: 1,
      config_fields: {},
    },
  ],
  publishers: [
    {
      unit_id: 1,
      config_fields: {},
    },
  ],
};

const formData = reactive({
  name: "",
  work_time_pattern: "",
  note: "",
  unit_configs: JSON.stringify(UnitConfigsTemplate, null, 4),
  is_enabled: true,
  auto_publish: false,
});

const { validationErrors, parseValidationErrors } = useValidationErrors();

const submitForm = async () => {
  const newScenario: any = {
    name: formData.name,
    unit_configs: JSON.parse(formData.unit_configs),
    is_enabled: formData.is_enabled,
    auto_publish: formData.auto_publish,
  };

  if (formData.note !== "") {
    newScenario.note = formData.note;
  }

  if (formData.work_time_pattern !== "") {
    newScenario.work_time_pattern = formData.work_time_pattern;
  }

  if (formData.unit_configs !== "") {
    newScenario.unit_configs = JSON.parse(formData.unit_configs);
  }

  try {
    // Call API to create a scenario
    await createScenario(newScenario);
    alert("Scenario created successfully");
    await router.push({ name: "Scenarios" });
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
    <!-- Scenario creation Section -->
    <div class="col-span-5 xl:col-span-3">
      <div
        class="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark"
      >
        <div class="border-b border-stroke py-4 px-7 dark:border-strokedark">
          <h3 class="font-medium text-black dark:text-white">
            Scenario Information
          </h3>
        </div>
        <div class="p-7">
          <form @submit.prevent="submitForm">
            <div
              v-if="Object.keys(validationErrors).length > 0"
              class="my-4 text-red-500"
            >
              <p v-for="(error, field) in validationErrors" :key="field">
                {{ field }}: {{ error }}
              </p>
            </div>
            <!-- Name and Type Section -->
            <div class="mb-5.5 w-full lg:w-1/2">
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
                  placeholder="Write scenario name"
                />
              </div>
            </div>

            <!-- Work time pattern Section -->
            <div class="mb-5.5 w-full">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                >Work time pattern</label
              >
              <div class="relative">
                <div class="pt-2">
                  <WorkTimePicker
                    v-model="formData.work_time_pattern"
                  ></WorkTimePicker>
                </div>
              </div>
            </div>

            <!-- Description Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="note"
                >Note</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <WrenchScrewdriverIcon class="size-5" />
                </span>
                <textarea
                  id="note"
                  v-model="formData.note"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="bio"
                  rows="5"
                  placeholder="Write scenario description here..."
                />
              </div>
            </div>

            <!-- Configuration Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="unit_configs"
                >Unit Configuration</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <PencilSquareIcon class="size-5" />
                </span>
                <textarea
                  id="unit_configs"
                  v-model="formData.unit_configs"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="unit_configs"
                  rows="20"
                  placeholder="Describe unit configuration options here..."
                />
              </div>
            </div>

            <!-- Save and Cancel Buttons -->
            <div class="flex justify-between gap-4.5">
              <div class="flex gap-4.5">
                <SwitchInput v-model="formData.is_enabled" title="Enabled" />
                <SwitchInput
                  v-model="formData.auto_publish"
                  title="Auto publish"
                />
              </div>
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
