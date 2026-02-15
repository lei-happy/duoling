import { ComponentResolver } from 'unplugin-vue-components/types';

/**
 * 参数类型
 */
export interface EleAdminResolverOptions {
    /** 包路径 */
    path?: string | '' | '/es' | '/lib' | '/es/core' | '/lib/core';
    /** 排除的组件名称 */
    exclude?: string[];
    /** 是否导入样式 */
    importStyle?: boolean | 'css' | 'sass';
}
/**
 * 按需加载插件
 * @param options 参数
 */
export declare function EleAdminResolver(options?: EleAdminResolverOptions): ComponentResolver;
