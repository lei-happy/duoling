/**
 * 修改密码参数
 */
export interface UpdatePasswordParam {
  /** 新密码 */
  password: string;
  /** 原始密码 */
  oldPassword: string;
}
