import axios from 'axios';

const request = axios.create({
  baseURL: '/api/open',
  timeout: 15000
});

/** 获取产品版本列表 */
export function getProductVersions() {
  return request.get('/product/versions');
}

/** 获取产品更新记录列表（分页） */
export function getChangelog(params?: { page?: number; page_size?: number }) {
  return request.get('/changelog', { params });
}

/** 发送短信验证码（官网企业注册 purpose=4） */
export async function sendSmsCode(phone: string, purpose: number) {
  const res = await request.post<{ code: number; message?: string; data?: { message?: string; code?: string } }>(
    '/sms/send',
    { phone, purpose, app_type: 'website' }
  );
  if (res.data.code === 0) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message || '发送失败'));
}

/** 查询手机号是否已关联企业（可客户端登录；仅有平台账号无企业时不视为已注册） */
export async function checkRegisterPhone(phone: string) {
  const res = await request.get<{ code: number; message?: string; data?: { registered: boolean } }>(
    '/register/phone-available',
    { params: { phone } }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message || '校验失败'));
}

/** 企业自助注册（立即返回 task_id，需轮询进度） */
export function registerTenant(data: {
  tenant_name: string;
  contact_person: string;
  contact_phone: string;
  sms_code: string;
  referrer_code?: string;
}) {
  return request.post('/register', data);
}

/** 查询企业注册任务进度 */
export function getRegisterProgress(taskId: string) {
  return request.get(`/register/progress/${encodeURIComponent(taskId)}`);
}
