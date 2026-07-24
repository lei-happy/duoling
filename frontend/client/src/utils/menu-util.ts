import { mapTree, isExternalLink } from 'ele-admin-plus';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import type { Menu } from '@/api/system/menu/model';
/** 直接指定菜单数据 */
const USER_MENUS: Menu[] | null = null;

/** 总览页共享组件地址（对应 src/views/_module-overview/index.vue） */
const OVERVIEW_COMPONENT = '/_module-overview';
/** 总览子路由的路径后缀 */
const OVERVIEW_PATH_SUFFIX = '/overview';
/**
 * 总览路径与既有业务子路由同名时的兜底后缀。
 * 例如数据洞察已存在 `/insight/overview`（运营看板），总览改用 `/insight/overview-home`，
 * 避免同名导致总览路由被业务页覆盖而不显示。
 */
const OVERVIEW_PATH_FALLBACK_SUFFIX = '/overview-home';
/** 不注入总览入口的一级模块（首页本身即工作台，无需总览） */
const OVERVIEW_EXCLUDED_PATHS = new Set<string>(['/dashboard']);

/**
 * 二级菜单图标映射：key 为二级菜单 path，value 为 src/assets/menu-icons 下的
 * SVG 文件名（不含扩展名，统一以 sub- 前缀标识）。
 *
 * 用于在不改动后端菜单数据的前提下，为所有二级菜单补齐图标；一级菜单图标则统一移除。
 */
const SUBMENU_ICON_BY_PATH: Record<string, string> = {
  // 首页
  '/dashboard/workplace': 'sub-workplace',
  // 运营调度
  '/operation/waybill': 'sub-waybill',
  '/operation/task': 'sub-task',
  '/operation/task-create': 'sub-task-create',
  '/operation/smart-stowage': 'sub-smart-stowage',
  '/operation/task-workbench': 'sub-task-workbench',
  '/operation/tracking': 'sub-tracking',
  '/operation/receipt': 'sub-receipt',
  '/operation/completed-task': 'sub-completed-task',
  // 财务结算（部分二级挂在 /operation 路径下）
  '/operation/task-finance-workbench': 'sub-fee-workbench',
  '/operation/task-finance': 'sub-fee-ledger',
  '/finance/receivable': 'sub-receivable',
  '/finance/reconciliation': 'sub-reconciliation',
  '/finance/invoice': 'sub-invoice',
  '/finance/profit': 'sub-profit',
  // 运力中心
  '/capacity/self-capacity': 'sub-self-capacity',
  '/capacity/carrier-capacity': 'sub-carrier-capacity',
  '/capacity/social-capacity': 'sub-social-capacity',
  '/capacity/compliance': 'sub-compliance',
  // 客商中心
  '/partner/customer': 'sub-customer',
  '/partner/carrier': 'sub-carrier',
  '/partner/inbound': 'sub-inbound',
  '/partner/dealer': 'sub-dealer',
  // 计费中心
  '/billing/contract': 'sub-contract',
  '/billing/route': 'sub-route',
  '/billing/cost-policy': 'sub-cost-policy',
  '/billing/carrier-contract': 'sub-carrier-contract',
  '/billing/fee-template': 'sub-fee-template',
  // 审批中心
  '/approval/pending': 'sub-approval-pending',
  '/approval/initiated': 'sub-approval-initiated',
  '/approval/history': 'sub-approval-history',
  // 数据洞察
  '/insight/cockpit': 'sub-cockpit',
  '/insight/overview': 'sub-dashboard-board',
  '/insight/report': 'sub-report',
  '/insight/prediction': 'sub-prediction',
  // 服务平台
  '/ecosystem/cargo-hall': 'sub-cargo-hall',
  '/ecosystem/capacity-hall': 'sub-capacity-hall',
  '/ecosystem/service-hall': 'sub-service-hall',
  // 日志中心
  '/log-center/operation-log': 'sub-operation-log',
  '/log-center/login-log': 'sub-login-log',
  // 企业配置
  '/enterprise/organization': 'sub-organization',
  '/enterprise/user': 'sub-staff',
  '/enterprise/role': 'sub-role-perm',
  '/enterprise/approval-config': 'sub-approval-config',
  '/enterprise/basic-data': 'sub-basic-data',
  '/enterprise/business-entity': 'sub-business-entity',
  '/enterprise/config': 'sub-sys-config',
  // 开放平台
  '/open-platform/apps': 'sub-open-apps',
  '/open-platform/capabilities': 'sub-open-capability',
  '/open-platform/docs': 'sub-open-docs',
  '/open-platform/logs': 'sub-open-logs'
};

/**
 * 菜单数据处理为 EleProLayout 所需要的格式
 * @param data 菜单数据
 * @param childField 子级的字段名称
 */
function formatMenus(data: Menu[], childField = 'children'): UserMenuResult {
  let homePath: string | undefined;
  let homeTitle: string | undefined;
  const menus = mapTree<Menu, MenuItem>(
    data,
    (item) => {
      const meta: MenuItem['meta'] =
        (typeof item.meta === 'string'
          ? JSON.parse(item.meta || '{}')
          : item.meta) || {};
      const menu: MenuItem = {
        path: item.path,
        component: item.component,
        meta: { title: item.title, icon: item.icon, hide: !!item.hide, ...meta }
      };
      const children = item[childField]
        ? item[childField].filter((d: any) => !(d.meta?.hide ?? d.hide))
        : void 0;
      if (!children?.length) {
        if (!homePath && menu.path && !isExternalLink(menu.path)) {
          homePath = menu.path;
          homeTitle = menu.meta?.title;
        }
      } else {
        const childPath = children[0].path;
        if (childPath) {
          if (!menu.component && !menu.redirect) {
            menu.redirect = childPath;
          }
          if (!menu.path) {
            menu.path = childPath.substring(0, childPath.lastIndexOf('/'));
          }
        }
      }
      if (!menu.path) {
        console.error('菜单path不能为空且要唯一:', item);
        return;
      }
      return menu;
    },
    childField
  );
  return { menus, homePath, homeTitle };
}

/**
 * 为每个一级业务模块在其子菜单最前方注入「总览」入口，并将模块默认重定向指向总览页。
 *
 * - 仅处理有子菜单、且未被排除（如首页）的可见一级模块；
 * - 总览节点全部指向同一个共享组件，页面内按 meta.overviewModule 区分模块；
 * - 幂等处理：若已存在总览节点则跳过插入，仅纠正重定向，避免重复注入。
 * @param menus 已格式化的菜单树
 */
function injectModuleOverview(menus?: MenuItem[]): MenuItem[] | undefined {
  if (!menus?.length) {
    return menus;
  }
  menus.forEach((top) => {
    const path = top.path;
    if (!path || OVERVIEW_EXCLUDED_PATHS.has(path) || isExternalLink(path)) {
      return;
    }
    if (top.meta?.hide) {
      return;
    }
    const children = top.children;
    if (!children?.length) {
      return;
    }
    const moduleKey = path.replace(/^\//, '');
    // 幂等：若已注入过总览（按 overviewModule 标识），仅纠正重定向后返回
    const injected = children.find(
      (child) => child.meta?.overviewModule === moduleKey
    );
    if (injected?.path) {
      top.redirect = injected.path;
      return;
    }
    // 与既有业务子路由同名（如 /insight/overview 运营看板）时启用兜底后缀，避免路由被覆盖
    const preferredPath = `${path}${OVERVIEW_PATH_SUFFIX}`;
    const overviewPath = children.some((child) => child.path === preferredPath)
      ? `${path}${OVERVIEW_PATH_FALLBACK_SUFFIX}`
      : preferredPath;
    children.unshift({
      path: overviewPath,
      component: OVERVIEW_COMPONENT,
      meta: {
        title: '总览',
        icon: 'overview',
        hide: false,
        overviewModule: moduleKey
      }
    });
    // 覆写模块默认重定向，使点击顶部一级菜单默认落地总览页
    top.redirect = overviewPath;
  });
  return menus;
}

/**
 * 统一处理菜单图标：
 * - 一级菜单（顶层模块）移除图标，仅保留文字；
 * - 二级菜单按 SUBMENU_ICON_BY_PATH 补齐图标，未命中的保留原有图标（如总览页的 overview）。
 *
 * 仅处理到第二层，三级及以下菜单保持原样。
 * @param menus 已格式化并注入总览的菜单树
 */
function applyMenuIconRules(menus?: MenuItem[]): MenuItem[] | undefined {
  if (!menus?.length) {
    return menus;
  }
  menus.forEach((top) => {
    top.meta = { ...(top.meta || {}), icon: void 0 };
    top.children?.forEach((child) => {
      const mapped = child.path ? SUBMENU_ICON_BY_PATH[child.path] : void 0;
      if (mapped) {
        child.meta = { ...(child.meta || {}), icon: mapped };
      }
    });
  });
  return menus;
}

/**
 * 处理用户菜单数据
 * @param userMenu 用户菜单
 */
export function formatUserMenu(userMenu: Menu[]): UserMenuResult {
  const result = formatMenus(USER_MENUS ?? userMenu);
  result.menus = injectModuleOverview(result.menus);
  result.menus = applyMenuIconRules(result.menus);
  return result;
}

export interface UserMenuResult {
  /** 菜单数据(EleProLayout 所需要的格式) */
  menus?: MenuItem[];
  /** 主页地址 */
  homePath?: string;
  /** 主页标题 */
  homeTitle?: string;
}
