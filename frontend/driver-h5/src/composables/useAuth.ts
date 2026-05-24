import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useUserStore } from '@/store/user';
import { useTenantStore } from '@/store/tenant';
import { useTaskStore } from '@/store/task';
import {
  loginByPassword,
  loginBySms,
  type LoginResponseData,
  type LoginResultUnion,
  type MultiTenantData,
  type TenantOption
} from '@/api/auth';

function isMulti(data: LoginResultUnion): data is MultiTenantData {
  return Array.isArray((data as MultiTenantData).tenants);
}

export function useAuth() {
  const router = useRouter();
  const user = useUserStore();
  const tenant = useTenantStore();
  const task = useTaskStore();

  async function passwordLogin(phone: string, password: string, tenantCode?: string) {
    const data = await loginByPassword({ phone, password, tenantCode });
    return handleLoginResult(data, phone);
  }

  async function smsLogin(phone: string, code: string, tenantCode?: string) {
    const data = await loginBySms({ phone, code, tenantCode });
    return handleLoginResult(data, phone);
  }

  async function handleLoginResult(data: LoginResultUnion, phone: string) {
    if (isMulti(data)) {
      tenant.tenants.length = 0;
      tenant.tenants.push(...data.tenants);
      await router.push({ name: 'TenantSelect', query: { phone } });
      return { needSelectTenant: true, tenants: data.tenants };
    }
    user.setLoginResult(data as LoginResponseData);
    await afterLogin();
    return { needSelectTenant: false };
  }

  async function afterLogin() {
    showToast({ message: '登录成功', type: 'success', duration: 1200 });
    if (user.needForceChangePwd) {
      await router.replace({ name: 'ChangePassword' });
    } else {
      const target =
        (router.currentRoute.value.query.redirect as string | undefined) || '/home';
      await router.replace(target);
    }
  }

  async function switchTo(t: TenantOption) {
    if (user.isLoggedIn && user.currentTenantCode) {
      // 切租户：调用 switch-tenant 重签
      await tenant.switchTo(t.tenantCode);
    }
    task.clear();
    await afterLogin();
  }

  async function logout() {
    await user.logout();
    task.clear();
    await router.replace({ name: 'Login' });
  }

  return { passwordLogin, smsLogin, switchTo, logout };
}
