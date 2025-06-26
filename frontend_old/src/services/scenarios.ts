import api from "@/services/api.ts";
import type { ApiError } from "@/types/api.ts";
import type { NewScenario, Scenario } from "@/types/scenarios.ts";

// Get all scenarios
export async function getScenarios(): Promise<Scenario[]> {
  const response = await api.get<Scenario[]>("/scenarios");
  return response.data;
}

// Get a single scenario by ID
export async function getScenarioById(id: number): Promise<Scenario> {
  const response = await api.get<Scenario>(`/scenarios/${id}`);
  return response.data;
}

// Create a new scenario
export async function createScenario(scenario: NewScenario): Promise<Scenario> {
  try {
    const response = await api.post<Scenario>("/scenarios", scenario);
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

// Update an existing scenario
export async function updateScenario(
  id: number,
  scenario: Partial<Scenario>,
): Promise<Scenario> {
  try {
    const response = await api.patch<Scenario>(`/scenarios/${id}`, scenario);
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

// Delete a scenario
export async function deleteScenario(id: number): Promise<void> {
  await api.delete(`/scenarios/${id}`);
}
