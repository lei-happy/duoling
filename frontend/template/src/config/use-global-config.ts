import { ref } from 'vue';
import type { TableGlobalConfig } from 'ele-admin-plus/es/ele-config-provider/types';
import { exceljsExportPlugin } from 'ele-admin-plus/es/ele-pro-table/exceljs-plugin';
import { proTableToolsDefault } from './pro-table-tool-presets';

/**
 * 组件全局配置
 */
export function useGlobalConfig() {
  /** 高级表格全局配置 */
  const tableConfig = ref<TableGlobalConfig>({
    response: {
      dataName: 'list',
      countName: 'count'
    },
    tools: proTableToolsDefault,
    exportConfig: {
      // 使用 exceljs 进行导出
      exportPlugin: exceljsExportPlugin
    }
  });

  return { tableConfig };
}
