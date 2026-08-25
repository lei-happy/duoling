import { EleMessage } from 'ele-admin-plus';

/**
 * 复制文本到剪贴板，并用口语提示结果。
 * 计划号、VIN、任务单号等标识字段统一走这里，避免各弹框各写一套。
 */
export async function copyTextWithToast(
  raw: string | undefined | null,
  options?: {
    emptyTip?: string;
    successTip?: string;
  }
): Promise<boolean> {
  const emptyTip = options?.emptyTip ?? '没有可复制的内容';
  const successTip = options?.successTip ?? '已复制';
  const text = raw?.trim();
  if (!text) {
    EleMessage.warning({ message: emptyTip, plain: true });
    return false;
  }
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    EleMessage.success({ message: successTip, plain: true });
    return true;
  } catch {
    EleMessage.error({ message: '复制失败，请重试', plain: true });
    return false;
  }
}
