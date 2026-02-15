import { PropType } from 'vue';
import { TabItem } from '../types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 是否支持内嵌缓存 */
    keepAlive: BooleanConstructor;
    /** 内嵌切换动画 */
    transitionName: StringConstructor;
    /** 内嵌进入动画延迟时间 */
    transitionDelay: NumberConstructor;
    /** 页签数据 */
    tabData: {
        type: PropType<TabItem[]>;
        required: true;
    };
    /** 页签选中 */
    tabActive: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 是否支持内嵌缓存 */
    keepAlive: BooleanConstructor;
    /** 内嵌切换动画 */
    transitionName: StringConstructor;
    /** 内嵌进入动画延迟时间 */
    transitionDelay: NumberConstructor;
    /** 页签数据 */
    tabData: {
        type: PropType<TabItem[]>;
        required: true;
    };
    /** 页签选中 */
    tabActive: StringConstructor;
}>> & Readonly<{}>, {
    keepAlive: boolean;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
