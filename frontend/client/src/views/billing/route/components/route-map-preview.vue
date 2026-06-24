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
  let fitTimer: ReturnType<typeof setTimeout> | null = null;

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

  const MARKER_ICON_SIZE = { w: 25, h: 34 };
  const MARKER_ICON_OFFSET = { x: -12, y: -28 };

  const createMarkerIcon = (kind: 'origin' | 'dest') => {
    const image =
      kind === 'origin'
        ? '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png'
        : '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png';
    return new AMapNS.Icon({
      size: new AMapNS.Size(MARKER_ICON_SIZE.w, MARKER_ICON_SIZE.h),
      image,
      imageSize: new AMapNS.Size(MARKER_ICON_SIZE.w, MARKER_ICON_SIZE.h)
    });
  };

  /** 收集起终点与折线坐标，用于计算视野 */
  const collectRoutePoints = (): [number, number][] => {
    const points: [number, number][] = [];
    if (hasPoints.value) {
      points.push(
        [props.origin!.longitude, props.origin!.latitude],
        [props.destination!.longitude, props.destination!.latitude]
      );
    }
    routePath.value.forEach((p) => points.push(p));
    return points;
  };

  const fitMapView = () => {
    if (!mapIns || !AMapNS) return;
    const points = collectRoutePoints();
    if (!points.length) return;

    let minLng = points[0][0];
    let maxLng = points[0][0];
    let minLat = points[0][1];
    let maxLat = points[0][1];
    for (const [lng, lat] of points) {
      minLng = Math.min(minLng, lng);
      maxLng = Math.max(maxLng, lng);
      minLat = Math.min(minLat, lat);
      maxLat = Math.max(maxLat, lat);
    }

    const minSpan = 0.08;
    if (maxLng - minLng < minSpan) {
      const pad = (minSpan - (maxLng - minLng)) / 2;
      minLng -= pad;
      maxLng += pad;
    }
    if (maxLat - minLat < minSpan) {
      const pad = (minSpan - (maxLat - minLat)) / 2;
      minLat -= pad;
      maxLat += pad;
    }

    const bounds = new AMapNS.Bounds(
      new AMapNS.LngLat(minLng, minLat),
      new AMapNS.LngLat(maxLng, maxLat)
    );
    // 顶部留更多空间给「起/终」标签；整体略放大边距，等效于 fit 后再缩小一级
    mapIns.setBounds(bounds, false, [72, 60, 60, 60]);
  };

  /** 等容器 layout / resize 完成后再适配，避免弹窗未展开时 fit 失败 */
  const scheduleFitMapView = () => {
    if (fitTimer) {
      clearTimeout(fitTimer);
    }
    fitTimer = window.setTimeout(() => {
      fitTimer = null;
      if (!mapIns) return;
      mapIns.resize?.();
      fitMapView();
    }, 180);
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
      icon: createMarkerIcon('origin'),
      offset: new AMapNS.Pixel(MARKER_ICON_OFFSET.x, MARKER_ICON_OFFSET.y),
      label: {
        content: '<span class="route-map-label route-map-label-origin">起</span>',
        direction: 'top',
        offset: new AMapNS.Pixel(0, -2)
      }
    });
    destMarker = new AMapNS.Marker({
      position: dPos,
      title: d.name,
      icon: createMarkerIcon('dest'),
      offset: new AMapNS.Pixel(MARKER_ICON_OFFSET.x, MARKER_ICON_OFFSET.y),
      label: {
        content: '<span class="route-map-label route-map-label-dest">终</span>',
        direction: 'top',
        offset: new AMapNS.Pixel(0, -2)
      }
    });

    originMarker.setMap(mapIns);
    destMarker.setMap(mapIns);
    updatePolyline();
    scheduleFitMapView();
  };

  const initMap = async () => {
    if (!mapRef.value || mapIns) return;
    try {
      AMapNS = await AMapLoader.load({
        key: import.meta.env.VITE_MAP_KEY,
        version: '2.0',
        plugins: ['AMap.Marker', 'AMap.Polyline', 'AMap.Icon']
      });
      mapIns = new AMapNS.Map(mapRef.value, {
        zoom: DEFAULT_ZOOM,
        center: DEFAULT_CENTER,
        viewMode: '2D',
        mapStyle: darkMode.value ? 'amap://styles/dark' : void 0
      });
      updateMarkers();
      await nextTick();
      scheduleFitMapView();
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
    scheduleFitMapView();
  };

  onMounted(() => {
    void initMap();
  });

  onBeforeUnmount(() => {
    if (fitTimer) {
      clearTimeout(fitTimer);
      fitTimer = null;
    }
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
        updateMarkers();
        scheduleFitMapView();
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
