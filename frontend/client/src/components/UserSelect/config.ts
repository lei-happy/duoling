import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
import { listOrganizations } from '@/api/system/organization';
import { pageUsers } from '@/api/system/user';

/**
 * 部门树id字段名
 */
export const deptIdField = 'organizationId';

/**
 * 部门树名称字段名
 */
export const deptNameField = 'organizationName';

/**
 * 部门树id字段名
 */
export const deptParentIdField = 'parentId';

/**
 * 部门树查询接口
 */
export const listDeptApi = listOrganizations;

/**
 * 用户id字段名
 */
export const userIdField = 'userId';

/**
 * 用户名字段名
 */
export const userNameField = 'nickname';

/**
 * 用户头像字段名
 */
export const avatarField = 'avatar';

/**
 * 用户分页查询接口
 */
export const pageUserApi = pageUsers;

/**
 * 用户表格列
 */
export const userTableColumns: Columns = [
  {
    prop: 'username',
    label: 'labelUsername',
    align: 'center',
    minWidth: 100
  },
  {
    prop: 'nickname',
    label: 'labelNickname',
    align: 'center',
    minWidth: 110
  },
  {
    prop: 'organizationName',
    label: 'labelOrganizationName',
    align: 'center',
    minWidth: 100
  },
  {
    prop: 'status',
    label: 'labelStatus',
    width: 80,
    align: 'center',
    slot: 'status'
  },
  {
    prop: 'phone',
    label: 'labelPhone',
    align: 'center',
    minWidth: 110
  }
];
