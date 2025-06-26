<script setup lang="ts">
import {
  UserIcon,
  LinkIcon,
  PencilSquareIcon,
  WrenchScrewdriverIcon,
} from "@heroicons/vue/24/outline";
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import SwitchInput from "@/components/Forms/SwitchInput.vue";
import { useValidationErrors } from "@/composables/useValidationErrors.ts";
import { getUnitById, updateUnit } from "@/services/units.ts";
import type { ApiError } from "@/types/api.ts";
import type { Unit } from "@/types/units.ts";

const route = useRoute();
const router = useRouter();
const unit_id = Number(route.params.id);

const formData = reactive({
  id: unit_id,
  internal_id: 0,
  name: "",
  type: "",
  description: "",
  config_template: "",
  is_enabled: true,
});

const unit = ref<Unit | null>(null);
const initialUnit = ref<Unit | null>(null);

// Incorporate validation error handling:
const { validationErrors, parseValidationErrors } = useValidationErrors();

const fetchUnit = async () => {
  try {
    unit.value = await getUnitById(unit_id);
    initialUnit.value = JSON.parse(JSON.stringify(unit.value)); // Deep copy for comparison

    formData.internal_id = unit.value.internal_id;
    formData.name = unit.value.name;
    formData.description = unit.value.description;
    formData.is_enabled = unit.value.is_enabled;
    formData.config_template = JSON.stringify(
      unit.value.config_template,
      null,
      4,
    );
  } catch (err) {
    alert(err);
  }
};

// Function to extract only changed fields
const getChangedFields = (): Partial<Unit> => {
  const updatedFields: Partial<Unit> = {};
  if (initialUnit.value) {
    // Compare each field and only add changed ones to updatedFields
    if (formData.internal_id !== initialUnit.value.internal_id)
      updatedFields.internal_id = formData.internal_id;
    if (formData.name !== initialUnit.value.name)
      updatedFields.name = formData.name;
    if (formData.description !== initialUnit.value.description)
      updatedFields.description = formData.description;
    if (formData.is_enabled !== initialUnit.value.is_enabled)
      updatedFields.is_enabled = formData.is_enabled;

    const parsedUnitConfigs = JSON.parse(formData.config_template);
    if (
      JSON.stringify(parsedUnitConfigs) !==
      JSON.stringify(initialUnit.value.config_template)
    )
      updatedFields.config_template = parsedUnitConfigs;
  }
  return updatedFields;
};

onMounted(async () => {
  await fetchUnit();
});

const handleSubmit = async () => {
  const changedFields = getChangedFields();
  if (Object.keys(changedFields).length === 0) {
    alert("No changes to update");
    return;
  }

  try {
    await updateUnit(unit_id, changedFields);
    alert("Unit updated successfully");
    await router.push({ name: "Units" });
  } catch (error: unknown) {
    const apiError = error as ApiError;

    // Populate validation errors
    if (apiError.validationErrors) {
      parseValidationErrors(apiError.validationErrors);
    }
  }
};

const handleCancel = () => {
  router.push({ name: "Units" });
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
              <div class="w-full sm:w-1/2">
                <label
                  class="mb-3 block text-sm font-medium text-black dark:text-white"
                  for="name"
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
              <div class="flex justify-between">
                <button
                  class="flex justify-center rounded bg-danger py-2 px-6 font-medium text-gray hover:bg-opacity-90"
                  type="submit"
                  @click="handleCancel"
                >
                  Cancel
                </button>
                <button
                  class="flex justify-center rounded bg-primary ml-5 py-2 px-6 font-medium text-gray hover:bg-opacity-90"
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
