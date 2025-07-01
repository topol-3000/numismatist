<template>
  <div v-if="visible" :class="alertClasses" role="alert">
    <i v-if="icon" :class="`fas fa-${icon} me-2`"></i>
    <div v-if="title" class="fw-bold">{{ title }}</div>
    <div>{{ message }}</div>
    <button
      v-if="dismissible"
      type="button"
      class="btn-close"
      aria-label="Close"
      @click="dismiss"
    ></button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

interface Props {
  message: string
  type?: 'success' | 'danger' | 'warning' | 'info' | 'primary' | 'secondary'
  title?: string
  dismissible?: boolean
  show?: boolean
  autoDismiss?: number // Auto dismiss after X milliseconds
}

interface Emits {
  (e: 'dismiss'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  dismissible: true,
  show: true,
})

const emit = defineEmits<Emits>()

const visible = ref(props.show)

const alertClasses = computed(() => {
  const classes = ['alert']
  classes.push(`alert-${props.type}`)

  if (props.dismissible) {
    classes.push('alert-dismissible')
  }

  return classes.join(' ')
})

const icon = computed(() => {
  switch (props.type) {
    case 'success':
      return 'check-circle'
    case 'danger':
      return 'exclamation-triangle'
    case 'warning':
      return 'exclamation-triangle'
    case 'info':
      return 'info-circle'
    default:
      return undefined
  }
})

const dismiss = () => {
  visible.value = false
  emit('dismiss')
}

// Auto dismiss functionality
watch(
  () => props.show,
  (newValue) => {
    visible.value = newValue

    if (newValue && props.autoDismiss) {
      setTimeout(() => {
        dismiss()
      }, props.autoDismiss)
    }
  },
  { immediate: true },
)
</script>
