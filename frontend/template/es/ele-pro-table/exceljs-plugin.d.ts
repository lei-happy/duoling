import { default as ExcelJS } from 'exceljs';
import { ExportPlugin, BeforeExportParams } from './types';

/**
 * 导出生成 ExcelJS Workbook
 * @param params 参数
 */
export declare function getExportWorkbook(params: BeforeExportParams): ExcelJS.Workbook;
/**
 * 使用 ExcelJS 进行导出的插件
 */
export declare const exceljsExportPlugin: ExportPlugin;
