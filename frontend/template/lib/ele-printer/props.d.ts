import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { PrintDirection, PrintOrientation, PrintTarget } from './types';

/**
 * 属性
 */
export declare const printerProps: {
    /** 是否打印 */
    modelValue: BooleanConstructor;
    /** 页眉样式 */
    headerStyle: PropType<StyleValue>;
    /** 内容样式 */
    bodyStyle: PropType<StyleValue>;
    /** 页脚样式 */
    footerStyle: PropType<StyleValue>;
    /** 标题 */
    title: StringConstructor;
    /** 页间距 */
    margin: (StringConstructor | NumberConstructor)[];
    /** 纸张方向 */
    direction: PropType<PrintDirection | null>;
    /** 纸张旋转 */
    orientation: PropType<PrintOrientation | null>;
    /** 打印位置 */
    target: PropType<PrintTarget | null>;
    /** 是否显示在文档流中 */
    static: BooleanConstructor;
    /** 打印方法参数 */
    options: ObjectConstructor;
};
export type PrinterProps = ExtractPropTypes<typeof printerProps>;
/**
 * 事件
 */
export declare const printerEmits: {
    /** 更新打印状态 */
    'update:modelValue': (_value: boolean) => boolean;
    /** 打印完成的事件 */
    done: () => boolean;
};
