import { PropType, ExtractPropTypes } from 'vue';
import { ElDividerProps } from '../ele-app/el';
import { ButtonItem, ButtonItemType, ButtonsLocale } from './types';

/**
 * 属性
 */
export declare const buttonsProps: {
    /** 按钮数据 */
    items: PropType<ButtonItem[]>;
    /** 是否显示分割线 */
    divider: PropType<boolean | ElDividerProps>;
    /** 组件类型 */
    type: PropType<ButtonItemType>;
    /** 间距 */
    gap: {
        type: (BooleanConstructor | NumberConstructor)[];
        default: null;
    };
    /** 是否自动换行 */
    wrap: {
        type: BooleanConstructor;
        default: null;
    };
    /** 是否是弹窗底栏 */
    modalFooter: BooleanConstructor;
    /** 国际化 */
    locale: PropType<Partial<ButtonsLocale>>;
};
export type ButtonsProps = ExtractPropTypes<typeof buttonsProps>;
/**
 * 事件
 */
export declare const buttonsEmits: {
    itemClick: (_command: any, _e?: MouseEvent) => boolean;
};
