import { ExtractPropTypes, PropType } from 'vue';
import { StyleValue } from '../ele-app/types';
import { ElCardProps } from '../ele-app/el';

/**
 * 属性
 */
export declare const cardProps: {
    /** 标题 */
    header: StringConstructor;
    /** 标题类名 */
    headerClass: StringConstructor;
    /** 页脚 */
    footer: StringConstructor;
    /** 页脚类名 */
    footerClass: StringConstructor;
    /** 主体样式 */
    bodyStyle: PropType<StyleValue>;
    /** 主体类名 */
    bodyClass: StringConstructor;
    /** 阴影 */
    shadow: PropType<ElCardProps["shadow"]>;
    /** 边框 */
    bordered: BooleanConstructor;
    /** 标题栏样式 */
    headerStyle: PropType<StyleValue>;
    /** 标题样式 */
    titleStyle: PropType<StyleValue>;
    /** 页脚样式 */
    footerStyle: PropType<StyleValue>;
    /** 是否可折叠 */
    collapsable: PropType<boolean | "header">;
    /** 是否折叠 */
    collapse: BooleanConstructor;
    /** 折叠按钮样式 */
    collapseIconStyle: PropType<StyleValue>;
    /** 是否是搜索表单卡片 */
    searchForm: BooleanConstructor;
    /** 内部表格是否弹性布局 */
    flexTable: PropType<boolean | "auto">;
};
export type CardProps = ExtractPropTypes<typeof cardProps>;
/**
 * 事件
 */
export declare const cardEmits: {
    /** 折叠展开事件 */
    collapseChange: (_collapse: boolean) => boolean;
};
