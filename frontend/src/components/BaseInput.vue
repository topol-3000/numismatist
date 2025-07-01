<template>
  <div class="mb-3">
    <label v-if="label" :for="id" class="form-label">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <input
      :id="id"
      :type="type"
      :class="inputClasses"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :value="modelValue"
      @input="onInput"
      @blur="onBlur"
    />
    <div v-if="error" class="invalid-feedback">
      {{ error }}
    </div>
    <div v-if="helpText && !error" class="form-text">
      {{ helpText }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  modelValue: string
  type?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
  helpText?: string
  id?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
})

const emit = defineEmits<Emits>()

const touched = ref(false)

const inputClasses = computed(() => {
  const baseClasses = ['form-control']

  if (props.error && touched.value) {
    baseClasses.push('is-invalid')
  }

  if (props.disabled) {
    baseClasses.push('disabled')
  }

  return baseClasses.join(' ')
})

const onInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const onBlur = () => {
  touched.value = true
  emit('blur')
}
</script>
