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

/** 企业自助注册 */
export function registerTenant(data: {
  tenant_name: string;
  contact_person: string;
  contact_phone: string;
  contact_email?: string;
  referrer_code?: string;
}) {
  return request.post('/register', data);
}
