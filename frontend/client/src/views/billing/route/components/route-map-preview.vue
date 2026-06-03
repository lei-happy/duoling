<template>
  <div class="route-map-preview">
    <div ref="mapRef" class="route-map-canvas"></div>
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
  import { useThemeStore } from '@/store/modules/theme';
  import { storeToRefs } from 'pinia';
  import type { RouteRegionPoint } from '@/api/resource/route/model';

  const props = defineProps<{
    /** 弹窗可见时触发地图 resize，避免容器未布局导致灰屏 */
    visible?: boolean;
    origin?: RouteRegionPoint | null;
    destination?: RouteRegionPoint | null;
    /** 驾车路线折线 [[lng, lat], ...] */
    path?: number[][] | null;
  }>();

  const themeStore = useThemeStore();
  const { darkMode } = storeToRefs(themeStore);

  /** 全国概览默认视野（无起终点时展示底图） */
  const DEFAULT_CENTER: [number, number] = [104.0, 35.0];
  const DEFAULT_ZOOM = 4;

  const mapRef = ref<HTMLElement | null>(null);
  let mapIns: any = null;
  let AMapNS: any = null;
  let originMarker: any = null;
  let destMarker: any = null;
  let routePolyline: any = null;

  const hasPoints = computed(
    () =>
      !!(
        props.origin?.longitude != null &&
        props.origin?.latitude != null &&
        props.destination?.longitude != null &&
        props.destination?.latitude != null
      )
  );

  const routePath = computed(() => {
    const raw = props.path;
    if (!raw?.length) return [];
    return raw.filter(
      (p) =>
        Array.isArray(p) &&
        p.length >= 2 &&
        Number.isFinite(p[0]) &&
        Number.isFinite(p[1])
    ) as [number, number][];
  });

  const destroyMarkers = () => {
    if (originMarker) {
      originMarker.setMap(null);
      originMarker = null;
    }
    if (destMarker) {
      destMarker.setMap(null);
      destMarker = null;
    }
  };

  const destroyPolyline = () => {
    if (routePolyline) {
      routePolyline.setMap(null);
      routePolyline = null;
    }
  };

  const updatePolyline = () => {
    destroyPolyline();
    if (!mapIns || !AMapNS || routePath.value.length < 2) return;

    routePolyline = new AMapNS.Polyline({
      path: routePath.value,
      strokeColor: '#1677ff',
      strokeWeight: 5,
      strokeOpacity: 0.85,
      lineJoin: 'round',
      lineCap: 'round',
      showDir: true
    });
    routePolyline.setMap(mapIns);
  };

  const resetMapView = () => {
    if (!mapIns) return;
    mapIns.setZoomAndCenter(DEFAULT_ZOOM, DEFAULT_CENTER);
  };

  const fitMapView = () => {
    if (!mapIns) return;
    const overlays: any[] = [];
    if (originMarker) overlays.push(originMarker);
    if (destMarker) overlays.push(destMarker);
    if (routePolyline) overlays.push(routePolyline);
    if (overlays.length) {
      mapIns.setFitView(overlays, false, [48, 48, 48, 48]);
    }
  };

  const updateMarkers = () => {
    if (!mapIns || !AMapNS) return;
    if (!hasPoints.value) {
      destroyMarkers();
      destroyPolyline();
      resetMapView();
      return;
    }

    const o = props.origin!;
    const d = props.destination!;
    const oPos: [number, number] = [o.longitude, o.latitude];
    const dPos: [number, number] = [d.longitude, d.latitude];

    destroyMarkers();

    originMarker = new AMapNS.Marker({
      position: oPos,
      title: o.name,
      anchor: 'bottom-center',
      label: {
        content: '<span class="route-map-label route-map-label-origin">起</span>',
        direction: 'top',
        offset: new AMapNS.Pixel(0, -2)
      }
    });
    destMarker = new AMapNS.Marker({
      position: dPos,
      title: d.name,
      anchor: 'bottom-center',
      label: {
        content: '<span class="route-map-label route-map-label-dest">终</span>',
        direction: 'top',
        offset: new AMapNS.Pixel(0, -2)
      }
    });

    originMarker.setMap(mapIns);
    destMarker.setMap(mapIns);
    updatePolyline();
    fitMapView();
  };

  const initMap = async () => {
    if (!mapRef.value || mapIns) return;
    try {
      AMapNS = await AMapLoader.load({
        key: import.meta.env.VITE_MAP_KEY,
        version: '2.0',
        plugins: ['AMap.Marker', 'AMap.Polyline']
      });
      mapIns = new AMapNS.Map(mapRef.value, {
        zoom: DEFAULT_ZOOM,
        center: DEFAULT_CENTER,
        viewMode: '2D',
        mapStyle: darkMode.value ? 'amap://styles/dark' : void 0
      });
      updateMarkers();
      await nextTick();
      mapIns.resize?.();
      window.setTimeout(() => mapIns?.resize?.(), 200);
    } catch (e) {
      console.error(e);
    }
  };

  const refreshMap = async () => {
    if (!mapIns) {
      await initMap();
      return;
    }
    updateMarkers();
    await nextTick();
    mapIns.resize?.();
  };

  onMounted(() => {
    void initMap();
  });

  onBeforeUnmount(() => {
    destroyMarkers();
    destroyPolyline();
    if (mapIns) {
      mapIns.destroy();
      mapIns = null;
    }
    AMapNS = null;
  });

  watch(
    () => [props.origin, props.destination, props.path],
    () => {
      void refreshMap();
    },
    { deep: true, immediate: true }
  );

  watch(darkMode, (value) => {
    if (mapIns) {
      mapIns.setMapStyle(value ? 'amap://styles/dark' : 'amap://styles/normal');
    }
  });

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      await nextTick();
      if (!mapIns) {
        await initMap();
      } else {
        mapIns.resize?.();
        updateMarkers();
      }
    }
  );
</script>

<style scoped>
  .route-map-preview {
    position: relative;
    width: 100%;
    aspect-ratio: 1 / 1;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-fill-color-lighter);
  }

  .route-map-canvas {
    width: 100%;
    height: 100%;
  }

  :deep(.amap-marker-label),
  :deep(.amap-marker-label-content) {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
  }

  :deep(.route-map-label) {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 22px;
    height: 22px;
    padding: 0 6px;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
    border: none;
    border-radius: 11px;
    color: #fff;
    white-space: nowrap;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
  }

  :deep(.route-map-label-origin) {
    background: #1677ff;
  }

  :deep(.route-map-label-dest) {
    background: #f5222d;
  }
</style>
