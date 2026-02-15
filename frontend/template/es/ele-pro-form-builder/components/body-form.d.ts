import { UserComponent } from '../../ele-app/types';
import { EleProFormProps } from '../../ele-app/plusx';
import { ProFormItemKey, ProFormItemProps, ProFormItemTypeData, ScreenSize } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 选中的表单项 id */
    currentFormItemId?: ProFormItemKey;
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentFormItemId": (formItemId?: string | number | symbol | undefined) => void;
    updateItems: (result: UpdateItemsResult) => void;
    openTableTool: (formItemId: string, el: HTMLElement) => void;
    updateFormItems: (items: ProFormItemProps[]) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 选中的表单项 id */
    currentFormItemId?: ProFormItemKey;
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>> & Readonly<{
    onUpdateItems?: ((result: UpdateItemsResult) => any) | undefined;
    "onUpdate:currentFormItemId"?: ((formItemId?: string | number | symbol | undefined) => any) | undefined;
    onOpenTableTool?: ((formItemId: string, el: HTMLElement) => any) | undefined;
    onUpdateFormItems?: ((items: ProFormItemProps[]) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_NonUndefinedable<T> = T extends undefined ? never : T;
type __VLS_TypePropsToRuntimeProps<T> = {
    [K in keyof T]-?: {} extends Pick<T, K> ? {
        type: import('vue').PropType<__VLS_NonUndefinedable<T[K]>>;
    } : {
        type: import('vue').PropType<T[K]>;
        required: true;
    };
};
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
