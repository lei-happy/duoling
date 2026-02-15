import { PropType } from 'vue';
import { EleTooltipProps } from '../../ele-app/plus';
import { UploadOption, BeforeUploadClick, CropperLocale } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 操作按钮布局 */
    tools: StringConstructor;
    /** 允许上传的图片类型 */
    accept: StringConstructor;
    /** 是否需要提示组件 */
    tooltip: BooleanConstructor;
    /** 提示组件属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 上传按钮点击前的钩子 */
    beforeUploadClick: PropType<BeforeUploadClick>;
    /** 国际化 */
    locale: PropType<Partial<CropperLocale>>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    reset: () => void;
    upload: (_option?: UploadOption | undefined) => void;
    zoomIn: () => void;
    zoomOut: () => void;
    moveLeft: () => void;
    moveRight: () => void;
    moveUp: () => void;
    moveDown: () => void;
    rotateLeft: () => void;
    rotateRight: () => void;
    flipX: () => void;
    flipY: () => void;
    ok: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 操作按钮布局 */
    tools: StringConstructor;
    /** 允许上传的图片类型 */
    accept: StringConstructor;
    /** 是否需要提示组件 */
    tooltip: BooleanConstructor;
    /** 提示组件属性 */
    tooltipProps: PropType<EleTooltipProps>;
    /** 上传按钮点击前的钩子 */
    beforeUploadClick: PropType<BeforeUploadClick>;
    /** 国际化 */
    locale: PropType<Partial<CropperLocale>>;
}>> & Readonly<{
    onReset?: (() => any) | undefined;
    onUpload?: ((_option?: UploadOption | undefined) => any) | undefined;
    onZoomIn?: (() => any) | undefined;
    onZoomOut?: (() => any) | undefined;
    onMoveLeft?: (() => any) | undefined;
    onMoveRight?: (() => any) | undefined;
    onMoveUp?: (() => any) | undefined;
    onMoveDown?: (() => any) | undefined;
    onRotateLeft?: (() => any) | undefined;
    onRotateRight?: (() => any) | undefined;
    onFlipX?: (() => any) | undefined;
    onFlipY?: (() => any) | undefined;
    onOk?: (() => any) | undefined;
}>, {
    tooltip: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
