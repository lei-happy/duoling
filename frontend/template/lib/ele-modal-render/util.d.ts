import { InjectionKey } from 'vue';
import { ModalUtilProvider, ModalHolderProvider, UseModalRenderResult } from './types';

/**
 * 弹窗渲染器容器注入键名
 */
export declare const MODAL_UTIL_KEY: InjectionKey<ModalUtilProvider>;
/**
 * 直接父级的弹窗渲染器注入键名
 */
export declare const MODAL_HOLDER_KEY: InjectionKey<ModalHolderProvider>;
/**
 * 弹窗渲染器数据操作
 */
export declare function useModalRender(): UseModalRenderResult;
/**
 * 提供弹窗操作方法给后代组件
 */
export declare function useModalRenderProvider(): UseModalRenderResult;
