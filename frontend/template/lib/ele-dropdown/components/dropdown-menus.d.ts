import { PropType } from 'vue';
import { ElIconProps, ElButtonProps } from '../../ele-app/el';
import { StyleValue } from '../../ele-app/types';
import { DropdownItem } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: {
    item: DropdownItem;
}) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 下拉菜单数据 */
    items: {
        type: PropType<DropdownItem[]>;
        required: true;
    };
    /** 选中的菜单 */
    selected: PropType<DropdownItem["command"]>;
    /** 自定义下拉菜单样式 */
    menuStyle: PropType<StyleValue>;
    /** 自定义图标属性 */
    iconProps: PropType<ElIconProps>;
    /** 图标尺寸 */
    iconSize: PropType<"small" | "default">;
    /** 尺寸 */
    size: PropType<ElButtonProps["size"]>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_item: DropdownItem, _e: MouseEvent) => void;
    wrapperContext: (_e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 下拉菜单数据 */
    items: {
        type: PropType<DropdownItem[]>;
        required: true;
    };
    /** 选中的菜单 */
    selected: PropType<DropdownItem["command"]>;
    /** 自定义下拉菜单样式 */
    menuStyle: PropType<StyleValue>;
    /** 自定义图标属性 */
    iconProps: PropType<ElIconProps>;
    /** 图标尺寸 */
    iconSize: PropType<"small" | "default">;
    /** 尺寸 */
    size: PropType<ElButtonProps["size"]>;
}>> & Readonly<{
    onItemClick?: ((_item: DropdownItem, _e: MouseEvent) => any) | undefined;
    onWrapperContext?: ((_e: MouseEvent) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
