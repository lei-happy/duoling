import { UserComponent } from '../ele-app/types';

/**
 * 预设常用布局
 */
export interface PredefinedLayout {
    /** 布局名称 */
    name: string;
    /** 缩略图 */
    cover: UserComponent;
    /** 布局配置 */
    config: Record<string, any>;
    /** 非圆角主题下需要调整的布局配置 */
    traditionalThemeConfig?: Record<string, any>;
}
/**
 * 主题皮肤配置
 */
export interface SkinConfig {
    /** 主题皮肤名称 */
    name?: string;
    /** 主题皮肤缩略图 */
    cover?: string;
    /** 自定义主题皮肤基于的默认主题皮肤名称 */
    skinName?: string;
    /** 主题色 */
    color?: string;
    /** 背景图片 */
    wallpaper?: string;
    /** 背景蒙层 */
    maskColor?: string;
    /** 顶栏背景 */
    headerBg?: string;
    /** 侧栏背景 */
    sidebarBg?: string;
    /** 卡片背景 */
    cardBg?: string;
    /** 弹层背景 */
    overlayBg?: string;
    /** 弹层背景蒙层 */
    overlayMaskColor?: string;
    /** 暗黑主题配置 */
    darkConfig: Omit<SkinConfig, 'name' | 'darkConfig' | 'layouts'>;
    /** 主题样式 */
    themeCss?: string;
    /** 主题类名 */
    themeClass?: string;
    /** 预设常用布局 */
    layouts?: PredefinedLayout[];
}
/**
 * 判断是否是颜色值
 * @param value 颜色
 */
export declare function isColorValue(value?: string): boolean;
/**
 * 切换主题色
 * @param color 颜色值
 * @param dark 是否暗黑模式
 * @param isTransparent 是否是皮肤主题
 * @param themeEl 主题节点
 * @param themeSelector 主题变量选择器
 * @param darkClass 暗黑主题节点类名
 * @param darkSelector 暗黑主题变量选择器
 */
export declare function changeColor(color?: string | null, dark?: boolean, isTransparent?: boolean, themeEl?: HTMLElement, themeSelector?: string, darkClass?: string, darkSelector?: string): void;
/**
 * 切换主题皮肤
 * @param skinConfig 主题皮肤配置
 * @param dark 是否暗黑模式
 * @param themeEl 主题节点
 * @param themeSelector 主题变量选择器
 * @param themeClass 主题节点类名
 */
export declare function changeSkin(skinConfig?: SkinConfig | null, dark?: boolean, themeEl?: HTMLElement, themeSelector?: string, themeClass?: string): void;
