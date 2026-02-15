import { PropType } from 'vue';
import { UserComponent } from '../../ele-app/types';
import { DataItem } from '../../ele-data-table/types';
import { ProFormItemTypeData, ScreenSize } from '../../ele-pro-form/types';
import { EditConfig, CrudField, EditApi, GetFieldsFormItemsFunction, GetAndCacheCodeFunction } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 弹窗是否打开 */
    modelValue: PropType<boolean>;
    /** 编辑弹窗数据 */
    data: PropType<DataItem>;
    /** 弹窗标题 */
    title: StringConstructor;
    /** 编辑配置 */
    editConfig: PropType<EditConfig>;
    /** 字段数据 */
    fields: PropType<CrudField[]>;
    /** 获取字段数据对应的表单项的方法 */
    getFieldsEditFormItems: PropType<GetFieldsFormItemsFunction>;
    /** 获取字段数据对应的表单项的方法 */
    getAndCacheCode: {
        type: PropType<GetAndCacheCodeFunction>;
        required: true;
    };
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 修改数据接口 */
    editApi: PropType<EditApi | string>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:modelValue": (_visible?: boolean | undefined) => void;
    editError: (_e: Error) => void;
    editDone: (_msg?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 弹窗是否打开 */
    modelValue: PropType<boolean>;
    /** 编辑弹窗数据 */
    data: PropType<DataItem>;
    /** 弹窗标题 */
    title: StringConstructor;
    /** 编辑配置 */
    editConfig: PropType<EditConfig>;
    /** 字段数据 */
    fields: PropType<CrudField[]>;
    /** 获取字段数据对应的表单项的方法 */
    getFieldsEditFormItems: PropType<GetFieldsFormItemsFunction>;
    /** 获取字段数据对应的表单项的方法 */
    getAndCacheCode: {
        type: PropType<GetAndCacheCodeFunction>;
        required: true;
    };
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 修改数据接口 */
    editApi: PropType<EditApi | string>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
}>> & Readonly<{
    "onUpdate:modelValue"?: ((_visible?: boolean | undefined) => any) | undefined;
    onEditError?: ((_e: Error) => any) | undefined;
    onEditDone?: ((_msg?: string | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
