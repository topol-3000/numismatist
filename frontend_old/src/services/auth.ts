import type { LoginCredentials, SignUpData, LoginResponse } from "@/types/auth";

import api from "./api";

export const login = async (
  credentials: LoginCredentials,
): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>("/signin", credentials);
  return response.data;
};

export const signup = async (userData: SignUpData): Promise<void> => {
  await api.post("/signup", userData);
};
