import { defineComponent, ref, watch, nextTick, onMounted, onBeforeUnmount, createElementBlock, openBlock, normalizeClass, unref, createElementVNode, createVNode, createBlock, createCommentVNode, normalizeStyle } from "vue";
import Cropper from "cropperjs";
import { useResponsive } from "../ele-pro-layout/util";
import CropperPreview from "./components/cropper-preview";
import CropperTools from "./components/cropper-tools";
import { cropperEmits, cropperProps } from "./props";
const _hoisted_1 = { class: "ele-cropper-main" };
const _hoisted_2 = ["src"];
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "EleCropper" },
  __name: "index",
  props: cropperProps,
  emits: cropperEmits,
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const isResponsive = useResponsive(props);
    const imageRef = ref(null);
    const previewRef = ref(null);
    const state = {
      instance: null,
      imageType: props.imageType,
      scaleXValue: -1,
      scaleYValue: -1
    };
    const render = () => {
      destroy();
      const options = { ...props.options };
      if (props.preview && previewRef.value) {
        options.preview = previewRef.value.getPreviews();
      }
      if (imageRef.value) {
        state.instance = new Cropper(imageRef.value, options);
      }
    };
    const destroy = () => {
      state.instance && state.instance.destroy();
      state.instance = null;
    };
    const handleZoomIn = () => {
      state.instance && state.instance.zoom(0.1);
    };
    const handleZoomOut = () => {
      state.instance && state.instance.zoom(-0.1);
    };
    const handleMoveLeft = () => {
      state.instance && state.instance.move(-10, 0);
    };
    const handleMoveRight = () => {
      state.instance && state.instance.move(10, 0);
    };
    const handleMoveUp = () => {
      state.instance && state.instance.move(0, -10);
    };
    const handleMoveDown = () => {
      state.instance && state.instance.move(0, 10);
    };
    const handleRotateLeft = () => {
      state.instance && state.instance.rotate(-45);
    };
    const handleRotateRight = () => {
      state.instance && state.instance.rotate(45);
    };
    const handleFlipX = () => {
      state.instance && state.instance.scaleX(state.scaleXValue);
      state.scaleXValue = -state.scaleXValue;
    };
    const handleFlipY = () => {
      state.instance && state.instance.scaleY(state.scaleYValue);
      state.scaleYValue = -state.scaleYValue;
    };
    const handleReset = () => {
      state.instance && state.instance.reset();
    };
    const handleUpload = ({ data, type }) => {
      state.imageType = type;
      if (state.instance) {
        state.instance.replace(data);
      } else {
        const elem = imageRef.value;
        if (elem) {
          elem.src = data;
          elem.style.display = "block";
        }
        render();
      }
    };
    const handleOk = () => {
      if (!state.instance) {
        emit("done");
        return;
      }
      const opt = props.croppedOptions ? props.croppedOptions : void 0;
      const result = state.instance.getCroppedCanvas(opt);
      if (!result) {
        emit("done");
        return;
      }
      if (props.toBlob) {
        result.toBlob((blob) => {
          emit("done", blob);
        }, state.imageType);
        return;
      }
      emit("done", result.toDataURL(state.imageType));
    };
    watch(
      () => props.src,
      (src) => {
        if (src) {
          if (state.instance) {
            state.instance.replace(src);
          } else {
            nextTick(() => {
              render();
            });
          }
        } else {
          destroy();
        }
      }
    );
    watch(
      () => props.imageType,
      (value) => {
        if (value) {
          state.imageType = value;
        }
      }
    );
    onMounted(() => {
      props.src && render();
    });
    onBeforeUnmount(() => {
      destroy();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        class: normalizeClass(["ele-cropper", { "is-responsive": unref(isResponsive) }])
      }, [
        createElementVNode("div", _hoisted_1, [
          createElementVNode("div", {
            class: "ele-cropper-image",
            style: normalizeStyle({ height: _ctx.height })
          }, [
            createElementVNode("img", {
              ref_key: "imageRef",
              ref: imageRef,
              src: _ctx.src,
              style: { display: "none" }
            }, null, 8, _hoisted_2)
          ], 4),
          _ctx.preview ? (openBlock(), createBlock(CropperPreview, {
            key: 0,
            ref_key: "previewRef",
            ref: previewRef,
            previewWidth: _ctx.previewWidth,
            aspectRatio: _ctx.options ? _ctx.options.aspectRatio : void 0
          }, null, 8, ["previewWidth", "aspectRatio"])) : createCommentVNode("", true)
        ]),
        createVNode(CropperTools, {
          tools: _ctx.tools,
          accept: _ctx.accept,
          locale: _ctx.locale,
          tooltip: _ctx.tooltip,
          tooltipProps: _ctx.tooltipProps,
          beforeUploadClick: _ctx.beforeUploadClick,
          onZoomIn: handleZoomIn,
          onZoomOut: handleZoomOut,
          onMoveLeft: handleMoveLeft,
          onMoveRight: handleMoveRight,
          onMoveUp: handleMoveUp,
          onMoveDown: handleMoveDown,
          onRotateLeft: handleRotateLeft,
          onRotateRight: handleRotateRight,
          onFlipX: handleFlipX,
          onFlipY: handleFlipY,
          onReset: handleReset,
          onUpload: handleUpload,
          onOk: handleOk
        }, null, 8, ["tools", "accept", "locale", "tooltip", "tooltipProps", "beforeUploadClick"])
      ], 2);
    };
  }
});
export {
  _sfc_main as default
};
