import axios from "axios";

import { useAuthStore } from "@/stores/auth";
import type { ApiError } from "@/types/api.ts";
import { parseApiError } from "@/utils/ApiError.ts";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach token dynamically using the reactive `useAuthStore`
api.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.isAuthenticated) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle token expiration (e.g., redirect to log in)
      const authStore = useAuthStore();
      authStore.signOut();
    }

    // Parse the error into a structured ApiError object
    const parsedError: ApiError = parseApiError(error);

    // Optionally, log errors for debugging or analytics
    console.error("API Error:", parsedError);

    // Reject the parsed error to be handled by the caller
    return Promise.reject(parsedError);
  },
);

export default api;
