import { InjectionKey } from 'vue';
import { ElePopconfirmInstance, ElePopconfirmPropsAndEmits } from '../ele-app/plus';
import { PopconfirmProvider } from './types';

/**
 * 气泡确认框注入键名
 */
export declare const POPCONFIRM_KEY: InjectionKey<PopconfirmProvider>;
/**
 * 提供气泡确认框操作给子组件
 */
export declare function usePopconfirmProvider(): {
    popconfirmRef: import('vue').Ref<ElePopconfirmInstance, ElePopconfirmInstance>;
    popconfirmVirtualRef: import('vue').ShallowRef<any, any>;
    popconfirmProps: import('vue').ShallowRef<Partial<import('../ele-popconfirm/props').PopconfirmPropsAndEmits>, Partial<import('../ele-popconfirm/props').PopconfirmPropsAndEmits>>;
    openPopconfirm: (triggerEl: any, props?: ElePopconfirmPropsAndEmits) => void;
};
/**
 * 气泡确认框操作
 */
export declare function usePopconfirm(): PopconfirmProvider;
