import { mapTree, isExternalLink } from 'ele-admin-plus';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import type { Menu } from '@/api/system/menu/model';
/** 直接指定菜单数据 */
const USER_MENUS: Menu[] | null = null;

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
 * 处理用户菜单数据
 * @param userMenu 用户菜单
 */
export function formatUserMenu(userMenu: Menu[]): UserMenuResult {
  return formatMenus(USER_MENUS ?? userMenu);
}

export interface UserMenuResult {
  /** 菜单数据(EleProLayout 所需要的格式) */
  menus?: MenuItem[];
  /** 主页地址 */
  homePath?: string;
  /** 主页标题 */
  homeTitle?: string;
}
