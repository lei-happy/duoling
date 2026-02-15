import { UserComponent } from '../../ele-app/types';
import { EleProFormProps } from '../../ele-app/plusx';
import { ProFormItemKey, ProFormItemTypeData } from '../../ele-pro-form/types';
import { ComponentGroup, UpdateItemsResult } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选中的表单项 id */
    currentFormItemId?: ProFormItemKey;
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 表单属性设置的组件预设属性值 */
    configFormPresetProps?: Record<string, any>;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 富文本编辑器组件 */
    htmlEditerComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentFormItemId": (formItemId?: string | undefined) => void;
    updateItem: (formItemId: string | number | symbol, field: string, value: any) => void;
    updateItems: (result: UpdateItemsResult) => void;
    sortItemChildren: (childIds: string[], formItemId: string | number | symbol) => void;
    openComponentPicker: (formItemId: string, formItemType?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 选中的表单项 id */
    currentFormItemId?: ProFormItemKey;
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 表单属性设置的组件预设属性值 */
    configFormPresetProps?: Record<string, any>;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** 代码编辑器组件 */
    codeEditerComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 富文本编辑器组件 */
    htmlEditerComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>> & Readonly<{
    onUpdateItems?: ((result: UpdateItemsResult) => any) | undefined;
    "onUpdate:currentFormItemId"?: ((formItemId?: string | undefined) => any) | undefined;
    onOpenComponentPicker?: ((formItemId: string, formItemType?: string | undefined) => any) | undefined;
    onUpdateItem?: ((formItemId: string | number | symbol, field: string, value: any) => any) | undefined;
    onSortItemChildren?: ((childIds: string[], formItemId: string | number | symbol) => any) | undefined;
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
