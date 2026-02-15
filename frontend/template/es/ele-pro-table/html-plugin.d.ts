import { ExportPlugin, BeforeExportParams } from './types';

/**
 * 生成表格 HTML
 * @param params 参数
 */
export declare function getTableHtml(params: BeforeExportParams): string;
/**
 * 导出为 html 格式的插件
 */
export declare const htmlExportPlugin: ExportPlugin;
