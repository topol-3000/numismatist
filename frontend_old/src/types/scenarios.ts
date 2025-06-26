export interface ConfigField {
  [key: string]: never;
}

export interface UnitConfig {
  unit_id: number;
  config_fields: ConfigField;
}

export interface UnitConfigs {
  extractors: UnitConfig[];
  processors: UnitConfig[];
  publishers: UnitConfig[];
}

export interface Scenario {
  id: number;
  name: string;
  note: string;
  work_time_pattern: string;
  unit_configs: UnitConfigs;
  status: "in_process" | "completed" | "pending";
  is_enabled: boolean;
  auto_publish: boolean;
}

export interface NewScenario {
  name: string;
  note?: string;
  work_time_pattern?: string;
  unit_configs: UnitConfigs;
  is_enabled?: boolean;
  auto_publish?: boolean;
}
