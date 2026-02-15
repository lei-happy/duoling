import { PropType, ExtractPropTypes } from 'vue';
import { UserComponent } from '../ele-app/types';
import { EleSplitPanelProps } from '../ele-app/plus';
import { EleProFormProps } from '../ele-app/plusx';
import { ProFormItemProps, ProFormItemTypeData } from '../ele-pro-form/types';
import { TemplateFormProps, ComponentGroup, TemplateItem, HeaderRightToolName } from './types';

/**
 * 属性
 */
export declare const proFormBuilderProps: {
    /** 配置数据 */
    modelValue: PropType<EleProFormProps>;
    /** 顶栏右侧操作按钮顺序 */
    headerTools: {
        type: PropType<boolean | HeaderRightToolName[]>;
        default: () => undefined;
    };
    /** 组件库数据 */
    componentData: PropType<ComponentGroup[]>;
    /** 模板库数据 */
    templateData: PropType<TemplateItem[]>;
    /** 表单属性设置的表单项配置 */
    configFormItems: PropType<ProFormItemProps[]>;
    /** 表单属性设置的组件预设属性值 */
    configFormPresetProps: PropType<TemplateFormProps>;
    /** 初始添加时的表单属性 */
    proFormInitialProps: PropType<TemplateFormProps>;
    /** 自定义分割面板组件属性 */
    splitPanelProps: PropType<EleSplitPanelProps>;
    /** 自定义右侧分割面板组件属性 */
    rightSplitPanelProps: PropType<EleSplitPanelProps>;
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 代码编辑器组件 */
    codeEditerComponent: PropType<UserComponent>;
    /** JSON 编辑器组件 */
    jsonEditerComponent: PropType<UserComponent>;
    /** 富文本编辑器组件 */
    htmlEditerComponent: PropType<UserComponent>;
    /** 代码查看器组件 */
    codeViewerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
};
export type ProFormBuilderProps = ExtractPropTypes<typeof proFormBuilderProps>;
/**
 * 事件
 */
export declare const proFormBuilderEmits: {
    'update:modelValue': (_config: EleProFormProps) => boolean;
    previewFormSubmit: (_data: Record<string, any>) => boolean;
};
