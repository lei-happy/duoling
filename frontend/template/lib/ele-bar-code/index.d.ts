import { default as JsBarCode } from 'jsbarcode';
import { JsBarCodeInstance } from './types';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    value: StringConstructor;
    tag: {
        type: import('vue').PropType<import('./types').BarCodeTag>;
        default: string;
    };
    options: import('vue').PropType<JsBarCode.Options>;
}>, {
    instance: null;
    getInstance: () => JsBarCodeInstance;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    value: StringConstructor;
    tag: {
        type: import('vue').PropType<import('./types').BarCodeTag>;
        default: string;
    };
    options: import('vue').PropType<JsBarCode.Options>;
}>> & Readonly<{}>, {
    tag: import('./types').BarCodeTag;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
