import { PropType } from 'vue';
import { ElProgressProps, ElImageProps } from '../../ele-app/el';
import { UploadItem, UploadLocale, ImageObjectUrl, ListType } from '../types';

declare function __VLS_template(): {
    thumbnail?(_: {
        item: UploadItem;
        imageUrl: string | undefined;
    }): any;
    itemExtra?(_: {
        item: UploadItem;
    }): any;
    progress?(_: {
        item: UploadItem;
    }): any;
    remove?(_: {
        item: UploadItem;
    }): any;
};
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: {
        type: PropType<UploadItem>;
        required: true;
    };
    /** 是否只读 */
    readonly: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否可拖拽排序 */
    sortable: BooleanConstructor;
    /** 图片属性 */
    imageProps: PropType<ElImageProps>;
    /** 进度条属性 */
    progressProps: PropType<ElProgressProps>;
    /** 预读图片文件 */
    imageObjectUrls: PropType<ImageObjectUrl[]>;
    /** 是否开启底部预览和修改的操作按钮 */
    tools: BooleanConstructor;
    /** 列表样式 */
    listType: PropType<ListType>;
    /** 国际化 */
    locale: {
        type: PropType<Partial<UploadLocale>>;
        required: true;
    };
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    remove: (_item: UploadItem) => void;
    retry: (_item: UploadItem) => void;
    preview: (_item: UploadItem) => void;
    edit: (_item: UploadItem) => void;
    itemClick: (_item: UploadItem) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 数据 */
    item: {
        type: PropType<UploadItem>;
        required: true;
    };
    /** 是否只读 */
    readonly: BooleanConstructor;
    /** 是否禁用 */
    disabled: BooleanConstructor;
    /** 是否可拖拽排序 */
    sortable: BooleanConstructor;
    /** 图片属性 */
    imageProps: PropType<ElImageProps>;
    /** 进度条属性 */
    progressProps: PropType<ElProgressProps>;
    /** 预读图片文件 */
    imageObjectUrls: PropType<ImageObjectUrl[]>;
    /** 是否开启底部预览和修改的操作按钮 */
    tools: BooleanConstructor;
    /** 列表样式 */
    listType: PropType<ListType>;
    /** 国际化 */
    locale: {
        type: PropType<Partial<UploadLocale>>;
        required: true;
    };
}>> & Readonly<{
    onRemove?: ((_item: UploadItem) => any) | undefined;
    onRetry?: ((_item: UploadItem) => any) | undefined;
    onPreview?: ((_item: UploadItem) => any) | undefined;
    onEdit?: ((_item: UploadItem) => any) | undefined;
    onItemClick?: ((_item: UploadItem) => any) | undefined;
}>, {
    disabled: boolean;
    readonly: boolean;
    sortable: boolean;
    tools: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
