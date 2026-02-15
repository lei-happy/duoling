"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const elementPlus = require("element-plus");
const useModal$1 = require("../ele-modal-render/use-modal");
const message = require("./message");
const messageBox = require("./message-box");
function useModal(options) {
  const modal = useModal$1.useModal();
  const message$1 = message.useMessage(options?.message);
  const messageBox$1 = messageBox.useMessageBox(options?.messageBox);
  return {
    ...modal,
    message: message$1,
    messageBox: messageBox$1,
    notification: elementPlus.ElNotification
  };
}
exports.useModal = useModal;
