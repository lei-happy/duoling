/** 登录页面的路由地址 */
export const LOGIN_PATH = '/login';

/** 不需要登录的路由地址：
 *  - '/invite-landing/*' 承运商邀请着陆页（路径 B 激活入口）
 *  - '/upgrade-plans'    版本对比/升级方案页（lite 用户横幅按钮 + 公开分享）
 */
export const WHITE_LIST: string[] = [
  LOGIN_PATH,
  '/forget',
  '/invite-landing/*',
  '/upgrade-plans'
];

/** 首页路径, 为空则取第一个菜单的地址 */
export const HOME_PATH: string | undefined = void 0;

/** 外层布局的路由地址 */
export const LAYOUT_PATH = '/';

/** 刷新路由的路由地址 */
export const REDIRECT_PATH = '/redirect';

/** token本地缓存的名称 */
export const TOKEN_CACHE_NAME = 'token';

/** refresh token本地缓存的名称 */
export const REFRESH_TOKEN_CACHE_NAME = 'refresh_token';

/** 主题配置本地缓存的名称 */
export const THEME_CACHE_NAME = 'theme';

/** token请求头名称 */
export const TOKEN_HEADER_NAME = 'Authorization';

/** i18n本地缓存的名称 */
export const I18N_CACHE_NAME = 'i18n-lang';
