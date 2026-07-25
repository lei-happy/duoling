import { ElMessageBox } from 'element-plus';
import { EleMessage } from 'ele-admin-plus';
import {
  grantWhitelist,
  revokeWhitelist
} from '@/api/ecosystem/audit-whitelist';

/**
 * 免审白名单的授予与移出
 *
 * 抽出来是因为这两个动作有三个入口（审核台右侧档案、白名单页的行操作、
 * 档案弹层），而确认文案本身就是风险提示的一部分：「移出后 30 天内不会被自动
 * 加回来」这句话如果只写在一个入口，从另一个入口点的人就不知道这件事。
 */
export function useWhitelistActions() {
  const grant = (tenantCode: string, onSuccess?: () => void) => {
    ElMessageBox.confirm(
      '授予后这家企业发布的挂牌会直接上架，只在 24 小时内做抽检。请确认已经看过它的历史记录。',
      '确定给这家企业开免审吗？',
      { type: 'warning', draggable: true, confirmButtonText: '确定授予' }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '正在授予免审，请稍候…',
          plain: true
        });
        grantWhitelist(tenantCode)
          .then((message) => {
            loading.close();
            EleMessage.success({
              message: (message as string) || '已加入免审白名单',
              plain: true
            });
            onSuccess?.();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const revoke = (tenantCode: string, onSuccess?: () => void) => {
    ElMessageBox.prompt(
      '移出后这家企业新发的挂牌都要走人工审核，30 天内不会被自动加回来。原因会记进处置记录。',
      '为什么要移出免审？',
      {
        draggable: true,
        confirmButtonText: '确定移出',
        inputType: 'textarea',
        inputPlaceholder: '例如：抽检发现挂牌内容与实际不符',
        inputValidator: (value: string) =>
          (value || '').trim().length >= 2 || '请简单写一下原因，至少 2 个字'
      }
    )
      .then(({ value }) => {
        const loading = EleMessage.loading({
          message: '正在移出免审，请稍候…',
          plain: true
        });
        revokeWhitelist(tenantCode, (value || '').trim())
          .then((message) => {
            loading.close();
            EleMessage.success({
              message: (message as string) || '已移出免审白名单',
              plain: true
            });
            onSuccess?.();
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  return { grant, revoke };
}
