import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElProgressProps, ElImageProps } from '../ele-app/el';
import { EleImageViewerProps } from '../ele-app/plus';
import { UploadItem, UploadLocale, EditUploadResult, ListType, BeforeUploadClick, BeforeItemEdit, BeforePreview } from './types';

/**
 * 属性
 */
export declare const uploadListProps: {
    /** 已上传列表 */
    modelValue: PropType<UploadItem[]>;
    /** 是否只读 */
    readonly: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否支持点击预览打开图片预览组件 */
    preview: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 最大上传数量 */
    limit: NumberConstructor;
    /** 是否支持多选文件 */
    multiple: BooleanConstructor;
    /** 是否启用拖拽上传 */
    drag: BooleanConstructor;
    /** 接受上传的文件类型 */
    accept: {
        type: StringConstructor;
        default: string;
    };
    /** 自定义条目样式 */
    itemStyle: PropType<StyleValue | false>;
    /** 自定义上传按钮样式 */
    buttonStyle: {
        type: PropType<StyleValue | false>;
        default: null;
    };
    /** 是否开启拖拽排序 */
    sortable: {
        type: PropType<boolean | Record<keyof any, any>>;
        default: boolean;
    };
    /** 自定义图片属性 */
    imageProps: PropType<ElImageProps>;
    /** 自定义进度条属性 */
    progressProps: PropType<ElProgressProps>;
    /** 自定义图片预览属性 */
    previewProps: PropType<EleImageViewerProps>;
    /** 是否开启底部预览和修改的操作按钮 */
    tools: BooleanConstructor;
    /** 列表显示样式 */
    listType: PropType<ListType>;
    /** 上传按钮点击前的钩子 */
    beforeUploadClick: PropType<BeforeUploadClick>;
    /** 修改按钮点击前的钩子 */
    beforeItemEdit: PropType<BeforeItemEdit>;
    /** 预览按钮点击前的钩子 */
    beforePreview: PropType<BeforePreview>;
    /** 国际化 */
    locale: PropType<Partial<UploadLocale>>;
};
export type UploadListProps = ExtractPropTypes<typeof uploadListProps>;
/**
 * 事件
 */
export declare const uploadListEmits: {
    /** 更新绑定值 */
    'update:modelValue': (_value: UploadItem[]) => boolean;
    /** item 点击事件 */
    itemClick: (_item: UploadItem) => boolean;
    /** 上传事件 */
    upload: (_item: UploadItem) => boolean;
    /** item 移除事件 */
    remove: (_item: UploadItem) => boolean;
    /** item 上传失败重试事件 */
    retry: (_item: UploadItem) => boolean;
    /** item 修改上传事件 */
    editUpload: (_result: EditUploadResult) => boolean;
    /** item 预览事件 */
    preview: (_item: UploadItem) => boolean;
};
