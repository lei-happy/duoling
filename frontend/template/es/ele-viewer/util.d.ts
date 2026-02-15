/**
 * 计算旋转后的宽高
 * @param w 宽
 * @param h 高
 * @param r 旋转角度
 */
export declare function getRotatedBounds(w: number, h: number, r: number): {
    width: number;
    height: number;
};
/**
 * 内容容器样式处理
 * @param updateStyle 更新样式
 */
export declare function useContentRatio(updateStyle?: any): {
    LoadingSpinner: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
        width: {
            type: NumberConstructor;
            default: number;
        };
        height: {
            type: NumberConstructor;
            default: number;
        };
        rotate: {
            type: NumberConstructor;
            default: number;
        };
        gapX: {
            type: NumberConstructor;
            default: number;
        };
        gapY: {
            type: NumberConstructor;
            default: number;
        };
        lineGap: {
            type: NumberConstructor;
            default: number;
        };
        font: {
            type: import('vue').PropType<Required<import('../ele-watermark/types').WatermarkFont>>;
            required: true;
        };
        contents: {
            type: import('vue').PropType<string[]>;
            required: true;
        };
        image: StringConstructor;
        offsetX: {
            type: NumberConstructor;
            default: number;
        };
        offsetY: {
            type: NumberConstructor;
            default: number;
        };
        commonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    }>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
        width: {
            type: NumberConstructor;
            default: number;
        };
        height: {
            type: NumberConstructor;
            default: number;
        };
        rotate: {
            type: NumberConstructor;
            default: number;
        };
        gapX: {
            type: NumberConstructor;
            default: number;
        };
        gapY: {
            type: NumberConstructor;
            default: number;
        };
        lineGap: {
            type: NumberConstructor;
            default: number;
        };
        font: {
            type: import('vue').PropType<Required<import('../ele-watermark/types').WatermarkFont>>;
            required: true;
        };
        contents: {
            type: import('vue').PropType<string[]>;
            required: true;
        };
        image: StringConstructor;
        offsetX: {
            type: NumberConstructor;
            default: number;
        };
        offsetY: {
            type: NumberConstructor;
            default: number;
        };
        commonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    }>> & Readonly<{}>, {
        height: number;
        rotate: number;
        width: number;
        gapX: number;
        gapY: number;
        lineGap: number;
        offsetX: number;
        offsetY: number;
    }, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
    slotProps: Record<string, any>;
    show: import('vue').ComputedRef<any>;
    to: import('vue').ComputedRef<HTMLElement | "body">;
};
