/**
 * 品牌口径集中配置。
 *
 * 品牌层级：法律主体「北京朵灵科技有限公司」→ 企业品牌「朵灵科技」
 * → 母品牌「朵灵」→ 产品线「朵灵·企云」（租户端）/「朵灵·司机」（司机端）。
 *
 * 官网所有出现品牌名称、口号、联系方式的地方都从这里取，改名时只改这一处。
 */

export const BRAND = {
  /** 产品名（官网主推） */
  product: '朵灵·企云',
  /** 导航角标，两个字母 */
  mark: 'DL',
  /** 产品一句话定位，跟在角标后面做副标题 */
  tagline: '轿运企业综合操作系统',
  /** 司机端产品名 */
  driverProduct: '朵灵·司机',
  /** 企业传播名称 */
  company: '朵灵科技',
  /** 法律主体，用于页脚版权 */
  legalEntity: '北京朵灵科技有限公司',
  /** 页脚品牌区的长句口号 */
  slogan:
    '让每一公里都不白跑。朵灵·企云面向轿运行业（汽车物流），把计划到结算收进一套企业经营系统。',
  /** 版权年份 */
  copyrightYear: 2026
} as const;

/** 租户端登录地址，生产环境由 .env.production 注入 */
export const CLIENT_URL: string =
  import.meta.env.VITE_CLIENT_URL || 'http://localhost:5174';

export const LOGIN_URL = `${CLIENT_URL}/login`;

/**
 * 待市场/商务确认的占位信息。
 * 页面上用 `.pending` 虚线标注，确认后替换这里即可。
 */
export const PENDING_INFO = {
  /** 400 服务电话 */
  hotline: '400-000-0000',
  /** ICP 备案号 */
  icp: '京ICP备00000000号'
} as const;
