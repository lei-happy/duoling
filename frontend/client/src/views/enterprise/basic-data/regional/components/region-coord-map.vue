<template>
  <div class="region-coord-map">
    <div ref="mapRef" class="region-coord-map-canvas"></div>
    <div class="region-coord-map-search">
      <el-autocomplete
        v-model="keywords"
        value-key="name"
        clearable
        placeholder="搜索地点"
        popper-class="region-coord-map-suggest"
        :fetch-suggestions="handleSearch"
        @select="handleSearchSelect"
      >
        <template #prefix>
          <el-icon class="el-input__icon">
            <Search />
          </el-icon>
        </template>
        <template #default="{ item }">
          <div class="region-coord-map-suggest-item">
            <div class="region-coord-map-suggest-title">{{ item.name }}</div>
            <div v-if="item.district" class="region-coord-map-suggest-text">
              {{ item.district }}
            </div>
          </div>
        </template>
      </el-autocomplete>
    </div>
    <div class="region-coord-map-tip">点击地图或搜索地点选择坐标</div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
  import AMapLoader from '@amap/amap-jsapi-loader';
  import { Search } from '@element-plus/icons-vue';

  type SuggestItem = {
    name: string;
    district?: string;
    address?: string;
    lng: number;
    lat: number;
  };

  const props = defineProps<{
    longitude?: string | number | null;
    latitude?: string | number | null;
    /** 输入建议城市范围，默认全国 */
    suggestionCity?: string;
  }>();

  const emit = defineEmits<{
    (e: 'change', payload: { lng: number; lat: number }): void;
  }>();

  const DEFAULT_CENTER: [number, number] = [104.0, 35.0];
  const DEFAULT_ZOOM = 5;
  const SELECTED_ZOOM = 14;

  const mapRef = ref<HTMLElement | null>(null);
  const keywords = ref('');
  let mapIns: any = null;
  let AMapNS: any = null;
  let marker: any = null;
  let autoCompleteIns: any = null;
  let lastSuggestion = '';
  let suggestionData: SuggestItem[] = [];
  let resizeTimer: ReturnType<typeof setTimeout> | null = null;

  const toCoord = (value: string | number | null | undefined) => {
    if (value === '' || value == null) return null;
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
  };

  const roundCoord = (n: number) => Math.round(n * 1e6) / 1e6;

  const hasSelected = () => {
    return toCoord(props.longitude) != null && toCoord(props.latitude) != null;
  };

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

  const applyPoint = (lng: number, lat: number) => {
    const nextLng = roundCoord(lng);
    const nextLat = roundCoord(lat);
    showMarker(nextLng, nextLat);
    mapIns?.setZoomAndCenter(SELECTED_ZOOM, [nextLng, nextLat]);
    emit('change', { lng: nextLng, lat: nextLat });
  };

  const syncSelected = (moveCenter = false) => {
    if (!mapIns) return;
    const lng = toCoord(props.longitude);
    const lat = toCoord(props.latitude);
    if (lng == null || lat == null) {
      destroyMarker();
      return;
    }
    showMarker(lng, lat);
    if (moveCenter) {
      mapIns.setZoomAndCenter(SELECTED_ZOOM, [lng, lat]);
    }
  };

  const scheduleResize = () => {
    if (resizeTimer) {
      clearTimeout(resizeTimer);
    }
    resizeTimer = window.setTimeout(() => {
      resizeTimer = null;
      mapIns?.resize?.();
      if (hasSelected()) {
        syncSelected(true);
      }
    }, 180);
  };

  const formatTip = (d: any): SuggestItem | null => {
    const location = d?.location;
    if (!location) return null;
    const lng =
      typeof location.getLng === 'function'
        ? location.getLng()
        : Number(location.lng);
    const lat =
      typeof location.getLat === 'function'
        ? location.getLat()
        : Number(location.lat);
    if (!Number.isFinite(lng) || !Number.isFinite(lat)) return null;
    return {
      name: d.name || '',
      district: d.district || '',
      address: Array.isArray(d.address) ? d.address[0] : d.address || '',
      lng,
      lat
    };
  };

  const searchKeywords = (keyword: string): Promise<SuggestItem[]> => {
    return new Promise((resolve, reject) => {
      if (!autoCompleteIns) {
        reject(new Error('AutoComplete instance is null'));
        return;
      }
      autoCompleteIns.search(keyword, (status: string, result: any) => {
        if (status === 'error') {
          reject(new Error(status));
          return;
        }
        if (!result?.tips) {
          resolve([]);
          return;
        }
        resolve(
          (result.tips as any[])
            .map((d) => formatTip(d))
            .filter((d): d is SuggestItem => !!d)
        );
      });
    });
  };

  const handleSearch = (
    keyword: string,
    callback: (data: SuggestItem[]) => void
  ) => {
    if (!keyword || lastSuggestion === keyword) {
      callback(suggestionData);
      return;
    }
    lastSuggestion = keyword;
    searchKeywords(keyword)
      .then((result) => {
        suggestionData = result;
        callback(suggestionData);
      })
      .catch((e) => {
        console.error(e);
        suggestionData = [];
        callback([]);
      });
  };

  const handleSearchSelect = (item: SuggestItem) => {
    if (!item || item.lng == null || item.lat == null) return;
    applyPoint(item.lng, item.lat);
  };

  const initMap = async () => {
    if (!mapRef.value || mapIns) return;
    try {
      AMapNS = await AMapLoader.load({
        key: import.meta.env.VITE_MAP_KEY,
        version: '2.0',
        plugins: ['AMap.Marker', 'AMap.Icon', 'AMap.AutoComplete']
      });
      const lng = toCoord(props.longitude);
      const lat = toCoord(props.latitude);
      const hasPoint = lng != null && lat != null;
      mapIns = new AMapNS.Map(mapRef.value, {
        zoom: hasPoint ? SELECTED_ZOOM : DEFAULT_ZOOM,
        center: hasPoint ? [lng, lat] : DEFAULT_CENTER,
        viewMode: '2D',
        resizeEnable: true
      });
      autoCompleteIns = new AMapNS.AutoComplete({
        city: props.suggestionCity || '全国'
      });
      if (hasPoint) {
        showMarker(lng, lat);
      }
      mapIns.on('click', (e: any) => {
        if (!e?.lnglat) return;
        applyPoint(e.lnglat.getLng(), e.lnglat.getLat());
      });
      await nextTick();
      scheduleResize();
    } catch (e) {
      console.error(e);
    }
  };

  onMounted(() => {
    void initMap();
  });

  onBeforeUnmount(() => {
    if (resizeTimer) {
      clearTimeout(resizeTimer);
      resizeTimer = null;
    }
    destroyMarker();
    autoCompleteIns = null;
    if (mapIns) {
      mapIns.destroy();
      mapIns = null;
    }
    AMapNS = null;
  });

  watch(
    () => [props.longitude, props.latitude],
    () => {
      syncSelected(false);
    }
  );

  watch(
    () => props.suggestionCity,
    (city) => {
      if (autoCompleteIns && city) {
        autoCompleteIns.setCity?.(city);
      }
    }
  );
</script>

<style scoped>
  .region-coord-map {
    position: relative;
    width: 100%;
    height: 360px;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 8px;
    overflow: hidden;
    background: var(--el-fill-color-lighter);
  }

  .region-coord-map-canvas {
    width: 100%;
    height: 100%;
  }

  .region-coord-map-search {
    position: absolute;
    top: 12px;
    left: 12px;
    right: 12px;
    z-index: 2;
  }

  .region-coord-map-search :deep(.el-autocomplete) {
    width: 100%;
  }

  .region-coord-map-search :deep(.el-input__wrapper) {
    background-color: #fff;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.12);
  }

  .region-coord-map-search :deep(.el-input__inner) {
    background-color: #fff;
  }

  .region-coord-map-tip {
    position: absolute;
    left: 12px;
    bottom: 12px;
    z-index: 1;
    padding: 4px 10px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.92);
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.4;
    pointer-events: none;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
</style>

<style>
  /* Element Plus 默认 li 固定高度会裁切双行建议项 */
  .region-coord-map-suggest.el-popper .el-autocomplete-suggestion__list > li {
    height: auto;
    line-height: normal;
    padding: 8px 12px;
  }

  .region-coord-map-suggest .region-coord-map-suggest-item {
    line-height: normal;
    box-sizing: border-box;
  }

  .region-coord-map-suggest .region-coord-map-suggest-title {
    color: var(--el-text-color-primary);
    font-size: 13px;
    line-height: 1.4;
    word-break: break-all;
  }

  .region-coord-map-suggest .region-coord-map-suggest-text {
    margin-top: 2px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.4;
    word-break: break-all;
  }
</style>
