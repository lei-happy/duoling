import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { EleMessage } from 'ele-admin-plus';
import { getToken, setToken, removeToken, setRefreshToken, removeRefreshToken } from '@/utils/token-util';
import { goLogin } from '@/utils/common';
import { usePageTab } from '@/utils/use-page-tab';
import { useUserStore } from '@/store/modules/user';
import { login as loginApi, logout as logoutApi } from '@/api/login';
import type { LoginParam } from '@/api/login/model';

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
   */
  const login = async (data: LoginParam) => {
    const result = await loginApi(data);
    const token = result.data?.access_token;
    if (!token) {
      return Promise.reject(new Error(result.message));
    }
    EleMessage.success({ message: result.message, plain: true });
    setToken(token, data.remember);
    setRefreshToken(result.data?.refresh_token, data.remember);
    clearData();
    goHome();
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
    logout,
    checkLogin,
    goHome,
    showLogoutConfirm
  };
}
