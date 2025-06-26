<script setup lang="ts">
import {
  UserIcon,
  PencilSquareIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/vue/24/outline";
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import SwitchInput from "@/components/Forms/SwitchInput.vue";
import WorkTimePicker from "@/components/Forms/WorkTimePicker.vue";
import { useValidationErrors } from "@/composables/useValidationErrors.ts";
import { getScenarioById, updateScenario } from "@/services/scenarios.ts";
import type { ApiError } from "@/types/api.ts";
import type { Scenario } from "@/types/scenarios.ts";

const route = useRoute();
const router = useRouter();
const scenario_id = Number(route.params.id);

const formData = reactive({
  name: "",
  note: "",
  work_time_pattern: "",
  unit_configs: "",
  is_enabled: true,
  auto_publish: true,
});

const scenario = ref<Scenario | null>(null);
const initialScenario = ref<Scenario | null>(null);

// Incorporate validation error handling:
const { validationErrors, parseValidationErrors } = useValidationErrors();

const fetchScenario = async () => {
  try {
    scenario.value = await getScenarioById(scenario_id);
    initialScenario.value = JSON.parse(JSON.stringify(scenario.value)); // Deep copy for comparison

    formData.name = scenario.value.name;
    formData.note = scenario.value.note;
    formData.work_time_pattern = scenario.value.work_time_pattern;
    formData.is_enabled = scenario.value.is_enabled;
    formData.auto_publish = scenario.value.auto_publish;
    formData.unit_configs = JSON.stringify(
      scenario.value.unit_configs,
      null,
      4,
    );
  } catch (err: unknown) {
    alert(err);
  }
};

// Function to extract only changed fields
const getChangedFields = (): Partial<Scenario> => {
  const updatedFields: Partial<Scenario> = {};
  if (initialScenario.value) {
    // Compare each field and only add changed ones to updatedFields
    if (formData.name !== initialScenario.value.name)
      updatedFields.name = formData.name;
    if (formData.note !== initialScenario.value.note)
      updatedFields.note = formData.note;
    if (formData.work_time_pattern !== initialScenario.value.work_time_pattern)
      updatedFields.work_time_pattern = formData.work_time_pattern;
    if (formData.is_enabled !== initialScenario.value.is_enabled)
      updatedFields.is_enabled = formData.is_enabled;
    if (formData.auto_publish !== initialScenario.value.auto_publish)
      updatedFields.auto_publish = formData.auto_publish;

    const parsedUnitConfigs = JSON.parse(formData.unit_configs);
    if (
      JSON.stringify(parsedUnitConfigs) !==
      JSON.stringify(initialScenario.value.unit_configs)
    )
      updatedFields.unit_configs = parsedUnitConfigs;
  }
  return updatedFields;
};

onMounted(async () => {
  await fetchScenario();
});

const handleSubmit = async () => {
  const changedFields = getChangedFields();

  if (Object.keys(changedFields).length === 0) {
    alert("No changes to update");
    return;
  }

  try {
    await updateScenario(scenario_id, changedFields);
    alert("Scenario updated successfully");
    await router.push({ name: "Scenarios" });
  } catch (error: unknown) {
    const apiError = error as ApiError;

    // Populate validation errors
    if (apiError.validationErrors) {
      parseValidationErrors(apiError.validationErrors);
    }
  }
};

const handleCancel = () => {
  router.push({ name: "Scenarios" });
};
</script>

<template>
  <div class="grid grid-cols-5 gap-8">
    <!-- Scenario updating section -->
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
          <form @submit.prevent="handleSubmit">
            <!-- Display validation error messages -->
            <div
              v-if="Object.keys(validationErrors).length > 0"
              class="my-4 text-red-500"
            >
              <p v-for="(error, field) in validationErrors" :key="field">
                {{ field }}: {{ error }}
              </p>
            </div>
            <!-- Name Section -->
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

            <!-- note Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="note"
                >Note</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <PencilSquareIcon class="size-5" />
                </span>
                <textarea
                  id="note"
                  v-model="formData.note"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="bio"
                  rows="5"
                  placeholder="Write scenario note here..."
                />
              </div>
            </div>

            <!-- Configuration Section -->
            <div class="mb-5.5">
              <label
                class="mb-3 block text-sm font-medium text-black dark:text-white"
                for="scenario_configs"
                >Scenario Configuration</label
              >
              <div class="relative">
                <span class="absolute left-4.5 top-4">
                  <WrenchScrewdriverIcon class="size-5" />
                </span>
                <textarea
                  id="scenario_configs"
                  v-model="formData.unit_configs"
                  class="w-full rounded border border-stroke bg-gray py-3 pl-11.5 pr-4.5 font-normal text-black focus:border-primary focus-visible:outline-none dark:border-strokedark dark:bg-meta-4 dark:text-white dark:focus:border-primary"
                  name="scenario_configs"
                  rows="20"
                  placeholder="Describe scenario configuration options here..."
                />
              </div>
            </div>

            <!-- Save and Cancel Buttons -->
            <div class="flex flex-col sm:flex-row justify-between gap-4.5">
              <div class="flex gap-4.5">
                <SwitchInput v-model="formData.is_enabled" title="Enabled" />
                <SwitchInput
                  v-model="formData.auto_publish"
                  title="Auto publish"
                />
              </div>
              <div class="flex justify-center gap-4.5">
                <button
                  class="flex justify-center rounded bg-danger py-2 px-6 font-medium text-gray hover:bg-opacity-90"
                  type="submit"
                  @click="handleCancel"
                >
                  Cancel
                </button>
                <button
                  class="flex justify-center rounded bg-primary py-2 px-6 font-medium text-gray hover:bg-opacity-90"
                  type="submit"
                >
                  Save
                </button>
              </div>
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
