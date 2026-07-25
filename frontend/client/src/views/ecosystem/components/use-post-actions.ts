import { ElMessageBox } from 'element-plus';
import { EleMessage } from 'ele-admin-plus';
import { delistPost, relistPost, submitPost } from '@/api/ecosystem/post';
import type { EcoPost } from '@/api/ecosystem/hall/model';
import { PostStatus } from '@/config/ecosystem/enums';

/**
 * 挂牌的状态流转动作（提交审核 / 停止展示 / 重新上架）
 *
 * 「我发布的」列表和详情抽屉里都有这三个动作。抽成一处的重点不是省几行代码，
 * 而是**确认文案**：「停止展示会一并结束 3 个正在进行的洽谈」这句风险提示，
 * 如果只写在列表里，从详情点下去的人就不知道这件事。
 *
 * 延长展示天数不在这里：它要让用户选天数，得有界面，见 eco-extend-modal.vue。
 */
export function usePostActions() {
  /** 提交审核 */
  const submit = async (post: EcoPost, onDone?: () => void) => {
    const loading = EleMessage.loading({
      message: '正在提交，请稍候…',
      plain: true
    });
    try {
      const { message } = await submitPost(post.id);
      EleMessage.success({
        message: message || '已提交，平台会尽快审核',
        plain: true
      });
      onDone?.();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能提交，请稍后再试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };

  /** 停止展示。草稿与被驳回的挂牌走的是同一个接口，但对用户是另一件事 */
  const delist = async (post: EcoPost, onDone?: () => void) => {
    const neverShown =
      post.status === PostStatus.DRAFT || post.status === PostStatus.REJECTED;
    const talking = post.intentCount ?? 0;
    const tip = neverShown
      ? '这条信息会被归档，之后需要的话可以重新上架。'
      : talking
        ? `有 ${talking} 位同行正在与你洽谈，停止展示会一并结束这些洽谈。`
        : '停止展示后，同行不会再看到这条信息。';
    const title = neverShown ? '不发了' : '停止展示';
    try {
      await ElMessageBox.confirm(`${tip}确定吗？`, title, {
        type: 'warning',
        draggable: true,
        confirmButtonText: title,
        cancelButtonText: '再想想'
      });
    } catch {
      return;
    }
    const loading = EleMessage.loading({
      message: neverShown ? '正在处理，请稍候…' : '正在停止展示，请稍候…',
      plain: true
    });
    try {
      const { data, message } = await delistPost(post.id);
      const extra = data.invalidatedIntentCount
        ? `，同时结束了 ${data.invalidatedIntentCount} 个洽谈`
        : '';
      EleMessage.success({
        message: (message || '已停止展示，同行不会再看到这条信息') + extra,
        plain: true
      });
      onDone?.();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能停止展示，请稍后再试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };

  /** 重新上架 */
  const relist = async (post: EcoPost, onDone?: () => void) => {
    try {
      await ElMessageBox.confirm(
        '重新上架要再过一次平台审核，通常 2 小时内完成。确定提交吗？',
        '重新上架',
        {
          type: 'info',
          draggable: true,
          confirmButtonText: '提交审核',
          cancelButtonText: '取消'
        }
      );
    } catch {
      return;
    }
    const loading = EleMessage.loading({
      message: '正在提交，请稍候…',
      plain: true
    });
    try {
      const { message } = await relistPost(post.id);
      EleMessage.success({
        message: message || '已提交，审核通过后同行就能看到了',
        plain: true
      });
      onDone?.();
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能提交，请稍后再试',
        plain: true
      });
    } finally {
      loading.close();
    }
  };

  return { submit, delist, relist };
}
