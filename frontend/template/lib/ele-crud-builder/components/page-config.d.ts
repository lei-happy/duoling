import { PropType } from 'vue';
import { UserComponent } from '../../ele-app/types';
import { EleCrudProps, EleProFormBuilderProps, EleProFormProps } from '../../ele-app/plusx';
import { ProFormItemTypeData, ProFormItemProps } from '../../ele-pro-form/types';
import { FormDesignType } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 配置数据 */
    config: PropType<EleCrudProps>;
    /** 页面设置的表单项配置 */
    pageConfigFormItems: PropType<ProFormItemProps[]>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 表单构建组件 */
    proFormBuilderComponent: PropType<UserComponent>;
    /** 表单构建组件属性 */
    proFormBuilderProps: PropType<EleProFormBuilderProps>;
    /** 代码编辑器组件 */
    codeEditerComponent: PropType<UserComponent>;
    /** JSON 编辑器组件 */
    jsonEditerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    updateConfigValue: (field: string, value: any) => void;
    updateFormConfig: (data?: EleProFormProps | undefined, type?: FormDesignType | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 配置数据 */
    config: PropType<EleCrudProps>;
    /** 页面设置的表单项配置 */
    pageConfigFormItems: PropType<ProFormItemProps[]>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 表单构建组件 */
    proFormBuilderComponent: PropType<UserComponent>;
    /** 表单构建组件属性 */
    proFormBuilderProps: PropType<EleProFormBuilderProps>;
    /** 代码编辑器组件 */
    codeEditerComponent: PropType<UserComponent>;
    /** JSON 编辑器组件 */
    jsonEditerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
}>> & Readonly<{
    onUpdateConfigValue?: ((field: string, value: any) => any) | undefined;
    onUpdateFormConfig?: ((data?: EleProFormProps | undefined, type?: FormDesignType | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
