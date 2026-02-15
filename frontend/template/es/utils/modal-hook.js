import { ElNotification } from "element-plus";
import { useModal as useModal$1 } from "../ele-modal-render/use-modal";
import { useMessage } from "./message";
import { useMessageBox } from "./message-box";
function useModal(options) {
  const modal = useModal$1();
  const message = useMessage(options?.message);
  const messageBox = useMessageBox(options?.messageBox);
  return {
    ...modal,
    message,
    messageBox,
    notification: ElNotification
  };
}
export {
  useModal
};
