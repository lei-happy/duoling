import type { TableTool } from 'ele-admin-plus/es/ele-pro-table/types';

/** 全局默认（不含导出、打印），与 use-global-config 中 tableConfig.tools 一致 */
export const proTableToolsDefault: TableTool[] = [
  'reload',
  'size',
  'columns',
  'maximized'
];

/** 页面需要导出时显式绑定 :tools="proTableToolsWithExport" */
export const proTableToolsWithExport: TableTool[] = [
  'reload',
  'export',
  'size',
  'columns',
  'maximized'
];

/** 页面需要导出 + 打印时显式绑定 :tools="proTableToolsWithExportPrint" */
export const proTableToolsWithExportPrint: TableTool[] = [
  'reload',
  'export',
  'print',
  'size',
  'columns',
  'maximized'
];
