export interface SystemConfig {
  id: number;
  configKey: string;
  configValue?: string;
  configGroup?: string;
  description?: string;
  valueType: string;
  defaultValue?: string;
}
