/** 产品模块字典编码，通过数据字典管理 */
export const DICT_CODE_PRODUCT_MODULE = 'product_module';

export interface ProductVersion {
  id?: number;
  versionCode?: string;
  versionName?: string;
  description?: string;
  features?: any;
  maxUsers?: number;
  maxVehicles?: number;
  price?: string;
  sortOrder?: number;
  status?: number;
  createdAt?: string;
}

export interface ProductFeature {
  id?: number;
  featureCode?: string;
  featureName?: string;
  module?: string;
  description?: string;
  requiredTables?: string[];
  sortOrder?: number;
  status?: number;
  createdAt?: string;
}

export interface VersionFeature {
  id?: number;
  versionId?: number;
  featureId?: number;
  status?: number;
  featureCode?: string;
  featureName?: string;
  module?: string;
  requiredTables?: string[];
}
