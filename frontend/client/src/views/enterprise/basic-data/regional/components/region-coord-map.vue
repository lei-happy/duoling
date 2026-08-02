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
    <div class="region-coord-map-tip">{{ tipText }}</div>
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue';
  import AMapLoader from '@amap/amap-jsapi-loader';
  import { EleMessage } from 'ele-admin-plus';
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
    /** 上级行政区划代码（adcode），用于搜索偏置与落点校验 */
    parentCode?: string;
    /** 上级地区名称，用于提示文案 */
    parentName?: string;
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
  let boundaryPolygons: any[] = [];
  let autoCompleteIns: any = null;
  let geocoderIns: any = null;
  let lastSuggestion = '';
  let suggestionData: SuggestItem[] = [];
  let resizeTimer: ReturnType<typeof setTimeout> | null = null;
  let applyingPoint = false;

  const tipText = computed(() => {
    const name = props.parentName?.trim();
    if (name) {
      return `请在「${name}」范围内点选或搜索`;
    }
    return '请在当前上级地区范围内点选或搜索';
  });

  const toCoord = (value: string | number | null | undefined) => {
    if (value === '' || value == null) return null;
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
  };

  const roundCoord = (n: number) => Math.round(n * 1e6) / 1e6;

  const hasSelected = () => {
    return toCoord(props.longitude) != null && toCoord(props.latitude) != null;
  };

  const normalizeAdcode = (code?: string | null) => {
    const raw = (code || '').trim();
    if (!raw) return '';
    // 国标多为 6 位；不足补 0，便于前缀比较
    return raw.padEnd(6, '0').slice(0, 6);
  };

  /**
   * 判断点的 adcode 是否属于上级行政区。
   * - 区县：全码相等
   * - 市（xx yy 00）：前 4 位一致
   * - 省（xx 0000）：前 2 位一致
   */
  const isAdcodeWithinParent = (pointAdcode: string, parentCode: string) => {
    const point = normalizeAdcode(pointAdcode);
    const parent = normalizeAdcode(parentCode);
    if (!point || !parent) return false;
    if (parent.endsWith('0000')) {
      return point.slice(0, 2) === parent.slice(0, 2);
    }
    if (parent.endsWith('00')) {
      return point.slice(0, 4) === parent.slice(0, 4);
    }
    return point === parent;
  };

  const outOfRangeMessage = () => {
    const name = props.parentName?.trim();
    if (name) {
      return `所选位置不在「${name}」范围内，请在当前地区内重新选择`;
    }
    return '所选位置不在当前上级地区范围内，请重新选择';
  };

  const destroyMarker = () => {
    if (marker) {
      marker.setMap(null);
      marker = null;
    }
  };

  const clearBoundary = () => {
    boundaryPolygons.forEach((p) => {
      p.setMap?.(null);
    });
    boundaryPolygons = [];
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

  const reverseGeocodeAdcode = (lng: number, lat: number): Promise<string> => {
    return new Promise((resolve, reject) => {
      if (!geocoderIns) {
        reject(new Error('Geocoder instance is null'));
        return;
      }
      geocoderIns.getAddress([lng, lat], (status: string, result: any) => {
        if (status !== 'complete' || !result?.regeocode) {
          reject(new Error(status || 'regeocode_failed'));
          return;
        }
        const adcode =
          result.regeocode.addressComponent?.adcode ||
          result.regeocode.addressComponent?.towncode ||
          '';
        resolve(String(adcode || ''));
      });
    });
  };

  /** 校验坐标是否落在上级行政区内；无 parentCode 时视为通过 */
  const validatePointInParent = async (
    lng: number,
    lat: number,
    options?: { silent?: boolean }
  ): Promise<boolean> => {
    const parentCode = props.parentCode?.trim();
    if (!parentCode) return true;
    try {
      const adcode = await reverseGeocodeAdcode(lng, lat);
      if (!adcode || !isAdcodeWithinParent(adcode, parentCode)) {
        if (!options?.silent) {
          EleMessage.warning({ message: outOfRangeMessage(), plain: true });
        }
        return false;
      }
      return true;
    } catch (e) {
      console.error(e);
      if (!options?.silent) {
        EleMessage.error({
          message: '无法确认所选位置所属地区，请稍后重试',
          plain: true
        });
      }
      return false;
    }
  };

  const commitPoint = (lng: number, lat: number) => {
    const nextLng = roundCoord(lng);
    const nextLat = roundCoord(lat);
    showMarker(nextLng, nextLat);
    mapIns?.setZoomAndCenter(SELECTED_ZOOM, [nextLng, nextLat]);
    emit('change', { lng: nextLng, lat: nextLat });
  };

  const applyPoint = async (lng: number, lat: number) => {
    if (applyingPoint) return;
    applyingPoint = true;
    try {
      const ok = await validatePointInParent(lng, lat);
      if (!ok) return;
      commitPoint(lng, lat);
    } finally {
      applyingPoint = false;
    }
  };

  /** 供保存前复验当前表单坐标 */
  const validateCurrentPoint = async (): Promise<boolean> => {
    const lng = toCoord(props.longitude);
    const lat = toCoord(props.latitude);
    if (lng == null || lat == null) {
      EleMessage.warning({
        message: '请在地图上点选位置',
        plain: true
      });
      return false;
    }
    return validatePointInParent(lng, lat);
  };

  defineExpose({ validateCurrentPoint });

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

  const searchCity = () => props.parentCode?.trim() || '全国';

  const applySearchCity = (code?: string) => {
    if (!autoCompleteIns) return;
    autoCompleteIns.setCity?.(code?.trim() || '全国');
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
    void applyPoint(item.lng, item.lat);
  };

  const districtLevelOf = (code: string) => {
    const parent = normalizeAdcode(code);
    if (!parent) return 'district';
    if (parent.endsWith('0000')) return 'province';
    if (parent.endsWith('00')) return 'city';
    return 'district';
  };

  const fitParentDistrict = (code: string) => {
    if (!mapIns || !AMapNS || !code) return;
    const district = new AMapNS.DistrictSearch({
      level: districtLevelOf(code),
      extensions: 'all',
      subdistrict: 0
    });
    district.search(code, (status: string, result: any) => {
      if (status !== 'complete' || !result?.districtList?.length) return;
      const info = result.districtList[0];
      const bounds = info.boundaries;
      if (!bounds?.length) {
        if (info.center) {
          mapIns.setZoomAndCenter(11, [info.center.lng, info.center.lat]);
        }
        return;
      }
      clearBoundary();
      const polygons: any[] = [];
      for (let i = 0; i < bounds.length; i++) {
        const polygon = new AMapNS.Polygon({
          path: bounds[i],
          strokeWeight: 1.5,
          strokeColor: '#409eff',
          fillColor: '#409eff',
          fillOpacity: 0.08
        });
        polygon.setMap(mapIns);
        polygons.push(polygon);
      }
      boundaryPolygons = polygons;
      if (!hasSelected()) {
        mapIns.setFitView(polygons);
      }
    });
  };

  const initMap = async () => {
    if (!mapRef.value || mapIns) return;
    try {
      AMapNS = await AMapLoader.load({
        key: import.meta.env.VITE_MAP_KEY,
        version: '2.0',
        plugins: [
          'AMap.Marker',
          'AMap.Icon',
          'AMap.AutoComplete',
          'AMap.Geocoder',
          'AMap.DistrictSearch'
        ]
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
      geocoderIns = new AMapNS.Geocoder({ radius: 500, extensions: 'base' });
      autoCompleteIns = new AMapNS.AutoComplete({
        city: searchCity()
      });
      if (hasPoint) {
        showMarker(lng, lat);
      }
      const parentCode = props.parentCode?.trim();
      if (parentCode) {
        fitParentDistrict(parentCode);
      }
      mapIns.on('click', (e: any) => {
        if (!e?.lnglat) return;
        void applyPoint(e.lnglat.getLng(), e.lnglat.getLat());
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
    clearBoundary();
    autoCompleteIns = null;
    geocoderIns = null;
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
    () => props.parentCode,
    (code) => {
      applySearchCity(code);
      if (code?.trim() && mapIns && AMapNS) {
        fitParentDistrict(code.trim());
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
    max-width: calc(100% - 24px);
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
