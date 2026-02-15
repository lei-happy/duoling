import { PropType } from 'vue';
import { TableSize } from '../../ele-data-table/types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 是否是选中状态 */
    checked: BooleanConstructor;
    /** 是否是半选状态 */
    indeterminate: BooleanConstructor;
    /** 是否是禁用状态 */
    disabled: BooleanConstructor;
    /** 尺寸 */
    size: PropType<TableSize>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    change: (_checked: boolean) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 是否是选中状态 */
    checked: BooleanConstructor;
    /** 是否是半选状态 */
    indeterminate: BooleanConstructor;
    /** 是否是禁用状态 */
    disabled: BooleanConstructor;
    /** 尺寸 */
    size: PropType<TableSize>;
}>> & Readonly<{
    onChange?: ((_checked: boolean) => any) | undefined;
}>, {
    disabled: boolean;
    indeterminate: boolean;
    checked: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
