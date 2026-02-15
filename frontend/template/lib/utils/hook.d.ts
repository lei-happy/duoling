import { Ref, InjectionKey, EmitsOptions, EmitsToProps } from 'vue';
import { EmitMethods } from '../ele-app/types';

/**
 * useTimer 返回结果
 */
export type UseTimerResult = [
    (callback?: () => void, timeout?: number) => void,
    () => void,
    Ref<boolean>
];
/**
 * 定时器
 * @param ms 等待时间
 * @param cb 执行方法
 */
export declare function useTimer(ms?: number | (() => number), cb?: () => void): UseTimerResult;
/**
 * useMediaQuery 返回结果
 */
export type UseMediaQueryResult = [MediaQueryList, () => void, () => void];
/**
 * 媒体查询
 * @param query 媒体查询字符串
 * @param onChange 改变回调
 */
export declare function useMediaQuery(query: string, onChange?: () => void): UseMediaQueryResult;
/**
 * 移动端小屏幕媒体查询
 */
export declare const mobileMediaQuery = "(max-width: 767.99px)";
/**
 * useMobile 返回结果
 */
export type UseMobileResult = [Ref<boolean>, () => void, () => void];
/**
 * 获取是否是移动端小屏幕
 * @param onChange 值改变回调
 */
export declare function useMobile(onChange?: (isMobile: boolean) => void): UseMobileResult;
/**
 * useMobileDevice 返回结果
 */
export type UseMobileDeviceResult = [Ref<boolean>, () => void, () => void];
/**
 * 获取是否是移动端触摸设备
 * @param onChange 值改变回调
 */
export declare function useMobileDevice(onChange?: (isMobile: boolean) => void): UseMobileDeviceResult;
/**
 * 折叠展开动画
 */
export declare function useCollapseAnim(): {
    handleBeforeEnter: (el: HTMLElement) => void;
    handleEnter: (el: HTMLElement) => void;
    handleAfterEnter: (el: HTMLElement) => void;
    handleBeforeLeave: (el: HTMLElement) => void;
    handleLeave: (el: HTMLElement) => void;
    handleAfterLeave: (el: HTMLElement) => void;
};
/**
 * 弹窗挂载容器
 */
export declare const modalItemContextKey: InjectionKey<Record<string, any>>;
/**
 * 鼠标滚轮事件回调方法参数
 */
export interface UseMousewheelCallbackParam {
    /** 事件对象 */
    e: MouseEvent;
    /** 方向 */
    direction: 'up' | 'down';
}
/**
 * 鼠标滚轮事件
 * @param cb 回调
 */
export declare function useMousewheel(cb?: (p: UseMousewheelCallbackParam) => void): {
    handleMousewheel: (e: MouseEvent) => void;
    handleFirefoxMousewheel: (e: MouseEvent) => void;
    bindMousewheel: (el: HTMLElement) => void;
    unbindMousewheel: (el: HTMLElement) => void;
};
/**
 * 触摸事件回调参数
 */
export interface UseTouchEventCallbackParam<T> {
    /** 事件对象 */
    e: T;
    /** 开始横向位置 */
    startX: number | null;
    /** 开始纵向位置 */
    startY: number | null;
    /** 横向移动距离 */
    distanceX?: number | null;
    /** 纵向移动距离 */
    distanceY?: number | null;
}
/**
 * 触摸事件参数
 */
export interface UseTouchEventOption<T> {
    /** 触摸开始的回调 */
    start?: (param: UseTouchEventCallbackParam<T>) => void;
    /** 触摸移动的回调 */
    move?: (param: UseTouchEventCallbackParam<T>) => void;
    /** 触摸结束的回调 */
    end?: (param: UseTouchEventCallbackParam<T>) => void;
    /** touchstart 事件参数 */
    touchstartOptions?: any;
    /** touchmove 事件参数 */
    touchmoveOptions?: any;
}
/**
 * 触摸事件
 * @param option 参数
 */
export declare function useTouchEvent(option?: UseTouchEventOption<TouchEvent>): {
    handleTouchStart: (e: TouchEvent) => void;
    handleTouchMove: (e: TouchEvent) => void;
    handleTouchEnd: (e: TouchEvent) => void;
    bindTouchEvent: (el: HTMLElement) => void;
    unbindTouchEvent: (el: HTMLElement) => void;
};
/**
 * 移动事件对象
 */
export type MoveEvent = MouseEvent | TouchEvent;
/**
 * 鼠标移动事件或触摸移动事件
 * @param option 参数
 */
export declare function useMoveEvent(option?: UseTouchEventOption<MoveEvent>): {
    handleMousedown: (e: MouseEvent) => void;
    handleTouchstart: (e: TouchEvent) => void;
};
/**
 * useComponentEvents 返回结果
 */
export interface UseComponentEventsResult<T extends EmitsOptions> {
    emitMethods: EmitMethods<T>;
    emitProps: Required<EmitsToProps<T>>;
}
/**
 * 二次封装组件事件处理 hook
 */
export declare function useComponentEvents<T extends EmitsOptions>(events: T, emit: any): UseComponentEventsResult<T>;
/**
 * 二次封装组件导出处理 hook
 */
export declare function useComponentExpose<T extends {}, M extends keyof T, R extends keyof T>(componentRef: Ref<T | null>, methodNames: M[], refNames: R[]): Pick<T, M> & Record<R, Ref<T[R], T[R]>>;
/**
 * 组件插槽传递处理
 */
export declare function useContentSlot(): {
    customProps: Ref<any, any>;
    LoadingSpinner: import('vue').DefineComponent<import('vue').ExtractPropTypes<{
        width: {
            type: NumberConstructor;
            default: number;
        };
        height: {
            type: NumberConstructor;
            default: number;
        };
        rotate: {
            type: NumberConstructor;
            default: number;
        };
        gapX: {
            type: NumberConstructor;
            default: number;
        };
        gapY: {
            type: NumberConstructor;
            default: number;
        };
        lineGap: {
            type: NumberConstructor;
            default: number;
        };
        font: {
            type: import('vue').PropType<Required<import('../ele-watermark/types').WatermarkFont>>;
            required: true;
        };
        contents: {
            type: import('vue').PropType<string[]>;
            required: true;
        };
        image: StringConstructor;
        offsetX: {
            type: NumberConstructor;
            default: number;
        };
        offsetY: {
            type: NumberConstructor;
            default: number;
        };
        commonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    }>, {}, {}, {}, {}, import('vue').ComponentOptionsMixin, import('vue').ComponentOptionsMixin, {}, string, import('vue').PublicProps, Readonly<import('vue').ExtractPropTypes<{
        width: {
            type: NumberConstructor;
            default: number;
        };
        height: {
            type: NumberConstructor;
            default: number;
        };
        rotate: {
            type: NumberConstructor;
            default: number;
        };
        gapX: {
            type: NumberConstructor;
            default: number;
        };
        gapY: {
            type: NumberConstructor;
            default: number;
        };
        lineGap: {
            type: NumberConstructor;
            default: number;
        };
        font: {
            type: import('vue').PropType<Required<import('../ele-watermark/types').WatermarkFont>>;
            required: true;
        };
        contents: {
            type: import('vue').PropType<string[]>;
            required: true;
        };
        image: StringConstructor;
        offsetX: {
            type: NumberConstructor;
            default: number;
        };
        offsetY: {
            type: NumberConstructor;
            default: number;
        };
        commonStyle: import('vue').PropType<import('../ele-app/types').StyleValue>;
    }>> & Readonly<{}>, {
        width: number;
        height: number;
        rotate: number;
        gapX: number;
        gapY: number;
        lineGap: number;
        offsetX: number;
        offsetY: number;
    }, {}, {}, {}, string, import('vue').ComponentProvideOptions, true, {}, any>;
    slotProps: Record<string, any>;
    show: import('vue').ComputedRef<any>;
    to: import('vue').ComputedRef<HTMLElement | "body">;
};
/**
 * 监听节点宽高改变参数
 */
export interface UseResizeObserverOption {
    /** 获取要观测的节点方法 */
    getEl: () => HTMLElement | null | undefined;
    /** 宽度改变事件 */
    onWidthChange?: (width: number) => void;
    /** 高度改变事件 */
    onHeightChange?: (height: number) => void;
    /** 挂载时立即更新尺寸延迟 */
    mountedUpdateDelay?: number;
    /** 失活又激活时立即更新尺寸延迟 */
    activatedUpdateDelay?: number;
}
/**
 * 监听节点宽高改变
 * @param option 参数
 */
export declare function useResizeObserver(option: UseResizeObserverOption): readonly [Ref<number, number>, Ref<number, number>, () => void];
/**
 * 窗口事件监听
 * @param event 事件
 * @param listener 回调
 */
export declare function useWindowListener(event: string | EventListenerOrEventListenerObject, listener?: EventListenerOrEventListenerObject): void;
/**
 * 高级选项数据 hook
 */
export declare function useProOptions<T extends Record<string, any>>(props: Record<string, any>, name?: string): {
    optionData: Ref<T[], T[]>;
    reloadOptions: (params?: any) => void;
};
/**
 * 重置组件表单验证
 */
export declare function useFormItemRest(): void;
