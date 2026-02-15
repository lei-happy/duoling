import { ElStepInstance } from '../ele-app/el';
import { StepItem } from './types';

declare function __VLS_template(): Partial<Record<string, (_: {
    index: number;
    item: StepItem;
}) => any>>;
declare const __VLS_component: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
    items: import('vue').PropType<StepItem[] | import('./types').StepItemsFunction>;
    type: import('vue').PropType<import('./types').StepType>;
    space: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    active: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    direction: {
        readonly type: import('vue').PropType<"horizontal" | "vertical">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "horizontal";
    };
    alignCenter: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    simple: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    finishStatus: {
        readonly type: import('vue').PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "finish";
    };
    processStatus: {
        readonly type: import('vue').PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "process";
    };
}>, {
    reloadOptions: (params?: any) => void;
    stepsRef: import('vue').Ref<ElStepInstance, ElStepInstance>;
}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
    items: import('vue').PropType<StepItem[] | import('./types').StepItemsFunction>;
    type: import('vue').PropType<import('./types').StepType>;
    space: {
        readonly type: import('vue').PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    active: {
        readonly type: import('vue').PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    direction: {
        readonly type: import('vue').PropType<"horizontal" | "vertical">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "horizontal";
    };
    alignCenter: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    simple: {
        readonly type: import('vue').PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    finishStatus: {
        readonly type: import('vue').PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "finish";
    };
    processStatus: {
        readonly type: import('vue').PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "process";
    };
}>> & Readonly<{}>, {
    direction: "horizontal" | "vertical";
    space: string | number;
    active: number;
    finishStatus: "error" | "success" | "wait" | "finish" | "process";
    processStatus: "error" | "success" | "wait" | "finish" | "process";
}, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
declare const _default: __VLS_WithTemplateSlots<typeof __VLS_component, ReturnType<typeof __VLS_template>>;
export default _default;
type __VLS_WithTemplateSlots<T, S> = T & {
    new (): {
        $slots: S;
    };
};
