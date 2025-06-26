import { useStorage } from "@vueuse/core";
import { defineStore } from "pinia";
import { computed } from "vue";

import { login, signup } from "@/services/auth";
import { useUserStore } from "@/stores/user.ts";
import type { LoginCredentials, SignUpData } from "@/types/auth";

export const useAuthStore = defineStore("auth", () => {
  const token = useStorage<string | null>("token", null, localStorage, {
    mergeDefaults: true,
  });
  const isAuthenticated = computed(() => !!token.value);

  const userStore = useUserStore();

  const signIn = async (credentials: LoginCredentials) => {
    const { access_token } = await login(credentials);
    token.value = access_token;
    await userStore.getUserInfo();
  };

  const signUp = async (userData: SignUpData) => {
    await signup(userData);
  };

  const signOut = () => {
    token.value = null;
    userStore.clearUser();
  };

  return {
    token,
    isAuthenticated,
    signIn,
    signUp,
    signOut,
  };
});
