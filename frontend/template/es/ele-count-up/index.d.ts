import { CountUp } from 'countup.js';

declare const _default: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    delay: {
        type: NumberConstructor;
        default: number;
    };
    endVal: {
        type: NumberConstructor;
        required: boolean;
    };
    options: import('vue').PropType<import('countup.js').CountUpOptions>;
}>, {
    printValue: (value: number) => void;
    start: (callback?: (args?: any) => any) => void;
    pauseResume: () => void;
    reset: () => void;
    update: (newEndVal?: string | number) => void;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {
    ready: (_instance?: CountUp | null | undefined) => void;
}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    delay: {
        type: NumberConstructor;
        default: number;
    };
    endVal: {
        type: NumberConstructor;
        required: boolean;
    };
    options: import('vue').PropType<import('countup.js').CountUpOptions>;
}>> & Readonly<{
    onReady?: ((_instance?: CountUp | null | undefined) => any) | undefined;
}>, {
    delay: number;
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
export default _default;
