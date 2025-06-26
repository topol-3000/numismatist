interface Field {
  name: string;
  label: string;
  placeholder: string;
  type: "text" | "number" | "boolean" | "date";
  default?: string;
  extra?: Record<string, string | number | boolean>;
}

interface ConfigTemplate {
  private_fields: Field[];
  public_fields: Field[];
}

export interface Unit {
  id?: number;
  internal_id: number;
  name: string;
  description: string;
  type: string;
  config_template?: ConfigTemplate | null;
  is_enabled: boolean;
}
