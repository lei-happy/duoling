<!-- 地图位置选择 -->
<template>
  <EleModal
    width="740px"
    :title="lang.title"
    v-bind="modalProps || {}"
    :modelValue="modelValue"
    class="ele-map-picker"
    :class="{ 'is-responsive': isResponsive }"
    @update:modelValue="updateModelValue"
  >
    <MapView
      v-bind="mapProps"
      ref="mapRef"
      :message="lang.message"
      :clickMessage="lang.clickMessage"
      :searchPlaceholder="lang.placeholder"
      :okText="lang.ok"
      :mapKey="aMapKey"
      :mode="keywordMode ? 'keyword' : mode"
      @mapDone="handleMapDone"
      @done="handleDone"
    />
    <template
      v-for="name in Object.keys($slots).filter((k) => 'default' !== k)"
      #[name]="slotProps"
    >
      <slot :name="name" v-bind="slotProps || {}"></slot>
    </template>
  </EleModal>
</template>

<script lang="ts" setup>
  import { ref, computed, watch } from 'vue';
  import { pick } from '../utils/common';
  import type { EleMapPickerViewInstance } from '../ele-app/plusx';
  import { useLocale } from '../ele-config-provider/receiver';
  import { useResponsive } from '../ele-pro-layout/util';
  import EleModal from '../ele-modal/index.vue';
  import MapView from './components/map-view.vue';
  import type { PoiItem } from './types';
  import { mapPickerProps, mapPickerEmits, mapPropKeys } from './props';
  import type { MapProps } from './props';

  defineOptions({ name: 'EleMapPicker' });

  const props = defineProps(mapPickerProps);

  const emit = defineEmits(mapPickerEmits);

  const { lang, globalConfig } = useLocale('map', props);

  /** 是否开启布局响应 */
  const isResponsive = useResponsive(props);

  /** 地图组件 */
  const mapRef = ref<EleMapPickerViewInstance>(null);

  /** 地图密钥 */
  const aMapKey = computed(() => props.mapKey || globalConfig.mapKey);

  /** 地图属性 */
  const mapProps = computed<Partial<MapProps>>(() => {
    return pick(props, mapPropKeys);
  });

  /** 更新modelValue */
  const updateModelValue = (visible: boolean) => {
    emit('update:modelValue', visible);
  };

  /** 地图渲染完成事件 */
  const handleMapDone = (ins: any) => {
    emit('mapDone', ins);
  };

  /** 位置选择完成事件 */
  const handleDone = (result: PoiItem) => {
    emit('done', result);
  };

  watch(
    () => props.modelValue,
    (visible: boolean) => {
      if (visible) {
        mapRef.value && mapRef.value.showInitSelected();
      }
    }
  );

  defineExpose({
    mapRef
  });
</script>
