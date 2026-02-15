import { PropType, ExtractPropTypes } from 'vue';
import { StepType, StepItem, StepItemsFunction } from './types';

/**
 * 属性
 */
export declare const stepsProps: {
    /** 步骤条数据 */
    items: PropType<StepItem[] | StepItemsFunction>;
    /** 类型 */
    type: PropType<StepType>;
    space: {
        readonly type: PropType<string | number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "";
    };
    active: {
        readonly type: PropType<number>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: 0;
    };
    direction: {
        readonly type: PropType<"horizontal" | "vertical">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "horizontal";
    };
    alignCenter: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    simple: {
        readonly type: PropType<boolean>;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    };
    finishStatus: {
        readonly type: PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "finish";
    };
    processStatus: {
        readonly type: PropType<"error" | "success" | "wait" | "finish" | "process">;
        readonly required: false;
        readonly validator: ((val: unknown) => boolean) | undefined;
        __epPropKey: true;
    } & {
        readonly default: "process";
    };
};
export type StepsProps = ExtractPropTypes<typeof stepsProps>;
