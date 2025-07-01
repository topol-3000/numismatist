<template>
  <div class="card shadow-lg border-0" style="max-width: 400px; width: 100%">
    <div class="card-body p-5">
      <div class="text-center mb-4">
        <h2 class="card-title mb-2">Create Account</h2>
        <p class="text-muted">Join the numismatist community</p>
      </div>

      <BaseAlert
        v-if="errorMessage"
        :message="errorMessage"
        type="danger"
        :dismissible="true"
        @dismiss="errorMessage = ''"
      />

      <form @submit.prevent="handleSubmit">
        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          placeholder="Enter your email"
          :required="true"
          :error="errors.email"
          id="email"
          @blur="validateField('email')"
        />

        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          placeholder="Create a password"
          :required="true"
          :error="errors.password"
          id="password"
          help-text="Password must be at least 8 characters long"
          @blur="validateField('password')"
        />

        <BaseInput
          v-model="form.confirmPassword"
          label="Confirm Password"
          type="password"
          placeholder="Confirm your password"
          :required="true"
          :error="errors.confirmPassword"
          id="confirmPassword"
          @blur="validateField('confirmPassword')"
        />

        <div class="form-check mb-4">
          <input
            v-model="form.agreeToTerms"
            class="form-check-input"
            type="checkbox"
            id="agreeToTerms"
            :class="{ 'is-invalid': errors.agreeToTerms }"
          />
          <label class="form-check-label" for="agreeToTerms">
            I agree to the
            <a href="#" class="text-decoration-none">Terms of Service</a>
            and
            <a href="#" class="text-decoration-none">Privacy Policy</a>
          </label>
          <div v-if="errors.agreeToTerms" class="invalid-feedback">
            {{ errors.agreeToTerms }}
          </div>
        </div>

        <BaseButton
          type="submit"
          variant="success"
          :loading="authStore.isLoading"
          :disabled="!isFormValid"
          text="Create Account"
          icon="user-plus"
          block
        />
      </form>

      <hr class="my-4" />

      <div class="text-center">
        <p class="mb-0">
          Already have an account?
          <router-link to="/login" class="text-decoration-none fw-bold"> Sign in </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseInput from '@/components/BaseInput.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseAlert from '@/components/BaseAlert.vue'

const router = useRouter()
const authStore = useAuthStore()

// Form data
const form = ref({
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false,
})

// Local error handling
const errorMessage = ref('')

// Form validation
const errors = ref({
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: '',
})

const validateField = (field: keyof typeof form.value) => {
  switch (field) {
    case 'email':
      if (!form.value.email) {
        errors.value.email = 'Email is required'
      } else if (!/\S+@\S+\.\S+/.test(form.value.email)) {
        errors.value.email = 'Please enter a valid email'
      } else {
        errors.value.email = ''
      }
      break
    case 'password':
      if (!form.value.password) {
        errors.value.password = 'Password is required'
      } else if (form.value.password.length < 8) {
        errors.value.password = 'Password must be at least 8 characters'
      } else {
        errors.value.password = ''
      }
      // Re-validate confirm password if it was already entered
      if (form.value.confirmPassword) {
        validateField('confirmPassword')
      }
      break
    case 'confirmPassword':
      if (!form.value.confirmPassword) {
        errors.value.confirmPassword = 'Please confirm your password'
      } else if (form.value.password !== form.value.confirmPassword) {
        errors.value.confirmPassword = 'Passwords do not match'
      } else {
        errors.value.confirmPassword = ''
      }
      break
    case 'agreeToTerms':
      if (!form.value.agreeToTerms) {
        errors.value.agreeToTerms = 'You must agree to the terms and conditions'
      } else {
        errors.value.agreeToTerms = ''
      }
      break
  }
}

const validateForm = () => {
  validateField('email')
  validateField('password')
  validateField('confirmPassword')
  validateField('agreeToTerms')

  return (
    !errors.value.email &&
    !errors.value.password &&
    !errors.value.confirmPassword &&
    !errors.value.agreeToTerms
  )
}

const isFormValid = computed(() => {
  return (
    form.value.email &&
    form.value.password &&
    form.value.confirmPassword &&
    form.value.agreeToTerms &&
    validateForm()
  )
})

const handleSubmit = async () => {
  if (!validateForm()) return

  errorMessage.value = '' // Clear previous errors

  const success = await authStore.register({
    email: form.value.email,
    password: form.value.password,
  })

  if (success) {
    // Redirect to dashboard or welcome page
    router.push('/')
  } else {
    errorMessage.value = 'Registration failed. Please check your information and try again.'
  }
}

// Redirect if already authenticated
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.card {
  border-radius: 1rem;
}
</style>
