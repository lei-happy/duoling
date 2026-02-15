import { defineComponent, ref, computed, watch } from 'vue';
import EleWatermark from '../../ele-watermark/index.vue';
import {
  getProps,
  svgContents,
  svgText,
  svgProp,
  getOption
} from '../../ele-watermark/util';

export default defineComponent({
  name: 'ReceiverView',
  props: {
    wrapHeight: [String, Number]
  },
  setup(props, { slots }) {
    const svgOptions = ref();
    const image = svgText[svgText.length - 2];
    const { svgKey, svgProps, svgConfig, imageId } = getProps(svgContents);
    const svgId = computed<string | undefined>(() => svgConfig.key);
    const content =
      svgProp[svgText.findIndex((c: any) => c === svgText[svgText.length - 1])];
    watch(
      svgId,
      (id) => {
        svgOptions.value = getOption(
          id,
          content,
          svgProps,
          2,
          13,
          image,
          svgKey,
          svgContents,
          svgProp,
          svgProp[svgText.findIndex((s: any) => s === image)]
        );
      },
      { immediate: true }
    );
    return () => (
      <EleWatermark
        width={236}
        height={74}
        wrapHeight={props.wrapHeight}
        disabled={!!imageId.value}
        fixed={!svgOptions.value}
        content={svgKey.value}
        wrapPosition={false}
        svgRender={true}
      >
        {slots.default?.(svgProps)}
      </EleWatermark>
    );
  }
});
