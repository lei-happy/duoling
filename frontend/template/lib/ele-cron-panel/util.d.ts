/**
 * 任意* 范围 间隔 指定 通用封装
 * @param minValue 最小值
 * @param maxValue 最大值
 * @param defaultType 默认类型
 */
export declare function useCron(minValue: number, maxValue: number, defaultType?: string): {
    type: import('vue').Ref<string, string>;
    start: import('vue').Ref<number, number>;
    end: import('vue').Ref<number, number>;
    endMin: import('vue').ComputedRef<number>;
    intervalStart: import('vue').Ref<number, number>;
    intervalStep: import('vue').Ref<number, number>;
    intervalStepMax: import('vue').ComputedRef<number>;
    selections: import('vue').Ref<number[], number[]>;
    getValue: () => string | undefined;
    parseValue: (str?: string) => void;
};
/**
 * 计算最近 5 次运行时间
 * 代码来源: https://gitee.com/y_project/RuoYi-Vue/blob/master/ruoyi-ui/src/components/Crontab/result.vue
 * @param cron Cron 表达式
 */
export declare function getResultItems(cron: string | undefined, noDataText: string, noMoreText: string): string[];
