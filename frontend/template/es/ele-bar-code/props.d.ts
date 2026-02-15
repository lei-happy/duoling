import { PropType, ExtractPropTypes } from 'vue';
import { Options } from 'jsbarcode';
import { BarCodeTag } from './types';

/**
 * 属性
 */
export declare const barCodeProps: {
    /** 条码内容 */
    value: StringConstructor;
    /** 渲染方式 */
    tag: {
        type: PropType<BarCodeTag>;
        default: string;
    };
    /** 参数 */
    options: PropType<Options>;
};
export type BarCodeProps = ExtractPropTypes<typeof barCodeProps>;
