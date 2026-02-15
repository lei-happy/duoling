import { UserComponent } from '../../ele-app/types';
import { EleCrudProps } from '../../ele-app/plusx';
import { ProFormItemTypeData, ScreenSize } from '../../ele-pro-form/types';
import { HeaderRightToolName } from '../types';

declare function __VLS_template(): {
    headerTools?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 是否禁用撤销 */
    undoDisabled?: boolean;
    /** 是否禁用恢复 */
    redoDisabled?: boolean;
    /** 增删改查配置 */
    config?: EleCrudProps;
    /** 顶栏右侧操作按钮顺序 */
    headerTools?: boolean | HeaderRightToolName[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    "update:currentScreen": (size?: string | undefined) => void;
    undo: () => void;
    redo: () => void;
    clear: () => void;
    importData: (data: EleCrudProps) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<__VLS_TypePropsToRuntimeProps<{
    /** 当前选中屏幕尺寸 */
    currentScreen?: ScreenSize;
    /** 是否禁用撤销 */
    undoDisabled?: boolean;
    /** 是否禁用恢复 */
    redoDisabled?: boolean;
    /** 增删改查配置 */
    config?: EleCrudProps;
    /** 顶栏右侧操作按钮顺序 */
    headerTools?: boolean | HeaderRightToolName[];
    /** 高级表单组件 */
    proFormComponent?: UserComponent;
    /** JSON 编辑器组件 */
    jsonEditerComponent?: UserComponent;
    /** 代码查看器组件 */
    codeViewerComponent?: UserComponent;
    /** 高级表单组件类型数据 */
    itemTypeData?: ProFormItemTypeData[];
    /** 远程数据源请求工具 */
    httpRequest?: any;
}>>> & Readonly<{
    onClear?: (() => any) | undefined;
    onImportData?: ((data: EleCrudProps) => any) | undefined;
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
