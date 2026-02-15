import { ElNotification } from 'element-plus';
import { useModal as useModalBase } from '../ele-modal-render/use-modal';
import { useMessage } from './message';
import type { MessageOptions } from './message';
import { useMessageBox } from './message-box';
import type { MessageBoxOptions } from './message-box';

export interface UseModalOptions {
  message: MessageOptions;
  messageBox?: MessageBoxOptions;
}

/**
 * 弹窗, 抽屉, 消息, 弹出框, 消息通知等组件操作
 */
export function useModal(options?: UseModalOptions) {
  const modal = useModalBase();
  const message = useMessage(options?.message);
  const messageBox = useMessageBox(options?.messageBox);

  return {
    ...modal,
    message,
    messageBox,
    notification: ElNotification
  };
}
