import type { SelectValue } from 'ele-admin-plus/es/ele-basic-select/types';
export type { Organization } from '@/api/system/organization/model';
export type { User, UserParam } from '@/api/system/user/model';

/**
 * 确认事件钩子
 */
export type BeforeConfirm = (value: SelectValue) => boolean | undefined;

/**
 * 组件文案
 */
export interface UserSelectLocale {
  title: string;
  searchPlaceholder: string;
  clear: string;
  selected: string;
  selectedUnit: string;
  labelUsername: string;
  labelNickname: string;
  labelPhone: string;
  labelOrganizationName: string;
  labelStatus: string;
  statusNormal: string;
  statusDisabled: string;
}
