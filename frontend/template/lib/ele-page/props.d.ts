import { ExtractPropTypes, PropType } from 'vue';

/**
 * 属性
 */
export declare const pageProps: {
    /** 是否是单纯的容器 */
    plain: BooleanConstructor;
    /** 内容是否为多个卡片 */
    multiCard: {
        type: BooleanConstructor;
        default: boolean;
    };
    /** 内部表格是否弹性布局 */
    flexTable: PropType<boolean | "auto">;
    /** 是否关闭页脚 */
    hideFooter: BooleanConstructor;
};
export type PageProps = ExtractPropTypes<typeof pageProps>;
