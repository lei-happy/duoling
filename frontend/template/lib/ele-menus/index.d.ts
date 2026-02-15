import { NavigationFailure } from 'vue-router';
import { MenuItemClicked } from 'element-plus';
import { ElMenuInstance, ElSubMenuInstance } from '../ele-app/el';
import { MenuItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    mode: import('vue').PropType<import('./types').MenuMode>;
    items: {
        type: import('vue').PropType<MenuItem[]>;
        required: boolean;
    };
    theme: import('vue').PropType<import('./types').MenuTheme>;
    popupTheme: {
        type: import('vue').PropType<import('./types').PopupMenuTheme>;
        default: string;
    };
    colorful: BooleanConstructor;
    popupColorful: {
        type: import('vue').PropType<import('./types').PopupColorful>;
        default: string;
    };
    firstPopperClass: StringConstructor;
    tooltipDisabled: BooleanConstructor;
    ellipsisProps: import('vue').PropType<import('./types').EllipsisProps>;
    textEllipsisTooltip: import('vue').PropType<import('./types').TextEllipsisTooltip>;
    defaultActive: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    defaultOpeneds: {
        readonly type: import('vue').PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [];
    };
    uniqueOpened: BooleanConstructor;
    router: BooleanConstructor;
    menuTrigger: {
        readonly type: import('vue').PropType<"hover" | "click">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    collapse: BooleanConstructor;
    backgroundColor: StringConstructor;
    textColor: StringConstructor;
    activeTextColor: StringConstructor;
    closeOnClickOutside: BooleanConstructor;
    collapseTransition: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    ellipsis: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    popperOffset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 6;
    };
    ellipsisIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    popperEffect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "dark";
    };
    popperClass: StringConstructor;
    showTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    hideTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
}>, {
    menuRef: import('vue').Ref<ElMenuInstance, ElMenuInstance>;
    ellipsisRef: import('vue').Ref<ElSubMenuInstance, ElSubMenuInstance>;
    open: (index: string) => void;
    close: (index: string) => void;
    updateActiveIndex: (index: string) => void;
    scrollToActive: () => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    select: (index: string, indexPath: string[], item: MenuItemClicked, routerResult?: Promise<void | NavigationFailure> | undefined) => void;
    close: (index: string, indexPath: string[]) => void;
    open: (index: string, indexPath: string[]) => void;
    itemClick: (_item: MenuItem, _e: MouseEvent, _type?: import('./types').MenuItemClickType) => void;
    itemMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    itemMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
    parentMouseenter: (_item: MenuItem, _e: MouseEvent) => void;
    parentMouseleave: (_item: MenuItem, _e: MouseEvent) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    mode: import('vue').PropType<import('./types').MenuMode>;
    items: {
        type: import('vue').PropType<MenuItem[]>;
        required: boolean;
    };
    theme: import('vue').PropType<import('./types').MenuTheme>;
    popupTheme: {
        type: import('vue').PropType<import('./types').PopupMenuTheme>;
        default: string;
    };
    colorful: BooleanConstructor;
    popupColorful: {
        type: import('vue').PropType<import('./types').PopupColorful>;
        default: string;
    };
    firstPopperClass: StringConstructor;
    tooltipDisabled: BooleanConstructor;
    ellipsisProps: import('vue').PropType<import('./types').EllipsisProps>;
    textEllipsisTooltip: import('vue').PropType<import('./types').TextEllipsisTooltip>;
    defaultActive: {
        readonly type: import('vue').PropType<string>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    defaultOpeneds: {
        readonly type: import('vue').PropType<string[]>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => [];
    };
    uniqueOpened: BooleanConstructor;
    router: BooleanConstructor;
    menuTrigger: {
        readonly type: import('vue').PropType<"hover" | "click">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "hover";
    };
    collapse: BooleanConstructor;
    backgroundColor: StringConstructor;
    textColor: StringConstructor;
    activeTextColor: StringConstructor;
    closeOnClickOutside: BooleanConstructor;
    collapseTransition: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    ellipsis: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
    popperOffset: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 6;
    };
    ellipsisIcon: {
        readonly type: import('vue').PropType<string | import('vue').Component>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: () => any;
    };
    popperEffect: {
        readonly type: import('vue').PropType<import('element-plus').PopperEffect>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "dark";
    };
    popperClass: StringConstructor;
    showTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    hideTimeout: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 300;
    };
    persistent: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: true;
    };
}>> & Readonly<{
    onSelect?: ((index: string, indexPath: string[], item: MenuItemClicked, routerResult?: Promise<void | NavigationFailure> | undefined) => any) | undefined;
    onClose?: ((index: string, indexPath: string[]) => any) | undefined;
    onOpen?: ((index: string, indexPath: string[]) => any) | undefined;
    onItemClick?: ((_item: MenuItem, _e: MouseEvent, _type?: import('./types').MenuItemClickType) => any) | undefined;
    onItemMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onItemMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onParentMouseenter?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
    onParentMouseleave?: ((_item: MenuItem, _e: MouseEvent) => any) | undefined;
}>, {
    persistent: boolean;
    showTimeout: number;
    hideTimeout: number;
    defaultActive: string;
    defaultOpeneds: string[];
    uniqueOpened: boolean;
    router: boolean;
    menuTrigger: "hover" | "click";
    collapse: boolean;
    closeOnClickOutside: boolean;
    collapseTransition: boolean;
    ellipsis: boolean;
    popperOffset: number;
    ellipsisIcon: string | import('vue').Component;
    popperEffect: import('element-plus').PopperEffect;
    popupTheme: import('./types').PopupMenuTheme;
    colorful: boolean;
    popupColorful: import('./types').PopupColorful;
    tooltipDisabled: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
