<template>
  <button :type="type" :class="buttonClasses" :disabled="disabled || loading" @click="onClick">
    <span
      v-if="loading"
      class="spinner-border spinner-border-sm me-2"
      role="status"
      aria-hidden="true"
    ></span>
    <i v-if="icon && !loading" :class="`fas fa-${icon} me-2`"></i>
    <slot>{{ text }}</slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'button' | 'submit' | 'reset'
  variant?:
    | 'primary'
    | 'secondary'
    | 'success'
    | 'danger'
    | 'warning'
    | 'info'
    | 'light'
    | 'dark'
    | 'outline-primary'
    | 'outline-secondary'
  size?: 'sm' | 'lg'
  disabled?: boolean
  loading?: boolean
  block?: boolean
  text?: string
  icon?: string
}

interface Emits {
  (e: 'click', event: MouseEvent): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  disabled: false,
  loading: false,
  block: false,
})

const emit = defineEmits<Emits>()

const buttonClasses = computed(() => {
  const classes = ['btn']

  classes.push(`btn-${props.variant}`)

  if (props.size) {
    classes.push(`btn-${props.size}`)
  }

  if (props.block) {
    classes.push('w-100')
  }

  return classes.join(' ')
})

const onClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
