import { PropType, ExtractPropTypes } from 'vue';
import { StyleValue } from '../ele-app/types';

/**
 * 属性
 */
export declare const bottomBarProps: {
    /** 内容样式 */
    bodyStyle: PropType<StyleValue>;
    /** 右侧样式 */
    extraStyle: PropType<StyleValue>;
    /** 是否插入到布局的内容节点后 */
    teleported: BooleanConstructor;
};
export type BottomBarProps = ExtractPropTypes<typeof bottomBarProps>;
