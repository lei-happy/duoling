import { debounce } from 'lodash-es';
import request from '@/utils/request';
import type { ApiResult } from '@/api';
import type { WorkplaceConfig } from '@/views/dashboard/workplace/quick-action/types';

async function _saveWorkplaceConfig(
  workplaceConfig: WorkplaceConfig | null
): Promise<void> {
  try {
    await request.put<ApiResult<unknown>>('/auth/user-workplace-config', {
      workplaceConfig
    });
  } catch (e) {
    console.error('保存工作台配置失败', e);
  }
}

/** 保存工作台配置（防抖，避免频繁请求） */
export const saveWorkplaceConfig = debounce(_saveWorkplaceConfig, 1500);
