import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { EleMessage } from 'ele-admin-plus';
import { getToken, setToken, removeToken, setRefreshToken, removeRefreshToken } from '@/utils/token-util';
import { goLogin } from '@/utils/common';
import { usePageTab } from '@/utils/use-page-tab';
import { useUserStore } from '@/store/modules/user';
import { login as loginApi, smsLogin as smsLoginApi, logout as logoutApi } from '@/api/login';
import type { LoginParam } from '@/api/login/model';
import { HOME_PATH, LAYOUT_PATH } from '@/config/setting';

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
   * 登录成功后跳转：使用硬跳转重新加载页面，
   * 避免动态路由注入与路由守卫的时序竞态导致用户停留在登录页。
   */
  const redirectAfterLogin = () => {
    const from = route.query.from;
    const fromPath = [from].flat()[0];
    const target = fromPath
      ? decodeURIComponent(fromPath)
      : (HOME_PATH || LAYOUT_PATH);
    window.location.replace(target);
  };

  /**
   * 登录
   * @param data 表单数据
   */
  const login = async (data: LoginParam) => {
    const result = await loginApi(data);
    const token = result.data?.access_token;
    if (!token) {
      return Promise.reject(new Error(result.message));
    }
    EleMessage.success({ message: '登录成功', plain: true });
    setToken(token, data.remember);
    setRefreshToken(result.data?.refresh_token, data.remember);
    clearData();
    return new Promise((resolve) => {
      setTimeout(() => {
        redirectAfterLogin();
        resolve(undefined);
      }, 500);
    });
  };

  /**
   * 验证码登录
   */
  const smsLogin = async (phone: string, code: string, remember: boolean = true) => {
    const result = await smsLoginApi(phone, code);
    const token = result.data?.access_token;
    if (!token) {
      return Promise.reject(new Error(result.message || '登录失败'));
    }
    EleMessage.success({ message: '登录成功', plain: true });
    setToken(token, remember);
    setRefreshToken(result.data?.refresh_token, remember);
    clearData();
    return new Promise((resolve) => {
      setTimeout(() => {
        redirectAfterLogin();
        resolve(undefined);
      }, 500);
    });
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
    redirectAfterLogin,
    showLogoutConfirm
  };
}
