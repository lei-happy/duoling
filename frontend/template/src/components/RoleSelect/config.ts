import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
import { listRoles } from '@/api/system/role';

/**
 * 角色id字段名
 */
export const roleIdField = 'roleId';

/**
 * 角色名字段名
 */
export const roleNameField = 'roleName';

/**
 * 角色查询接口
 */
export const listRoleApi = listRoles;

/**
 * 角色表格列
 */
export const roleTableColumns: Columns = [
  {
    prop: 'roleName',
    label: 'labelRoleName',
    minWidth: 120
  },
  {
    prop: 'roleCode',
    label: 'labelRoleCode',
    minWidth: 120
  },
  {
    prop: 'comments',
    label: 'labelComments',
    minWidth: 140
  },
  {
    prop: 'createTime',
    label: 'labelCreateTime',
    width: 180,
    align: 'center'
  }
];
