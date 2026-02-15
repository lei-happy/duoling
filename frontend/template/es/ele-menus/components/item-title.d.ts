import { PropType } from 'vue';
import { MenuItem } from '../types';

declare function __VLS_template(): {
    icon?(_: {
        item: MenuItem;
        icon: import('../../ele-app/types').UserComponent | undefined;
    }): any;
    title?(_: {
        item: MenuItem;
        title: string | undefined;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 菜单项数据 */
    item: {
        type: PropType<MenuItem>;
        required: true;
    };
    /** 是否需要标题 */
    showTitle: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否需要链接 */
    showLink: BooleanConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    itemClick: (_item: MenuItem, _e: MouseEvent) => void;
    itemMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    itemMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 菜单项数据 */
    item: {
        type: PropType<MenuItem>;
        required: true;
    };
    /** 是否需要标题 */
    showTitle: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 是否需要链接 */
    showLink: BooleanConstructor;
}>> & Readonly<{
    onItemClick?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onItemMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onItemMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
}>, {
    showLink: boolean;
    showTitle: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
