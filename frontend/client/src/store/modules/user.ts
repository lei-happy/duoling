import { defineStore } from 'pinia';
import type { BadgeProps } from 'element-plus';
import { toTree, mapTree } from 'ele-admin-plus';
import type { MenuItem } from 'ele-admin-plus/es/ele-pro-layout/types';
import type { UserMenuResult } from '@/utils/menu-util';
import { formatUserMenu } from '@/utils/menu-util';
import { isShowModuleOverviewEnabled } from '@/utils/workplace-config';
import defaultAvatarUrl from '@/assets/avatar.png';
import type { User } from '@/api/system/user/model';
import { resolveUploadUrl } from '@/utils/upload-url';
import { getUserInfo, getMenuVersion } from '@/api/layout';

/** 模块级缓存：上次检查菜单版本戳的时间戳，用于节流避免频繁请求 */
let _menuVersionCheckedAt = 0;

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
    roles: [] as (string | undefined)[] | null | undefined,
    /**
     * 当前菜单版本戳（来自 /auth/user-info 的 menuVersion）
     * 与 /auth/menu-version 比对，不一致时需重新拉取菜单
     */
    menuVersion: null as number | null,
    /** 当前租户已启用的产品功能码（仅 client 端有值），用于顶栏全局入口的可见性判断 */
    features: [] as string[]
  }),
  getters: {
    /** 是否是企业管理员 */
    isAdmin(): boolean {
      return this.info?.userType === 1;
    },
    /** 判断当前租户是否启用某个 feature_code */
    hasFeature(): (code: string) => boolean {
      return (code: string) => (this.features ?? []).includes(code);
    },
    /** 当前生效的产品版本编码（lite/basic/...） */
    versionCode(): string | undefined {
      return this.info?.versionCode ?? undefined;
    },
    /** 是否为轻量版（承运商邀请激活的 lite 租户） */
    isLite(): boolean {
      return this.info?.versionCode === 'lite';
    },
    /** 系统显示名称：优先自定义名称 > 企业名称 > 环境变量默认值 */
    displayName(): string {
      return (
        this.info?.systemName ||
        this.info?.tenantName ||
        import.meta.env.VITE_APP_NAME ||
        ''
      );
    }
  },
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
        const workplaceConfig = userInfo.workplaceConfig;
        const userMenuResult: UserMenuResult = formatUserMenu(userMenu, {
          isModuleOverviewEnabled: (moduleKey) =>
            isShowModuleOverviewEnabled(workplaceConfig, moduleKey)
        });
        // 租户端已关闭自定义主题功能，主题固定为品牌配置，
        // 不再从服务端恢复主题外观自定义
        // 数据更新到状态管理中
        this.setInfo(userInfo);
        this.setAuthorities(
          userInfo?.authorities?.map?.((d) => d.authority)?.filter?.((a) => !!a)
        );
        this.setRoles(userInfo?.roles?.map?.((d) => d.roleCode));
        this.setMenus(userMenuResult.menus);
        this.setMenuVersion(
          typeof userInfo.menuVersion === 'number' ? userInfo.menuVersion : null
        );
        this.setFeatures(
          Array.isArray(userInfo.features) ? userInfo.features : []
        );
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
        const avatar = resolveUploadUrl(data?.avatar) || defaultAvatarUrl;
        this.info = { ...data, avatar };
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
     * 更新菜单版本戳
     */
    setMenuVersion(v: number | null) {
      this.menuVersion = v;
    },
    /**
     * 更新租户功能码列表
     */
    setFeatures(features: string[]) {
      this.features = features ?? [];
    },
    /**
     * 检查菜单版本是否过期（轻量接口，内置节流）
     * @returns 若已过期返回 true（前端应清空菜单并重新拉取）
     */
    async checkMenuOutdated(throttleMs = 5000): Promise<boolean> {
      const now = Date.now();
      const last = _menuVersionCheckedAt;
      if (now - last < throttleMs) {
        return false;
      }
      _menuVersionCheckedAt = now;
      try {
        const remoteVersion = await getMenuVersion();
        const local = this.menuVersion ?? 0;
        if (remoteVersion !== local) {
          console.info(
            `[menu-version] 菜单版本变化 local=${local} → remote=${remoteVersion}，需重新拉取菜单`
          );
          return true;
        }
        return false;
      } catch (e) {
        console.warn('[menu-version] 版本戳查询失败，忽略本次检查', e);
        return false;
      }
    },
    /**
     * 清空状态数据
     */
    clearData() {
      this.setInfo(null);
      this.setMenus(null);
      this.setAuthorities(null);
      this.setRoles(null);
      this.setMenuVersion(null);
      this.setFeatures([]);
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
