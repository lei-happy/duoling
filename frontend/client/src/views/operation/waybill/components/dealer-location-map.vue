<!-- 收车门店位置只读预览（高德） -->
<template>
  <div class="dealer-location-map">
    <div
      v-show="hasCoords"
      ref="mapRef"
      class="dealer-location-map__canvas"
    />
    <div v-if="!hasCoords" class="dealer-location-map__empty">
      <el-icon :size="28" class="dealer-location-map__empty-icon">
        <Location />
      </el-icon>
      <p class="dealer-location-map__empty-title">{{ emptyTitle }}</p>
      <p v-if="emptyHint" class="dealer-location-map__empty-hint">
        {{ emptyHint }}
      </p>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import {
    ref,
    computed,
    watch,
    nextTick,
    onMounted,
    onBeforeUnmount
  } from 'vue';
  import AMapLoader from '@amap/amap-jsapi-loader';
  import { Location } from '@element-plus/icons-vue';

  const props = withDefaults(
    defineProps<{
      longitude?: string | number | null;
      latitude?: string | number | null;
      /** 所在步骤可见时触发 resize，避免容器未布局导致灰屏 */
      visible?: boolean;
      /** 是否已选择门店（用于空态文案） */
      hasDealer?: boolean;
    }>(),
    {
      visible: true,
      hasDealer: false
    }
  );

  const DEFAULT_CENTER: [number, number] = [104.0, 35.0];
  const DEFAULT_ZOOM = 5;
  const SELECTED_ZOOM = 15;

  const mapRef = ref<HTMLElement | null>(null);
  let mapIns: any = null;
  let AMapNS: any = null;
  let marker: any = null;
  let resizeTimer: number | null = null;
  let initPromise: Promise<void> | null = null;

  const toCoord = (value: string | number | null | undefined) => {
    if (value === '' || value == null) return null;
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
  };

  const hasCoords = computed(() => {
    return toCoord(props.longitude) != null && toCoord(props.latitude) != null;
  });

  const emptyTitle = computed(() =>
    props.hasDealer ? '该门店暂无位置信息' : '请选择收车门店'
  );

  const emptyHint = computed(() =>
    props.hasDealer ? '请先在门店资料中完善经纬度后再查看地图' : ''
  );

  const destroyMarker = () => {
    if (marker) {
      marker.setMap(null);
      marker = null;
    }
  };

  const showMarker = (lng: number, lat: number) => {
    if (!mapIns || !AMapNS) return;
    const position: [number, number] = [lng, lat];
    if (!marker) {
      marker = new AMapNS.Marker({
        position,
        icon: new AMapNS.Icon({
          size: new AMapNS.Size(25, 34),
          image:
            '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
          imageSize: new AMapNS.Size(25, 34)
        }),
        offset: new AMapNS.Pixel(-12, -28)
      });
      marker.setMap(mapIns);
    } else {
      marker.setPosition(position);
    }
  };

  const syncSelected = (moveCenter = false) => {
    if (!mapIns) return;
    const lng = toCoord(props.longitude);
    const lat = toCoord(props.latitude);
    if (lng == null || lat == null) {
      destroyMarker();
      mapIns.setZoomAndCenter(DEFAULT_ZOOM, DEFAULT_CENTER);
      return;
    }
    showMarker(lng, lat);
    if (moveCenter) {
      mapIns.setZoomAndCenter(SELECTED_ZOOM, [lng, lat]);
    }
  };

  const scheduleResize = () => {
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      resizeTimer = null;
      mapIns?.resize?.();
      if (hasCoords.value) syncSelected(true);
    }, 180);
  };

  const initMap = async () => {
    if (!mapRef.value || mapIns) return;
    if (initPromise) {
      await initPromise;
      return;
    }
    initPromise = (async () => {
      try {
        AMapNS = await AMapLoader.load({
          key: import.meta.env.VITE_MAP_KEY,
          version: '2.0',
          plugins: ['AMap.Marker', 'AMap.Icon']
        });
        if (!mapRef.value) return;
        const lng = toCoord(props.longitude);
        const lat = toCoord(props.latitude);
        const hasPoint = lng != null && lat != null;
        mapIns = new AMapNS.Map(mapRef.value, {
          zoom: hasPoint ? SELECTED_ZOOM : DEFAULT_ZOOM,
          center: hasPoint ? [lng, lat] : DEFAULT_CENTER,
          viewMode: '2D',
          resizeEnable: true,
          dragEnable: true,
          zoomEnable: true,
          doubleClickZoom: false
        });
        if (hasPoint) showMarker(lng!, lat!);
        await nextTick();
        scheduleResize();
      } catch (e) {
        console.error(e);
      } finally {
        initPromise = null;
      }
    })();
    await initPromise;
  };

  const ensureMap = async () => {
    if (!hasCoords.value) return;
    await nextTick();
    if (!mapIns) await initMap();
    else scheduleResize();
  };

  onMounted(() => {
    if (props.visible && hasCoords.value) void ensureMap();
  });

  onBeforeUnmount(() => {
    if (resizeTimer) {
      clearTimeout(resizeTimer);
      resizeTimer = null;
    }
    destroyMarker();
    if (mapIns) {
      mapIns.destroy();
      mapIns = null;
    }
    AMapNS = null;
  });

  watch(
    () => [props.longitude, props.latitude] as const,
    async () => {
      if (!hasCoords.value) {
        destroyMarker();
        return;
      }
      await ensureMap();
      syncSelected(true);
    }
  );

  watch(
    () => props.visible,
    (v) => {
      if (v && hasCoords.value) void ensureMap();
    }
  );
</script>

<style scoped>
  .dealer-location-map {
    position: relative;
    width: 100%;
    height: 320px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    overflow: hidden;
    background: var(--el-fill-color-lighter);
  }

  .dealer-location-map__canvas {
    width: 100%;
    height: 100%;
  }

  .dealer-location-map__empty {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 16px;
    text-align: center;
  }

  .dealer-location-map__empty-icon {
    color: var(--el-text-color-placeholder);
  }

  .dealer-location-map__empty-title {
    margin: 0;
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.4;
  }

  .dealer-location-map__empty-hint {
    margin: 0;
    font-size: 12px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
  }
</style>
