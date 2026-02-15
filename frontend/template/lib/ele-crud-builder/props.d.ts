import { PropType, ExtractPropTypes } from 'vue';
import { UserComponent } from '../ele-app/types';
import { EleSplitPanelProps } from '../ele-app/plus';
import { EleCrudProps, EleProFormBuilderProps } from '../ele-app/plusx';
import { ProFormItemProps, ProFormItemTypeData } from '../ele-pro-form/types';
import { HeaderRightToolName, TemplateItem } from './types';

/**
 * 属性
 */
export declare const crudBuilderProps: {
    /** 增删改查配置 */
    modelValue: PropType<EleCrudProps>;
    /** 顶栏右侧操作按钮顺序 */
    headerTools: {
        type: PropType<boolean | HeaderRightToolName[]>;
        default: () => undefined;
    };
    /** 模板库数据 */
    templateData: PropType<TemplateItem[]>;
    /** 页面设置的表单项配置 */
    pageConfigFormItems: PropType<ProFormItemProps[]>;
    /** 字段编辑的表单项配置 */
    fieldEditFormItems: PropType<ProFormItemProps[]>;
    /** 自定义分割面板组件属性 */
    splitPanelProps: PropType<EleSplitPanelProps>;
    /** 增删改查组件 */
    crudComponent: PropType<UserComponent>;
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
    /** 代码查看器组件 */
    codeViewerComponent: PropType<UserComponent>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
};
export type CrudBuilderProps = ExtractPropTypes<typeof crudBuilderProps>;
/**
 * 事件
 */
export declare const crudBuilderEmits: {
    'update:modelValue': (_config?: EleCrudProps) => boolean;
};
