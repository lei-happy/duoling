"use strict";
Object.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
const vue = require("vue");
const elementPlus = require("element-plus");
const receiver = require("../ele-config-provider/receiver");
const util = require("../ele-pro-layout/util");
const MessageBoxIcon = require("../ele-app/components/message-box-icon");
const common = require("./common");
function getWrapEl(bodyEl) {
  const parent = bodyEl || document.body;
  const className = "ele-message-box-wrapper";
  const elem = document.createElement("div");
  elem.classList.add(className);
  parent.appendChild(elem);
  return elem;
}
function useMessageBox(globalOpt) {
  const layoutState = util.useLayoutState();
  const globalProps = receiver.useGlobalProps("messageBox");
  const appContext = vue.getCurrentInstance?.()?.appContext;
  const state = { wrapEl: null, isActivated: true, id: 0 };
  const instances = /* @__PURE__ */ new Map();
  const hideClass = "is-hide";
  vue.onActivated(() => {
    state.isActivated = true;
    state.wrapEl && state.wrapEl.classList.remove(hideClass);
  });
  vue.onDeactivated(() => {
    state.isActivated = false;
    state.wrapEl && state.wrapEl.classList.add(hideClass);
  });
  vue.onBeforeUnmount(() => {
    for (const [_key, insDoClose] of instances) {
      insDoClose && insDoClose();
    }
    instances.clear();
  });
  const getOption = (options) => {
    state.id++;
    const msgId = `m_${state.id}`;
    const opt = {
      ...globalProps.value || {},
      ...globalOpt || {},
      ...options || {}
    };
    if (opt.inner) {
      if (opt.appendTo == null && layoutState.modalsEl != null) {
        if (state.wrapEl == null) {
          state.wrapEl = getWrapEl(layoutState.modalsEl);
        }
        opt.appendTo = state.wrapEl;
      } else if (opt.appendTo != null) {
        opt.appendTo = vue.unref(opt.appendTo);
      }
      opt.lockScroll = false;
    } else if (opt.appendTo != null) {
      opt.appendTo = vue.unref(opt.appendTo);
    }
    const classes = ["ele-message-box"];
    if (opt.customClass) {
      classes.push(opt.customClass);
    }
    opt.customClass = classes.join(" ");
    opt.icon = vue.h(MessageBoxIcon, {
      type: opt.type,
      icon: opt.icon,
      boxId: msgId,
      onBoxDestroy: (boxId) => {
        boxId && instances.delete(boxId);
      },
      onBoxMounted: ({ boxId, doClose }) => {
        boxId && instances.set(boxId, doClose);
      }
    });
    return common.omit(opt, ["inner"]);
  };
  const messageBox = function(options) {
    return elementPlus.ElMessageBox(getOption(options), appContext);
  };
  messageBox.alert = function(message, title, options, context) {
    const ctx = context ?? appContext;
    return elementPlus.ElMessageBox.alert(message, title, getOption(options), ctx);
  };
  messageBox.confirm = function(message, title, options, context) {
    const ctx = context ?? appContext;
    return elementPlus.ElMessageBox.confirm(message, title, getOption(options), ctx);
  };
  messageBox.prompt = function(message, title, options, context) {
    const ctx = context ?? appContext;
    return elementPlus.ElMessageBox.prompt(message, title, getOption(options), ctx);
  };
  messageBox.close = function() {
    return elementPlus.ElMessageBox.close();
  };
  return messageBox;
}
exports.useMessageBox = useMessageBox;
