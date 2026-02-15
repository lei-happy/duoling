import { ExtractPropTypes } from 'vue';

/**
 * 属性
 */
export declare const tabToolProps: {
    /** 是否为模拟页签 */
    tab: BooleanConstructor;
    /** 为模拟页签时是否选中 */
    active: BooleanConstructor;
    /** 为模拟页签时页签标识 */
    tabName: (StringConstructor | NumberConstructor)[];
};
export type TabToolProps = ExtractPropTypes<typeof tabToolProps>;
