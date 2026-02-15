import { UserComponent } from '../../ele-app/types';
import { EleProFormProps } from '../../ele-app/plusx';
import { ProFormItemTypeData, ScreenSize } from '../../ele-pro-form/types';
import { HeaderRightToolName, ComponentGroup } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & {
    headerTools?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 是否禁用撤销 */
    undoDisabled?: boolean;
    /** 是否禁用恢复 */
    redoDisabled?: boolean;
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 顶栏右侧操作按钮顺序 */
    headerTools?: boolean | HeaderRightToolName[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentScreen": (size?: string | undefined) => void;
    undo: () => void;
    redo: () => void;
    clear: () => void;
    previewFormSubmit: (data: Record<string, any>) => void;
    importData: (data: EleProFormProps) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 是否禁用撤销 */
    undoDisabled?: boolean;
    /** 是否禁用恢复 */
    redoDisabled?: boolean;
    /** 表单属性 */
    formProps?: EleProFormProps;
    /** 顶栏右侧操作按钮顺序 */
    headerTools?: boolean | HeaderRightToolName[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
    /** 组件库数据 */
    componentData?: ComponentGroup[];
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>> & Readonly<{
    onClear?: (() => any) | undefined;
    onImportData?: ((data: EleProFormProps) => any) | undefined;
    onPreviewFormSubmit?: ((data: Record<string, any>) => any) | undefined;
    "onUpdate:currentScreen"?: ((size?: string | undefined) => any) | undefined;
    onUndo?: (() => any) | undefined;
    onRedo?: (() => any) | undefined;
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
