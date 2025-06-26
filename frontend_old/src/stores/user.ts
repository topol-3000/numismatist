import { useStorage } from "@vueuse/core";
import { defineStore } from "pinia";

import { fetchUserInfo } from "@/services/user";
import type { User } from "@/types/user";

export const useUserStore = defineStore("user", () => {
  const user = useStorage<User>(
    "user_data",
    {
      id: 0,
      first_name: "undefined",
      last_name: "undefined",
      email: "undefined@undefined.undefined",
      is_active: false,
      account_id: 0,
    },
    localStorage,
    {
      serializer: {
        read: (v: string) => JSON.parse(v),
        write: (v: User) => JSON.stringify(v),
      },
    },
  );

  const getUserInfo = async () => {
    user.value = await fetchUserInfo();
  };

  const clearUser = () => {
    user.value = null;
  };

  return {
    user,
    getUserInfo,
    clearUser,
  };
});
