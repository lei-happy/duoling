import { PropType } from 'vue';
import { EleDropdownProps, EleDropdownInstance } from '../../ele-app/plus';
import { DropdownItem } from '../../ele-dropdown/types';

declare function __VLS_template(): {
    icon?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 右键菜单 */
    items: PropType<DropdownItem[]>;
    /** 右键菜单属性 */
    dropdownProps: PropType<EleDropdownProps>;
    /** 是否点击后自动关闭菜单 */
    autoClose: {
        type: BooleanConstructor;
        default: boolean;
    };
}>, {
    dropdownRef: import('vue').Ref<EleDropdownInstance, EleDropdownInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    menuClick: (_command: string) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 右键菜单 */
    items: PropType<DropdownItem[]>;
    /** 右键菜单属性 */
    dropdownProps: PropType<EleDropdownProps>;
    /** 是否点击后自动关闭菜单 */
    autoClose: {
        type: BooleanConstructor;
        default: boolean;
    };
}>> & Readonly<{
    onMenuClick?: ((_command: string) => any) | undefined;
}>, {
    autoClose: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
