import { PrintOption, PrintTarget, PrintPdfOption } from './types';

export declare const printContainerId = "ele-printer-container";
export declare const printFrameId = "ele-printer-iframe";
export declare const printingClass = "ele-printing";
/**
 * 合并打印方法参数
 * @param options 参数
 * @param userOptions 自定义参数
 */
export declare function mergeOptions(options?: any, userOptions?: any): any;
/**
 * 创建并获取打印容器
 */
export declare function getPrintContainer(): Element;
/**
 * usePrinter
 * @param done 打印结束回调
 */
export declare function usePrinter(done: () => void): (option: PrintOption, target?: PrintTarget | null) => void;
/**
 * 打印 pdf
 * @param option 打印参数
 */
export declare function printPdf(option: PrintPdfOption): void;
