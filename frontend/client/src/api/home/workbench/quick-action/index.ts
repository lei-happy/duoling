import { debounce } from 'lodash-es';
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import { resolveUploadUrl } from '@/utils/upload-url';
import type {
  QuickActionConfig,
  WorkplaceConfig
} from '@/views/dashboard/workplace/quick-action/types';

/** 立即保存工作台配置（抛错供调用方提示用户） */
export async function saveWorkplaceConfigNow(
  workplaceConfig: WorkplaceConfig | null
): Promise<void> {
  const res = await request.put<ApiResult<unknown>>(
    '/auth/user-workplace-config',
    { workplaceConfig }
  );
  if (res.data.code !== 0) {
    return Promise.reject(new Error(res.data.message || '保存失败'));
  }
}

async function _saveWorkplaceConfig(
  workplaceConfig: WorkplaceConfig | null
): Promise<void> {
  try {
    await saveWorkplaceConfigNow(workplaceConfig);
  } catch (e) {
    console.error('保存工作台配置失败', e);
  }
}

/** 保存工作台配置（防抖，避免频繁请求） */
export const saveWorkplaceConfig = debounce(_saveWorkplaceConfig, 1500);

/** 后端下发的快捷操作目录项（运营在 Console 客户端菜单里配置） */
interface QuickActionRegistryDto {
  key: string;
  title: string;
  image?: string | null;
  color?: string | null;
  group?: string | null;
  type?: string | null;
  path?: string | null;
  query?: Record<string, string> | null;
  permission?: string | null;
  feature?: string | null;
  defaultVisible?: boolean;
  sortOrder?: number;
}

function toConfig(dto: QuickActionRegistryDto): QuickActionConfig {
  return {
    key: dto.key,
    title: dto.title,
    image: dto.image ? resolveUploadUrl(dto.image) : undefined,
    color: dto.color || undefined,
    group: dto.group || '常用功能',
    type: dto.type === 'external' ? 'external' : 'route',
    path: dto.path || '',
    query: dto.query || undefined,
    permission: dto.permission || undefined,
    feature: dto.feature || undefined,
    defaultVisible: !!dto.defaultVisible,
    sortOrder: dto.sortOrder ?? 0
  };
}

/** 获取快捷操作目录（服务端配置驱动） */
export async function getQuickActionRegistry(): Promise<QuickActionConfig[]> {
  const res = await request.get<ApiResult<QuickActionRegistryDto[]>>(
    '/workbench/quick-action'
  );
  if (res.data.code === 0 && Array.isArray(res.data.data)) {
    return res.data.data.map(toConfig);
  }
  return Promise.reject(new Error(res.data.message));
}
