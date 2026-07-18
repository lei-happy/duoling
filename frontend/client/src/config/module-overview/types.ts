/**
 * 模块总览页配置类型定义
 *
 * 一套配置驱动一个一级模块的总览页，包含模块定位、工作流程、
 * 子模块卡片补充文案与常用操作等。子模块卡片主体来自用户真实菜单，
 * 配置仅做文案与图标补充，保证总览内容始终跟随权限。
 */

/** 工作流程中的单个步骤 */
export interface OverviewWorkflowStep {
  /** 步骤标题 */
  title: string;
  /** 步骤说明 */
  desc?: string;
  /** 图标名称（对应 overview-icon 图标注册表） */
  icon?: string;
  /** 点击跳转的路由地址，缺省则不可点击 */
  path?: string;
}

/** 子模块卡片的文案/图标补充（按菜单 path 匹配） */
export interface OverviewModuleCardOverride {
  /** 匹配的子菜单 path */
  path: string;
  /** 补充说明文案 */
  desc?: string;
  /** 图标名称（对应 overview-icon 图标注册表） */
  icon?: string;
}

/** 渲染到模块导航区的卡片数据 */
export interface OverviewModuleCard {
  /** 卡片标题 */
  title?: string;
  /** 说明文案 */
  desc?: string;
  /** 图标名称 */
  icon?: string;
  /** 跳转地址 */
  path: string;
}

/** 常用操作按钮 */
export interface OverviewQuickAction {
  /** 按钮文案 */
  title: string;
  /** 跳转地址 */
  path: string;
  /** 图标名称 */
  icon?: string;
  /** 是否为主按钮 */
  primary?: boolean;
}

/** 单个一级模块的总览配置 */
export interface ModuleOverviewConfig {
  /** 模块 key，等于路径去掉前导斜杠，如 operation */
  key: string;
  /** 模块名称，缺省时取菜单标题 */
  title?: string;
  /** 一句话定位 */
  positioning: string;
  /** 更完整的模块介绍 */
  description?: string;
  /** Hero 主插画地址（import 得到的 URL） */
  heroIllustration?: string;
  /** Hero 插画宽高比（如 4 表示 4:1），用于宽幅配图布局 */
  heroAspectRatio?: number;
  /** Hero 缺省插画使用的主题图标名称（无 heroIllustration 时生效） */
  heroIcon?: string;
  /** Hero 主题强调色，用于点缀（缺省用主题主色） */
  accentColor?: string;
  /** 工作流程步骤 */
  workflow?: OverviewWorkflowStep[];
  /** 子模块卡片补充配置 */
  moduleCards?: OverviewModuleCardOverride[];
  /** 常用操作按钮 */
  quickActions?: OverviewQuickAction[];
  /** 使用提示 */
  tips?: string[];
}
