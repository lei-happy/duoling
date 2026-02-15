<template>
  <ele-card header="地图位置选择">
    <div>
      <ele-dropdown
        v-model="mode"
        :items="[
          { title: '点击地图模式', command: 'lnglat' },
          { title: '关键字检索模式', command: 'keyword' },
          { title: 'POI检索模式', command: 'poi' }
        ]"
        trigger="click"
        style="margin-right: 12px"
      >
        <template #default="{ selected }">
          <el-button class="ele-btn-icon" style="width: 134px">
            <span>{{ selected?.title }}</span>
            <el-icon :size="12" style="margin: 0 -4px 0 2px">
              <ArrowDown />
            </el-icon>
          </el-button>
        </template>
      </ele-dropdown>
      <el-button type="primary" class="ele-btn-icon" @click="openMapPicker">
        打开位置选择
      </el-button>
    </div>
    <div style="margin-top: 12px">经 纬 度 : {{ result.lngAndLat }}</div>
    <div style="margin-top: 12px">选中位置: {{ result.location }}</div>
    <div style="margin-top: 12px">详细地址: {{ result.address }}</div>
  </ele-card>
  <!-- 地图位置选择弹窗 -->
  <ele-map-picker
    v-model="visible"
    :return-regions="true"
    :selected="selectedData"
    :dark-mode="darkMode"
    :mode="mode"
    height="100%"
    :modal-props="{
      bodyStyle: { height: '460px', minHeight: '100%', maxHeight: '100%' },
      maxable: true,
      resizable: true,
      resizeIconStyle: { zIndex: 200 },
      minWidth: 372,
      minHeight: 280
    }"
    :side-style="{ maxWidth: '448px' }"
    @done="handleChoose"
  />
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { ArrowDown } from '@/components/icons';
  import type {
    PoiItem,
    SelectMode
  } from 'ele-admin-plus/es/ele-map-picker/types';
  import { useThemeStore } from '@/store/modules/theme';
  import { storeToRefs } from 'pinia';

  const themeStore = useThemeStore();
  const { darkMode } = storeToRefs(themeStore);

  /** 是否显示地图选择弹窗 */
  const visible = ref(false);

  /** 地点检索类型 */
  const mode = ref<SelectMode>('lnglat');

  /** 回显选中的位置 */
  const selectedData = ref<PoiItem>();

  /** 选择结果 */
  const result = reactive({
    location: '',
    address: '',
    lngAndLat: ''
  });

  /** 打开位置选择 */
  const openMapPicker = () => {
    visible.value = true;
  };

  /** 地图选择后回调 */
  const handleChoose = (location: PoiItem) => {
    console.log(JSON.parse(JSON.stringify(location)));
    result.location = `${location.city?.province}/${location.city?.city}/${location.city?.district}`;
    result.address = `${location.name} ${location.address}`;
    result.lngAndLat = `${location.lng},${location.lat}`;
    visible.value = false;
    selectedData.value = location;
  };
</script>
