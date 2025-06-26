import type { User } from "@/types/user";

import api from "./api";

export const fetchUserInfo = async (): Promise<User> => {
  const response = await api.get<User>("/users/me");
  return response.data;
};
