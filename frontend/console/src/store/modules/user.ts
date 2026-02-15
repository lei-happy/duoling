import { defineStore } from 'pinia';
import type { BadgeProps } from 'element-plus';
import { toTree, mapTree } from 'ele-admin-plus';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import type { UserMenuResult } from '@/utils/menu-util';
import { formatUserMenu } from '@/utils/menu-util';
import defaultAvatarUrl from '@/assets/avatar.png';
import type { User } from '@/api/system/user/model';
import { getUserInfo } from '@/api/layout';
import { useThemeStore } from './theme';
import { cacheSetting } from '@/utils/theme-util';

/**
 * 登录用户状态管理
 */
export const useUserStore = defineStore('user', {
  state: () => ({
    /** 当前登录用户的信息 */
    info: null as User | null | undefined,
    /** 当前登录用户的菜单数据 */
    menus: null as MenuItem[] | null | undefined,
    /** 当前登录用户的按钮权限数据 */
    authorities: [] as (string | undefined)[] | null | undefined,
    /** 当前登录用户的角色权限数据 */
    roles: [] as (string | undefined)[] | null | undefined
  }),
  actions: {
    /**
     * 请求登录用户的个人信息/权限/角色/菜单
     * @param toRoute 路由守卫中要进入的路由
     */
    async fetchUserInfo(toRoute: any): Promise<UserMenuResult> {
      try {
        // 请求用户信息接口
        const userInfo = await getUserInfo(toRoute);
        // 处理菜单数据格式
        const userMenu = toTree({
          data: userInfo.authorities?.filter?.((d) => d.menuType !== 1),
          idField: 'menuId',
          parentIdField: 'parentId'
        });
        const userMenuResult: UserMenuResult = formatUserMenu(userMenu);
        // 从服务端恢复主题配置（服务端优先于本地缓存）
        if (userInfo.themeConfig && Object.keys(userInfo.themeConfig).length > 0) {
          const themeStore = useThemeStore();
          const serverConfig = userInfo.themeConfig;
          // 将服务端配置写入 localStorage 缓存
          cacheSetting(serverConfig);
          // 同步到 themeStore 状态（排除 skinConfig，它有特殊处理逻辑）
          Object.keys(serverConfig).forEach((key) => {
            if (key !== 'skinConfig' && typeof serverConfig[key] !== 'undefined') {
              (themeStore as any)[key] = serverConfig[key];
            }
          });
          // 恢复主题视觉效果
          themeStore.recoverTheme();
        }
        // 数据更新到状态管理中
        this.setInfo(userInfo);
        this.setAuthorities(
          userInfo?.authorities?.map?.((d) => d.authority)?.filter?.((a) => !!a)
        );
        this.setRoles(userInfo?.roles?.map?.((d) => d.roleCode));
        this.setMenus(userMenuResult.menus);
        return userMenuResult;
      } catch (e) {
        console.error(e);
      }
      return {};
    },
    /**
     * 更新用户信息
     */
    setInfo(data?: User | null) {
      if (data == null) {
        this.info = null;
      } else {
        this.info = { ...data, avatar: data?.avatar || defaultAvatarUrl };
      }
    },
    /**
     * 更新菜单数据
     */
    setMenus(menus?: MenuItem[] | null) {
      this.menus = menus;
    },
    /**
     * 更新按钮权限数据
     */
    setAuthorities(authorities?: (string | undefined)[] | null) {
      this.authorities = authorities;
    },
    /**
     * 更新角色权限数据
     */
    setRoles(roles?: (string | undefined)[] | null) {
      this.roles = roles;
    },
    /**
     * 清空状态数据
     */
    clearData() {
      this.setInfo(null);
      this.setMenus(null);
      this.setAuthorities(null);
      this.setRoles(null);
    },
    /**
     * 更新菜单的徽章
     * @param path 菜单地址
     * @param value 徽章值
     * @param type 徽章类型
     */
    setMenuBadge(
      path: string,
      value?: number | string | null,
      type?: BadgeProps['type']
    ) {
      this.menus = mapTree(this.menus, (m) => {
        if (path === m.path) {
          const meta = m.meta || {};
          return {
            ...m,
            meta: {
              ...meta,
              props: {
                ...meta.props,
                badge: value == null ? void 0 : { value, type }
              }
            }
          };
        }
        return m;
      });
    }
  }
});
