"use strict";
const vue = require("vue");
const elementPlus = require("element-plus");
const index = require("../icons/index");
const common = require("../utils/common");
const hook = require("../utils/hook");
const MainContent = require("../ele-loading/components/main-content");
const LoadingSpinner = require("../ele-loading/components/loading-spinner");
const util = require("../ele-pro-layout/util");
const util$1 = require("./util");
const props = require("./props");
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "EleModal", inheritAttrs: false },
  __name: "index",
  props: props.modalProps,
  emits: props.modalEmits,
  setup(__props, { expose: __expose, emit: __emit }) {
    const props$1 = __props;
    const emit = __emit;
    const layoutState = util.useLayoutState();
    const isResponsive = util.useResponsive(props$1);
    const dialogRef = vue.ref(null);
    const isFullscreen = vue.ref(props$1.fullscreen ?? false);
    const modalPositionTop = vue.ref();
    const modalPositionLeft = vue.ref();
    const modalResizedWidth = vue.ref();
    const modalResizedHeight = vue.ref();
    const modalZIndex = vue.ref(props$1.zIndex);
    const modalIsMoving = vue.ref(false);
    const isActivated = vue.ref(!props$1.isDeactivated);
    const dialogClass = vue.computed(() => {
      const classes = [util$1.wrapperClass];
      if (isResponsive.value) {
        classes.push("ele-modal-responsive");
      }
      if (props$1.maxHeight == null || props$1.maxHeight != null && props$1.maxHeight !== "") {
        classes.push("ele-modal-fluid");
      }
      if (props$1.position === "top") {
        classes.push("ele-modal-top");
      } else if (props$1.position === "bottom") {
        classes.push("ele-modal-bottom");
      } else if (props$1.position === "left") {
        classes.push("ele-modal-left");
      } else if (props$1.position === "right") {
        classes.push("ele-modal-right");
      } else if (props$1.position === "leftTop") {
        classes.push("ele-modal-left-top");
      } else if (props$1.position === "leftBottom") {
        classes.push("ele-modal-left-bottom");
      } else if (props$1.position === "rightTop") {
        classes.push("ele-modal-right-top");
      } else if (props$1.position === "rightBottom") {
        classes.push("ele-modal-right-bottom");
      }
      if (props$1.draggable) {
        classes.push("ele-modal-movable");
      }
      if (props$1.resizable) {
        classes.push("ele-modal-resizable");
      }
      if (props$1.multiple) {
        classes.push("ele-modal-multiple");
      }
      if (isFullscreen.value) {
        classes.push("ele-modal-fullscreen");
      }
      if (!props$1.modelValue) {
        classes.push(util$1.closedClass);
      }
      if (!isActivated.value && props$1.modelValue) {
        classes.push("ele-modal-hide");
      }
      if (props$1.inner) {
        classes.push("ele-modal-inner");
      }
      if (props$1.compLoading && !props$1.loading) {
        classes.push("ele-modal-comp-loading");
      }
      if (props$1.flexTable === "auto") {
        classes.push("ele-modal-flex-auto-table");
      } else if (props$1.flexTable) {
        classes.push("ele-modal-flex-table");
      }
      if (props$1.customFooter) {
        classes.push("ele-modal-custom-footer");
      }
      if (props$1.modalClass) {
        classes.push(props$1.modalClass);
      }
      return classes.join(" ");
    });
    const modalIsAbsolute = vue.computed(() => {
      return modalPositionTop.value != null || modalPositionLeft.value != null;
    });
    const modalPositionMargin = vue.computed(() => {
      if (typeof props$1.position === "string") {
        return;
      }
      return util$1.getPositionMargin({
        top: props$1.top,
        ...props$1.alignCenter ? { top: "auto", left: "auto", right: "auto", bottom: "auto" } : {},
        ...props$1.position || {}
      });
    });
    const teleportTo = vue.computed(() => {
      return util$1.getModalContainer(
        props$1.inner,
        props$1.multiple,
        props$1.appendTo,
        layoutState.modalsEl
      );
    });
    const teleportDisabled = vue.computed(() => {
      const bodyAppend = "body";
      const appendTo = props$1.appendTo || bodyAppend;
      const disabled = appendTo === bodyAppend ? !props$1.appendToBody : false;
      return props$1.multiple || props$1.inner ? false : disabled;
    });
    const getModalEl = () => {
      const el = vue.unref(dialogRef.value?.dialogContentRef)?.$el;
      return el;
    };
    const topModal = () => {
      const zIndex = util$1.getMaxZIndex(getModalEl(), props$1.zIndex);
      if (zIndex != null && modalZIndex.value !== zIndex) {
        modalZIndex.value = zIndex;
      }
    };
    const moveEventOption = {
      modalEl: null,
      wrapEl: null,
      downOL: null,
      downOT: null,
      downW: null,
      downH: null,
      fixTop: 0.65,
      fixLeft: 0.65
    };
    const {
      handleMousedown: handleHeaderMousedown,
      handleTouchstart: handleHeaderTouchstart
    } = hook.useMoveEvent({
      start: () => {
        moveEventOption.modalEl = getModalEl();
        moveEventOption.wrapEl = moveEventOption.modalEl?.parentElement;
        if (!moveEventOption.modalEl || !moveEventOption.wrapEl || !props$1.draggable || isFullscreen.value) {
          return;
        }
        modalIsMoving.value = true;
        moveEventOption.downOL = moveEventOption.modalEl.offsetLeft;
        moveEventOption.downOT = moveEventOption.modalEl.offsetTop;
      },
      move: ({ distanceX, distanceY, e }) => {
        if (!moveEventOption.modalEl || !moveEventOption.wrapEl || moveEventOption.downOL == null || moveEventOption.downOT == null || distanceX == null || distanceY == null) {
          return;
        }
        e.preventDefault();
        let positionLeft = distanceX + moveEventOption.downOL;
        let positionTop = distanceY + moveEventOption.downOT;
        const limitL = moveEventOption.wrapEl.clientWidth - moveEventOption.modalEl.clientWidth - moveEventOption.fixLeft;
        const limitT = moveEventOption.wrapEl.clientHeight - moveEventOption.modalEl.clientHeight - moveEventOption.fixTop;
        if (!props$1.moveOut) {
          if (positionLeft < 0) {
            positionLeft = 0;
          } else if (positionLeft > limitL) {
            positionLeft = limitL;
          }
          if (positionTop > limitT) {
            positionTop = limitT;
          }
          if (positionTop < 0) {
            positionTop = 0;
          }
        } else {
          if (!util$1.canMoveOut(props$1.moveOut, "left") && positionLeft < 0) {
            positionLeft = 0;
          }
          if (!util$1.canMoveOut(props$1.moveOut, "right") && positionLeft > limitL) {
            positionLeft = limitL;
          }
          if (!util$1.canMoveOut(props$1.moveOut, "bottom") && positionTop > limitT) {
            positionTop = limitT;
          }
          if (!util$1.canMoveOut(props$1.moveOut, "top") && positionTop < 0) {
            positionTop = 0;
          }
          const minLimitL = moveEventOption.wrapEl.clientWidth - 48;
          if (positionLeft > minLimitL) {
            positionLeft = minLimitL;
          }
          const minLimitT = moveEventOption.wrapEl.clientHeight - 48;
          if (props$1.multiple && positionTop > minLimitT) {
            positionTop = minLimitT;
          }
        }
        modalPositionLeft.value = `${Math.floor(positionLeft)}px`;
        modalPositionTop.value = `${Math.floor(positionTop)}px`;
      },
      end: () => {
        modalIsMoving.value = false;
        moveEventOption.downOL = null;
        moveEventOption.downOT = null;
      },
      touchmoveOptions: { passive: false }
    });
    const {
      handleMousedown: handleResizeMousedown,
      handleTouchstart: handleResizeTouchstart
    } = hook.useMoveEvent({
      start: () => {
        moveEventOption.modalEl = getModalEl();
        moveEventOption.wrapEl = moveEventOption.modalEl?.parentElement;
        if (!moveEventOption.modalEl || !moveEventOption.wrapEl || !props$1.resizable || isFullscreen.value) {
          return;
        }
        modalIsMoving.value = true;
        moveEventOption.downW = moveEventOption.modalEl.clientWidth;
        moveEventOption.downH = moveEventOption.modalEl.clientHeight;
      },
      move: ({ distanceX, distanceY, e }) => {
        if (!moveEventOption.modalEl || !moveEventOption.wrapEl || moveEventOption.downW == null || moveEventOption.downH == null || distanceX == null || distanceY == null) {
          return;
        }
        e.preventDefault();
        if (modalPositionLeft.value == null) {
          modalPositionLeft.value = `${moveEventOption.modalEl.offsetLeft}px`;
        }
        if (modalPositionTop.value == null) {
          modalPositionTop.value = `${moveEventOption.modalEl.offsetTop}px`;
        }
        if (props$1.resizable !== "vertical") {
          const w = distanceX + moveEventOption.downW;
          const maxW = moveEventOption.wrapEl.clientWidth - moveEventOption.modalEl.offsetLeft - moveEventOption.fixLeft;
          const nw = (w < props$1.minWidth ? props$1.minWidth : !util$1.canMoveOut(props$1.moveOut, "right") && w > maxW ? maxW : w) + "px";
          modalResizedWidth.value = nw;
        }
        if (props$1.resizable !== "horizontal") {
          const h = distanceY + moveEventOption.downH;
          const maxH = moveEventOption.wrapEl.clientHeight - moveEventOption.modalEl.offsetTop - moveEventOption.fixTop;
          const nh = (h < props$1.minHeight ? props$1.minHeight : !util$1.canMoveOut(props$1.moveOut, "bottom") && h > maxH ? maxH : h) + "px";
          modalResizedHeight.value = nh;
        }
      },
      end: () => {
        modalIsMoving.value = false;
        moveEventOption.downW = null;
        moveEventOption.downH = null;
      },
      touchmoveOptions: { passive: false }
    });
    const mousedownListener = () => {
      if (props$1.multiple) {
        topModal();
      }
    };
    const bindAutoTopEvent = () => {
      const modalEl = getModalEl();
      if (modalEl) {
        modalEl.addEventListener("mousedown", mousedownListener);
        modalEl.addEventListener("touchstart", mousedownListener, {
          passive: true
        });
      }
    };
    const unbindAutoTopEvent = () => {
      const modalEl = getModalEl();
      if (modalEl) {
        modalEl.removeEventListener("mousedown", mousedownListener);
        modalEl.removeEventListener("touchstart", mousedownListener);
      }
    };
    const updateModelValue = (modelValue) => {
      emit("update:modelValue", modelValue);
    };
    const toggleFullscreen = (fullscreen) => {
      isFullscreen.value = !isFullscreen.value;
      topModal();
      emit("update:fullscreen", isFullscreen.value);
    };
    const resetPosition = () => {
      isFullscreen.value = props$1.fullscreen ?? false;
      modalPositionTop.value = void 0;
      modalPositionLeft.value = void 0;
      modalResizedWidth.value = void 0;
      modalResizedHeight.value = void 0;
      modalIsMoving.value = false;
    };
    const handleOpen = () => {
      topModal();
      emit("open");
    };
    const handleOpened = () => {
      bindAutoTopEvent();
      emit("opened");
    };
    const handleClose = () => {
      unbindAutoTopEvent();
      emit("close");
    };
    const handleClosed = () => {
      if (props$1.resetOnClose || props$1.destroyOnClose) {
        resetPosition();
      }
      emit("closed");
    };
    const handleOpenAutoFocus = () => {
      emit("openAutoFocus");
    };
    const handleCloseAutoFocus = () => {
      emit("closeAutoFocus");
    };
    const closeModal = () => {
      if (dialogRef.value) {
        dialogRef.value.handleClose();
      } else {
        updateModelValue(false);
      }
    };
    vue.watch(
      () => props$1.zIndex,
      (zIndex) => {
        modalZIndex.value = zIndex;
      }
    );
    vue.watch(
      () => props$1.fullscreen,
      (fullscreen) => {
        isFullscreen.value = fullscreen ?? false;
      }
    );
    vue.watch(
      () => props$1.isDeactivated,
      (deactivated) => {
        isActivated.value = !deactivated;
      }
    );
    vue.onMounted(() => {
      if (props$1.modelValue) {
        topModal();
      }
    });
    vue.onBeforeUnmount(() => {
      moveEventOption.modalEl = null;
      moveEventOption.wrapEl = null;
      unbindAutoTopEvent();
    });
    vue.onActivated(() => {
      isActivated.value = true;
    });
    vue.onDeactivated(() => {
      isActivated.value = false;
    });
    __expose({
      dialogRef,
      resetPosition,
      handleClose: closeModal
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(vue.Teleport, {
        to: teleportTo.value,
        disabled: teleportDisabled.value
      }, [
        vue.createVNode(vue.unref(elementPlus.ElDialog), vue.mergeProps({ ..._ctx.$attrs, ...vue.unref(common.pick)(_ctx.$props, vue.unref(props.dialogPropKeys)) }, {
          ref_key: "dialogRef",
          ref: dialogRef,
          fullscreen: false,
          modal: _ctx.multiple ? false : _ctx.modal,
          modalClass: dialogClass.value,
          appendToBody: false,
          lockScroll: _ctx.inner || _ctx.multiple ? false : _ctx.lockScroll,
          showClose: false,
          draggable: false,
          overflow: false,
          alignCenter: false,
          zIndex: modalZIndex.value,
          style: {
            margin: modalIsAbsolute.value ? 0 : modalPositionMargin.value,
            position: modalIsAbsolute.value ? "absolute" : void 0,
            top: modalPositionTop.value,
            left: modalPositionLeft.value,
            width: modalResizedWidth.value,
            maxWidth: modalResizedWidth.value,
            minWidth: modalResizedWidth.value,
            height: modalResizedHeight.value ?? (typeof _ctx.height === "number" ? `${_ctx.height}px` : _ctx.height),
            maxHeight: modalResizedHeight.value ?? (typeof _ctx.maxHeight === "number" ? `${_ctx.maxHeight}px` : _ctx.maxHeight),
            minHeight: modalResizedHeight.value,
            userSelect: modalIsMoving.value ? "none" : void 0
          },
          "onUpdate:modelValue": updateModelValue,
          onOpen: handleOpen,
          onOpened: handleOpened,
          onClose: handleClose,
          onClosed: handleClosed,
          onOpenAutoFocus: handleOpenAutoFocus,
          onCloseAutoFocus: handleCloseAutoFocus
        }), vue.createSlots({
          header: vue.withCtx(({ close, titleId, titleClass }) => [
            vue.createElementVNode("div", {
              style: vue.normalizeStyle(_ctx.headerStyle),
              class: "ele-modal-header",
              onMousedown: _cache[6] || (_cache[6] = //@ts-ignore
              (...args) => vue.unref(handleHeaderMousedown) && vue.unref(handleHeaderMousedown)(...args)),
              onTouchstartPassive: _cache[7] || (_cache[7] = //@ts-ignore
              (...args) => vue.unref(handleHeaderTouchstart) && vue.unref(handleHeaderTouchstart)(...args))
            }, [
              vue.createElementVNode("div", {
                class: "ele-modal-title",
                style: vue.normalizeStyle(_ctx.titleStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "header", {
                  close,
                  titleId,
                  titleClass
                }, () => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.title), 1)
                ])
              ], 4),
              _ctx.maxable ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 0,
                class: "ele-modal-tool ele-modal-tool-max",
                style: vue.normalizeStyle(_ctx.fullscreenBtnStyle),
                onClick: _cache[0] || (_cache[0] = ($event) => toggleFullscreen()),
                onMousedown: _cache[1] || (_cache[1] = vue.withModifiers(() => {
                }, ["stop"])),
                onTouchstartPassive: _cache[2] || (_cache[2] = vue.withModifiers(() => {
                }, ["stop"]))
              }, [
                vue.renderSlot(_ctx.$slots, "maxIcon", { fullscreen: isFullscreen.value }, () => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      isFullscreen.value ? (vue.openBlock(), vue.createBlock(vue.unref(index.CompressOutlined), { key: 0 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.ExpandOutlined), { key: 1 }))
                    ]),
                    _: 1
                  })
                ])
              ], 36)) : vue.createCommentVNode("", true),
              _ctx.showClose ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 1,
                class: "ele-modal-tool",
                style: vue.normalizeStyle(_ctx.closeBtnStyle),
                onClick: _cache[3] || (_cache[3] = ($event) => updateModelValue(false)),
                onMousedown: _cache[4] || (_cache[4] = vue.withModifiers(() => {
                }, ["stop"])),
                onTouchstartPassive: _cache[5] || (_cache[5] = vue.withModifiers(() => {
                }, ["stop"]))
              }, [
                vue.renderSlot(_ctx.$slots, "closeIcon", {}, () => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                    default: vue.withCtx(() => [
                      _ctx.closeIcon ? (vue.openBlock(), vue.createBlock(vue.resolveDynamicComponent(_ctx.closeIcon), { key: 0 })) : (vue.openBlock(), vue.createBlock(vue.unref(index.CloseOutlined), { key: 1 }))
                    ]),
                    _: 1
                  })
                ])
              ], 36)) : vue.createCommentVNode("", true)
            ], 36),
            _ctx.resizable ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 0,
              class: vue.normalizeClass(["ele-modal-resize-icon", [
                { "is-horizontal": _ctx.resizable === "horizontal" },
                { "is-vertical": _ctx.resizable === "vertical" }
              ]]),
              style: vue.normalizeStyle(_ctx.resizeIconStyle),
              onMousedown: _cache[8] || (_cache[8] = //@ts-ignore
              (...args) => vue.unref(handleResizeMousedown) && vue.unref(handleResizeMousedown)(...args)),
              onTouchstartPassive: _cache[9] || (_cache[9] = //@ts-ignore
              (...args) => vue.unref(handleResizeTouchstart) && vue.unref(handleResizeTouchstart)(...args))
            }, [
              vue.renderSlot(_ctx.$slots, "resizeIcon", {}, () => [
                vue.createVNode(vue.unref(elementPlus.ElIcon), null, {
                  default: vue.withCtx(() => [
                    vue.createVNode(vue.unref(index.ResizeOutlined))
                  ]),
                  _: 1
                })
              ])
            ], 38)) : vue.createCommentVNode("", true)
          ]),
          default: vue.withCtx(() => [
            vue.createVNode(MainContent, {
              class: vue.normalizeClass(["ele-modal-body", [{ "is-form": _ctx.form }, _ctx.modalBodyClass]]),
              style: vue.normalizeStyle(_ctx.bodyStyle)
            }, {
              default: vue.withCtx(() => [
                vue.renderSlot(_ctx.$slots, "default")
              ]),
              _: 3
            }, 8, ["class", "style"]),
            vue.createVNode(LoadingSpinner, vue.mergeProps(_ctx.loadingProps || {}, {
              loading: _ctx.compLoading || _ctx.loading,
              plain: true
            }), null, 16, ["loading"])
          ]),
          _: 2
        }, [
          _ctx.$slots.footer ? {
            name: "footer",
            fn: vue.withCtx(() => [
              vue.createElementVNode("div", {
                class: "ele-modal-footer",
                style: vue.normalizeStyle(_ctx.footerStyle)
              }, [
                vue.renderSlot(_ctx.$slots, "footer")
              ], 4)
            ]),
            key: "0"
          } : void 0
        ]), 1040, ["modal", "modalClass", "lockScroll", "zIndex", "style"])
      ], 8, ["to", "disabled"]);
    };
  }
});
module.exports = _sfc_main;
