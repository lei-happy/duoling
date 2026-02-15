import { PropType } from 'vue';
import { UserComponent } from '../../ele-app/types';
import { DataItem } from '../../ele-data-table/types';
import { ProFormItemTypeData, ScreenSize } from '../../ele-pro-form/types';
import { EditConfig, BtnClickAction, CrudField, EditApi, GetAndCacheCodeFunction, CrudLocale } from '../types';

declare function __VLS_template(): Partial<Record<string, (_: any) => any>> & Partial<Record<string, (_: any) => any>> & {
    default?(_: {}): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 添加弹窗是否打开 */
    addVisible: PropType<boolean>;
    /** 添加弹窗数据 */
    addData: PropType<DataItem>;
    /** 修改弹窗是否打开 */
    editVisible: PropType<boolean>;
    /** 修改弹窗数据 */
    editData: PropType<DataItem>;
    /** 添加配置 */
    addConfig: PropType<EditConfig | boolean>;
    /** 修改配置 */
    editConfig: PropType<EditConfig | boolean>;
    /** 字段数据 */
    fields: PropType<CrudField[]>;
    /** 获取字段数据对应的表单项的方法 */
    getAndCacheCode: {
        type: PropType<GetAndCacheCodeFunction>;
        required: true;
    };
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 添加数据接口 */
    addApi: PropType<EditApi | string>;
    /** 修改数据接口 */
    editApi: PropType<EditApi | string>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
    /** 国际化 */
    lang: {
        type: PropType<Partial<CrudLocale>>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    editError: (_e: Error) => void;
    addError: (_e: Error) => void;
    "update:addVisible": (_visible?: boolean | undefined) => void;
    "update:editVisible": (_visible?: boolean | undefined) => void;
    btnClick: (_action: BtnClickAction, _e: MouseEvent, _item?: DataItem | undefined) => void;
    addDone: (_msg?: string | undefined) => void;
    editDone: (_msg?: string | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 添加弹窗是否打开 */
    addVisible: PropType<boolean>;
    /** 添加弹窗数据 */
    addData: PropType<DataItem>;
    /** 修改弹窗是否打开 */
    editVisible: PropType<boolean>;
    /** 修改弹窗数据 */
    editData: PropType<DataItem>;
    /** 添加配置 */
    addConfig: PropType<EditConfig | boolean>;
    /** 修改配置 */
    editConfig: PropType<EditConfig | boolean>;
    /** 字段数据 */
    fields: PropType<CrudField[]>;
    /** 获取字段数据对应的表单项的方法 */
    getAndCacheCode: {
        type: PropType<GetAndCacheCodeFunction>;
        required: true;
    };
    /** 高级表单组件 */
    proFormComponent: PropType<UserComponent>;
    /** 添加数据接口 */
    addApi: PropType<EditApi | string>;
    /** 修改数据接口 */
    editApi: PropType<EditApi | string>;
    /** 高级表单组件类型数据 */
    itemTypeData: PropType<ProFormItemTypeData[]>;
    /** 远程数据源请求工具 */
    httpRequest: (ObjectConstructor | FunctionConstructor)[];
    /** 屏幕尺寸 */
    screenSize: PropType<ScreenSize>;
    /** 国际化 */
    lang: {
        type: PropType<Partial<CrudLocale>>;
        required: true;
    };
}>> & Readonly<{
    onEditError?: ((_e: Error) => any) | undefined;
    onAddError?: ((_e: Error) => any) | undefined;
    "onUpdate:addVisible"?: ((_visible?: boolean | undefined) => any) | undefined;
    "onUpdate:editVisible"?: ((_visible?: boolean | undefined) => any) | undefined;
    onBtnClick?: ((_action: BtnClickAction, _e: MouseEvent, _item?: DataItem | undefined) => any) | undefined;
    onAddDone?: ((_msg?: string | undefined) => any) | undefined;
    onEditDone?: ((_msg?: string | undefined) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
