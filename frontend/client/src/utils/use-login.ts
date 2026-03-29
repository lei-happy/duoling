import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { EleMessage } from 'ele-admin-plus';
import { getToken, setToken, removeToken, setRefreshToken, removeRefreshToken } from '@/utils/token-util';
import { goLogin } from '@/utils/common';
import { usePageTab } from '@/utils/use-page-tab';
import { useUserStore } from '@/store/modules/user';
import { login as loginApi, smsLogin as smsLoginApi, logout as logoutApi } from '@/api/login';
import type { LoginParam, LoginResult, TenantOption } from '@/api/login/model';

/** 登录结果类型 */
export interface LoginActionResult {
  /** 登录是否成功（已获取 token） */
  success: boolean;
  /** 是否需要选择企业 */
  needSelectTenant?: boolean;
  /** 可选企业列表 */
  tenants?: TenantOption[];
  /** 是否需要强制修改密码 */
  forceChangePwd?: boolean;
}

/**
 * 登录操作
 */
export function useLogin() {
  const { t } = useI18n();
  const route = useRoute();
  const { cleanPageTabs, goHomeRoute } = usePageTab();
  const userStore = useUserStore();

  /**
   * 清空登录状态数据
   */
  const clearData = () => {
    cleanPageTabs();
    userStore.clearData();
  };

  /**
   * 跳转到首页
   */
  const goHome = () => {
    const from = route.query.from;
    goHomeRoute([from].flat()[0]);
  };

  /**
   * 登录
   * @param data 表单数据
   * @returns LoginActionResult 供登录页面处理多企业选择和强制改密
   */
  const login = async (data: LoginParam): Promise<LoginActionResult> => {
    const result = await loginApi(data);
    const loginData = result.data as LoginResult | undefined;

    // 多企业选择场景
    if (loginData?.needSelectTenant && loginData.tenants?.length) {
      return {
        success: false,
        needSelectTenant: true,
        tenants: loginData.tenants
      };
    }

    // 正常登录
    const token = loginData?.access_token;
    if (!token) {
      return Promise.reject(new Error(result.message || '登录失败'));
    }

    EleMessage.success({ message: result.message, plain: true });
    setToken(token, data.remember);
    setRefreshToken(loginData?.refresh_token, data.remember);
    clearData();

    // 检查是否需要强制修改密码
    const forceChangePwd = loginData?.user?.force_change_pwd === 1;
    if (forceChangePwd) {
      return { success: true, forceChangePwd: true };
    }

    // 直接跳转首页
    goHome();
    return { success: true };
  };

  /**
   * 验证码登录
   */
  const smsLogin = async (
    phone: string,
    code: string,
    tenantCode?: string,
    remember: boolean = true
  ): Promise<LoginActionResult> => {
    const result = await smsLoginApi(phone, code, tenantCode);
    const loginData = result.data as LoginResult | undefined;

    if (loginData?.needSelectTenant && loginData.tenants?.length) {
      return {
        success: false,
        needSelectTenant: true,
        tenants: loginData.tenants
      };
    }

    const token = loginData?.access_token;
    if (!token) {
      return Promise.reject(new Error(result.message || '登录失败'));
    }

    EleMessage.success({ message: result.message, plain: true });
    setToken(token, remember);
    setRefreshToken(loginData?.refresh_token, remember);
    clearData();

    const forceChangePwd = loginData?.user?.force_change_pwd === 1;
    if (forceChangePwd) {
      return { success: true, forceChangePwd: true };
    }

    goHome();
    return { success: true };
  };

  /**
   * 退出登录
   */
  const logout = async () => {
    await logoutApi();
    removeToken();
    removeRefreshToken();
    //clearData();
    goLogin(void 0, false);
  };

  /**
   * 检查登录状态
   */
  const checkLogin = async () => {
    if (!getToken()) {
      return Promise.reject(new Error());
    }
    goHome();
  };

  /**
   * 弹出退出登录确认弹窗
   */
  const showLogoutConfirm = () => {
    ElMessageBox.confirm(t('layout.logout.message'), t('layout.logout.title'), {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        logout()
          .then(() => {
            loading.close();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  return {
    login,
    smsLogin,
    logout,
    checkLogin,
    goHome,
    showLogoutConfirm
  };
}
