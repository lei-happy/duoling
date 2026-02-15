declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    value: StringConstructor;
    size: {
        type: NumberConstructor;
        default: number;
    };
    level: {
        type: import('vue').PropType<import('../ele-qr-code/types').Level>;
        default: string;
    };
    bgColor: {
        type: StringConstructor;
        default: string;
    };
    fgColor: {
        type: StringConstructor;
        default: string;
    };
    margin: {
        type: NumberConstructor;
        default: number;
    };
    imageSettings: import('vue').PropType<import('../ele-qr-code/types').ImageSettings>;
    customStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tag: import('vue').PropType<import('../ele-qr-code/types').QrCodeTag>;
}>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    done: () => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    value: StringConstructor;
    size: {
        type: NumberConstructor;
        default: number;
    };
    level: {
        type: import('vue').PropType<import('../ele-qr-code/types').Level>;
        default: string;
    };
    bgColor: {
        type: StringConstructor;
        default: string;
    };
    fgColor: {
        type: StringConstructor;
        default: string;
    };
    margin: {
        type: NumberConstructor;
        default: number;
    };
    imageSettings: import('vue').PropType<import('../ele-qr-code/types').ImageSettings>;
    customStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    tag: import('vue').PropType<import('../ele-qr-code/types').QrCodeTag>;
}>> & Readonly<{
    onDone?: (() => any) | undefined;
}>, {
    margin: number;
    size: number;
    level: import('../ele-qr-code/types').Level;
    bgColor: string;
    fgColor: string;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
