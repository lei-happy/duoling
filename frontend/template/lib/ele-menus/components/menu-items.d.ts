import { PropType } from 'vue';
import { MenuItem, MenuTheme, PopupMenuTheme, PopupColorful, MenuItemClickType } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    title?(_: {
        item: MenuItem;
        title: string | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 菜单数据 */
    items: PropType<MenuItem[]>;
    /** 是否是第一级菜单 */
    first: BooleanConstructor;
    /** 是否禁用折叠的 tooltip */
    tipDisabled: BooleanConstructor;
    /** 父级是否是分组菜单 */
    parentIsGroup: BooleanConstructor;
    /** 主题 */
    theme: PropType<MenuTheme>;
    /** 气泡菜单主题 */
    popTheme: PropType<PopupMenuTheme>;
    /** 是否彩色图标 */
    colorful: BooleanConstructor;
    /** 气泡菜单是否彩色图标 */
    popupColorful: PropType<PopupColorful>;
    /** 第一级气泡菜单类名 */
    firstPopClass: StringConstructor;
    /** 是否是 webkit 内核 */
    webkit: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => void;
    itemMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    itemMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
    parentMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    parentMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 菜单数据 */
    items: PropType<MenuItem[]>;
    /** 是否是第一级菜单 */
    first: BooleanConstructor;
    /** 是否禁用折叠的 tooltip */
    tipDisabled: BooleanConstructor;
    /** 父级是否是分组菜单 */
    parentIsGroup: BooleanConstructor;
    /** 主题 */
    theme: PropType<MenuTheme>;
    /** 气泡菜单主题 */
    popTheme: PropType<PopupMenuTheme>;
    /** 是否彩色图标 */
    colorful: BooleanConstructor;
    /** 气泡菜单是否彩色图标 */
    popupColorful: PropType<PopupColorful>;
    /** 第一级气泡菜单类名 */
    firstPopClass: StringConstructor;
    /** 是否是 webkit 内核 */
    webkit: BooleanConstructor;
}>> & Readonly<{
    onItemClick?: ((_item: MenuItem, _e: MouseEvent, _type?: MenuItemClickType) => any) | undefined;
    onItemMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onItemMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onParentMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onParentMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
}>, {
    colorful: boolean;
    first: boolean;
    tipDisabled: boolean;
    parentIsGroup: boolean;
    webkit: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
