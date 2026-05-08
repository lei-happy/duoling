import axios from 'axios';
import type { ApiResult } from '@/api';

export interface ProductVersionItem {
  id: number;
  versionCode: string;
  versionName: string;
  description?: string | null;
  maxUsers?: number | null;
  maxVehicles?: number | null;
  price?: string | null;
  sortOrder?: number;
}

export interface ProductFeatureItem {
  featureCode: string;
  featureName: string;
  module?: string | null;
  description?: string | null;
  sortOrder?: number;
  /** 该功能在哪些 versionCode 中包含（来自 sys_version_feature） */
  includedIn: string[];
}

export interface ProductVersionFeatureMatrix {
  versions: ProductVersionItem[];
  modules: string[];
  features: ProductFeatureItem[];
}

/**
 * 获取产品版本×功能矩阵（公开，无需登录）
 * 用于"查看升级方案"对比页。
 */
export async function getVersionFeaturesMatrix() {
  const res = await axios.get<ApiResult<ProductVersionFeatureMatrix>>(
    '/api/open/product/version-features'
  );
  if (res.data.code === 0) return res.data.data;
  return Promise.reject(new Error(res.data.message));
}
