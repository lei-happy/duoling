import { Ref, InjectionKey } from 'vue';
import { modalItemContextKey as injectContext } from '../utils/hook';
import { GlobalProvide, UseLocaleResult, LocaleProps, EleLocale } from './types';

export { injectContext };
/**
 * 全局配置键名
 */
export declare const CONFIG_KEY: InjectionKey<GlobalProvide>;
/**
 * 获取全局配置
 */
export declare function useReceiver(): GlobalProvide;
/**
 * 获取全局属性
 */
export declare function useGlobalProps<T>(name: string): Ref<T>;
/**
 * 获取国际化
 */
export declare function useLocale<K extends keyof EleLocale>(name?: K, props?: LocaleProps<EleLocale[K]>): UseLocaleResult<EleLocale[K]>;
export declare const configValues: any;
