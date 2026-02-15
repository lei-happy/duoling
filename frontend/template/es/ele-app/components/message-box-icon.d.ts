import { PropType } from 'vue';
import { ElMessageBoxOptions } from '../el';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    /** 类型 */
    type: PropType<ElMessageBoxOptions["type"]>;
    /** 图标 */
    icon: PropType<ElMessageBoxOptions["icon"]>;
    /** 标识id */
    boxId: StringConstructor;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    boxDestroy: (_boxId?: string | undefined) => void;
    boxMounted: (_: {
        boxId?: string;
        doClose?: () => void;
    }) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    /** 类型 */
    type: PropType<ElMessageBoxOptions["type"]>;
    /** 图标 */
    icon: PropType<ElMessageBoxOptions["icon"]>;
    /** 标识id */
    boxId: StringConstructor;
}>> & Readonly<{
    onBoxDestroy?: ((_boxId?: string | undefined) => any) | undefined;
    onBoxMounted?: ((_: {
        boxId?: string;
        doClose?: () => void;
    }) => any) | undefined;
}>, {}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
