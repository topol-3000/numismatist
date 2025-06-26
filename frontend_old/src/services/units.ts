import type { ApiError } from "@/types/api.ts";
import type { Unit } from "@/types/units";

import api from "./api";

export const getUnitById = async (id: number): Promise<Unit> => {
  const response = await api.get<Unit>(`/units/${id}`);
  return response.data;
};

export const getAllUnits = async (): Promise<Unit[]> => {
  const response = await api.get<Unit[]>("/units/");
  return response.data;
};

export async function createUnit(unit: Unit): Promise<Unit> {
  try {
    const response = await api.post<Unit>("/units", unit);
    return response.data;
  } catch (error: unknown) {
    const apiError = error as ApiError; // Type-cast the parsed error
    if (apiError.validationErrors) {
      console.error("Validation Errors:", apiError.validationErrors);
    }
    // Rethrow to be caught by the form or caller
    throw apiError;
  }
}

export async function updateUnit(
  id: number,
  unit: Partial<Unit>,
): Promise<Unit> {
  try {
    const response = await api.patch<Unit>(`/units/${id}`, unit);
    return response.data;
  } catch (error: unknown) {
    const apiError = error as ApiError; // Parse the error using ApiError type
    if (apiError.validationErrors) {
      console.error("Validation Errors:", apiError.validationErrors);
    }
    // Rethrow to be handled at the component level
    throw apiError;
  }
}
