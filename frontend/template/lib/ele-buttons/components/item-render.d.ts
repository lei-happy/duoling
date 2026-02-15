import { PropType } from 'vue';
import { ElDividerProps } from '../../ele-app/el';
import { ButtonItem, ButtonItemType, ButtonsLocale } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 按钮数据 */
    item: {
        type: PropType<ButtonItem>;
        required: true;
    };
    /** 是否显示分割线 */
    divider: PropType<boolean | ElDividerProps>;
    /** 组件类型 */
    type: PropType<ButtonItemType>;
    /** 是否增加包裹类名 */
    wrapClass: BooleanConstructor;
    /** 文案 */
    lang: {
        type: PropType<ButtonsLocale>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_command: any, _e?: MouseEvent | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 按钮数据 */
    item: {
        type: PropType<ButtonItem>;
        required: true;
    };
    /** 是否显示分割线 */
    divider: PropType<boolean | ElDividerProps>;
    /** 组件类型 */
    type: PropType<ButtonItemType>;
    /** 是否增加包裹类名 */
    wrapClass: BooleanConstructor;
    /** 文案 */
    lang: {
        type: PropType<ButtonsLocale>;
        required: true;
    };
}>> & Readonly<{
    onItemClick?: ((_command: any, _e?: MouseEvent | undefined) => any) | undefined;
}>, {
    wrapClass: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
