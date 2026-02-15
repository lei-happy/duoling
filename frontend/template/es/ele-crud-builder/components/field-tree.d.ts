import { PropType } from 'vue';
import { UserComponent } from '../../ele-app/types';
import { ProFormItemProps, ProFormItemTypeData } from '../../ele-pro-form/types';
import { CrudField } from '../../ele-crud/types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 全部字段 */
    fields: PropType<CrudField[]>;
    /** 字段编辑的表单项配置 */
    fieldEditFormItems: PropType<ProFormItemProps[]>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** JSON 编辑器组件 */
    jsonEditerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    deleteField: (key: string) => void;
    addField: (field: CrudField, parentKey?: string | undefined, index?: number | undefined) => void;
    updateField: (field: CrudField) => void;
    updateFieldChildren: (data: CrudField[], parentKey?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 全部字段 */
    fields: PropType<CrudField[]>;
    /** 字段编辑的表单项配置 */
    fieldEditFormItems: PropType<ProFormItemProps[]>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** JSON 编辑器组件 */
    jsonEditerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>> & Readonly<{
    onDeleteField?: ((key: string) => any) | undefined;
    onAddField?: ((field: CrudField, parentKey?: string | undefined, index?: number | undefined) => any) | undefined;
    onUpdateField?: ((field: CrudField) => any) | undefined;
    onUpdateFieldChildren?: ((data: CrudField[], parentKey?: string | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
