import { toTree } from 'ele-admin-plus';
import { listOrganizations } from '@/api/system/organization';

/**
 * 部门id字段名
 */
export const departmentIdField = 'organizationId';

/**
 * 部门名字段名
 */
export const departmentNameField = 'organizationName';

/**
 * 部门查询接口
 */
export const listDepartmentApi = async () => {
  const data = await listOrganizations();
  return toTree({
    data,
    idField: departmentIdField,
    parentIdField: 'parentId'
  });
};
