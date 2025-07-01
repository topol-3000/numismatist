<template>
  <div class="card shadow-lg border-0" style="max-width: 400px; width: 100%">
    <div class="card-body p-5">
      <div class="text-center mb-4">
        <h2 class="card-title mb-2">Welcome Back</h2>
        <p class="text-muted">Sign in to your account</p>
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
          v-model="form.username"
          label="Email"
          type="email"
          placeholder="Enter your email"
          :required="true"
          :error="errors.username"
          id="username"
          @blur="validateField('username')"
        />

        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          placeholder="Enter your password"
          :required="true"
          :error="errors.password"
          id="password"
          @blur="validateField('password')"
        />

        <div class="d-flex justify-content-between align-items-center mb-4">
          <div class="form-check">
            <input
              v-model="form.rememberMe"
              class="form-check-input"
              type="checkbox"
              id="rememberMe"
            />
            <label class="form-check-label" for="rememberMe"> Remember me </label>
          </div>
          <router-link to="/forgot-password" class="text-decoration-none">
            Forgot password?
          </router-link>
        </div>

        <BaseButton
          type="submit"
          variant="primary"
          :loading="authStore.isLoading"
          :disabled="!isFormValid"
          text="Sign In"
          icon="sign-in-alt"
          block
        />
      </form>

      <hr class="my-4" />

      <div class="text-center">
        <p class="mb-0">
          Don't have an account?
          <router-link to="/register" class="text-decoration-none fw-bold">
            Create one
          </router-link>
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
  username: '',
  password: '',
  rememberMe: false,
})

// Local error handling
const errorMessage = ref('')

// Form validation
const errors = ref({
  username: '',
  password: '',
})

const validateField = (field: keyof typeof form.value) => {
  switch (field) {
    case 'username':
      if (!form.value.username) {
        errors.value.username = 'Email is required'
      } else if (!/\S+@\S+\.\S+/.test(form.value.username)) {
        errors.value.username = 'Please enter a valid email'
      } else {
        errors.value.username = ''
      }
      break
    case 'password':
      if (!form.value.password) {
        errors.value.password = 'Password is required'
      } else if (form.value.password.length < 6) {
        errors.value.password = 'Password must be at least 6 characters'
      } else {
        errors.value.password = ''
      }
      break
  }
}

const validateForm = () => {
  validateField('username')
  validateField('password')
  return !errors.value.username && !errors.value.password
}

const isFormValid = computed(() => {
  return form.value.username && form.value.password && validateForm()
})

const handleSubmit = async () => {
  if (!validateForm()) return

  errorMessage.value = '' // Clear previous errors

  const success = await authStore.login({
    username: form.value.username,
    password: form.value.password,
  })

  if (success) {
    // Redirect to intended page or dashboard
    const redirectTo = (router.currentRoute.value.query.redirect as string) || '/'
    router.push(redirectTo)
  } else {
    errorMessage.value = 'Invalid email or password. Please try again.'
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
