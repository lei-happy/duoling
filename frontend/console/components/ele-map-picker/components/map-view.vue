<template>
  <EleLoading
    :loading="loading"
    class="ele-map-view"
    :class="{ 'is-poi-mode': poiMode }"
    :style="{ height }"
  >
    <div class="ele-map-view-body">
      <div ref="mapRef" :style="{ height: '100%' }"></div>
      <template v-if="poiMode">
        <ElIcon class="ele-map-view-icon-plus">
          <PlusOutlined />
        </ElIcon>
        <img :src="markerSrc" :class="centerIconClass" />
      </template>
      <div
        v-if="filterable && !keywordMode"
        class="ele-map-view-search"
        :style="searchStyle"
      >
        <ElAutocomplete
          ref="autocompleteRef"
          valueKey="name"
          :clearable="true"
          v-model="keywords"
          :placeholder="searchPlaceholder"
          popperClass="ele-map-suggest-popper"
          :fetchSuggestions="handleSearch"
          @select="handleSearchSelect"
        >
          <template #prefix>
            <ElIcon class="el-input__icon">
              <SearchOutlined />
            </ElIcon>
          </template>
          <template #default="{ item }">
            <div class="ele-map-suggest-item">
              <div class="ele-map-suggest-title">{{ item.name }}</div>
              <div class="ele-map-suggest-text">{{ item.district }}</div>
            </div>
          </template>
        </ElAutocomplete>
      </div>
      <template v-if="!poiMode && !keywordMode">
        <div
          v-if="confirmDisabled && clickMessage"
          class="ele-map-view-message"
        >
          {{ clickMessage }}
        </div>
        <ElButton
          v-else
          type="primary"
          :loading="confirmLoading"
          :disabled="confirmDisabled"
          class="ele-map-view-btn-ok"
          @click="handleConfirm"
        >
          {{ okText }}
        </ElButton>
      </template>
    </div>
    <EleLoading
      v-if="keywordMode || poiMode"
      :loading="poiLoading"
      :style="sideStyle"
      class="ele-map-view-side"
    >
      <div v-if="keywordMode" class="ele-map-view-search" :style="searchStyle">
        <ElInput
          :clearable="true"
          v-model="keywords"
          :prefixIcon="SearchOutlined"
          :placeholder="searchPlaceholder"
          :validateEvent="false"
          @change="handleSearch"
        />
      </div>
      <div ref="listRef" class="ele-map-view-list">
        <div
          v-for="item in data"
          :key="item.key"
          class="ele-map-view-item"
          :class="{ 'is-active': item === current }"
          @click="handleItemClick(item)"
        >
          <ElIcon class="ele-map-view-item-icon">
            <EnvironmentOutlined />
          </ElIcon>
          <div class="ele-map-view-item-body">
            <div
              v-if="!item.name && !item.address"
              class="ele-map-view-item-title"
            >
              <span>{{ item.lng }}</span>
              <span>,</span>
              <span>{{ item.lat }}</span>
            </div>
            <template v-else>
              <div class="ele-map-view-item-title">{{ item.name }}</div>
              <div v-if="item.address" class="ele-map-view-item-text">
                {{ item.address }}
              </div>
            </template>
          </div>
          <ElIcon class="ele-map-view-item-radio">
            <CheckCircleOutlined />
          </ElIcon>
        </div>
        <div v-if="!data || !data.length" class="ele-map-view-empty">
          <ElEmpty :imageSize="80" v-bind="emptyProps || {}" />
        </div>
      </div>
      <div class="ele-map-view-extra">
        <div v-if="confirmDisabled && message" class="ele-map-view-message">
          {{ message }}
        </div>
        <ElButton
          v-else
          type="primary"
          :loading="confirmLoading"
          :disabled="confirmDisabled"
          class="ele-map-view-btn-ok"
          @click="handleConfirm"
        >
          {{ okText }}
        </ElButton>
      </div>
    </EleLoading>
  </EleLoading>
</template>

<script lang="ts" setup>
  import {
    ref,
    computed,
    onMounted,
    onBeforeUnmount,
    nextTick,
    inject,
    watch
  } from 'vue';
  import AMapLoader from '@amap/amap-jsapi-loader';
  import {
    ElAutocomplete,
    ElInput,
    ElButton,
    ElIcon,
    ElEmpty
  } from 'element-plus';
  import {
    PlusOutlined,
    EnvironmentOutlined,
    CheckCircleOutlined,
    SearchOutlined
  } from '../../icons/index';
  import type { ElAutocompleteInstance } from '../../ele-app/el';
  import { modalItemContextKey } from '../../utils/hook';
  import EleLoading from '../../ele-loading/index.vue';
  import type { PoiItem, City, MapState } from '../types';
  import { mapProps } from '../props';
  const ICON_CLASS = 'ele-map-view-body-icon';

  defineOptions({ name: 'MapView' });

  const props = defineProps(mapProps);

  const emit = defineEmits({
    mapDone: (_ins: any) => true,
    select: (_selected: PoiItem | null) => true,
    done: (_result: PoiItem) => true
  });

  const state: MapState = { context: inject(modalItemContextKey, null) };

  /** 地图节点 */
  const mapRef = ref<HTMLDivElement | null>(null);

  /** 搜索建议实例 */
  const autocompleteRef = ref<ElAutocompleteInstance>(null);

  /** 列表节点 */
  const listRef = ref<HTMLDivElement | null>(null);

  /** 地图渲染状态 */
  const loading = ref<boolean>(true);

  /** 列表请求状态 */
  const poiLoading = ref<boolean>(false);

  /** 确定按钮请求状态 */
  const confirmLoading = ref<boolean>(false);

  /** POI数据 */
  const data = ref<PoiItem[]>([]);

  /** 输入建议数据 */
  const suggestionData = ref<PoiItem[]>([]);

  /** 地图中心图标类名 */
  const centerIconClass = ref([ICON_CLASS]);

  /** 输入建议关键字 */
  const keywords = ref<string>('');

  /** 选中数据 */
  const current = ref<PoiItem | null | undefined>(null);

  /** 确定按钮是否禁用 */
  const confirmDisabled = computed(() => props.required && !current.value);

  /** 是否是关键字搜索模式 */
  const keywordMode = computed<boolean>(() => 'keyword' === props.mode);

  /** 是否是POI搜索模式 */
  const poiMode = computed<boolean>(() => 'poi' === props.mode);

  /** 获取初始回显位置 */
  const getInitSelected = () => {
    if (props.selected != null) {
      const { lng, lat } = props.selected;
      if (lat != null && lng != null) {
        return props.selected;
      }
    }
  };

  /** 判断是否是相同的POI数据 */
  const isSamePOI = (poi: PoiItem, item: PoiItem): boolean => {
    return (
      item.lat === poi.lat &&
      item.lng === poi.lng &&
      item.name === poi.name &&
      item.address === poi.address
    );
  };

  /** 指定POI数据添加到首位 */
  const addFirstPOI = (poi: PoiItem, list: PoiItem[]): PoiItem[] => {
    const index = list.findIndex((d) => isSamePOI(poi, d));
    if (index == -1) {
      return [poi, ...list];
    }
    const result = [...list];
    result[index] = poi;
    return result;
  };

  /** 判断行政区数据是否为空 */
  const isNullCity = (city?: City) => {
    if (
      city == null ||
      typeof city !== 'object' ||
      (city.province == null &&
        city.city == null &&
        city.district == null &&
        city.citycode == null)
    ) {
      return true;
    }
    return false;
  };

  /** 处理POI数据 */
  const formatPOI = (d: PoiItem): PoiItem => {
    const name = d.name || '';
    const addr = Array.isArray(d.address) ? d.address[0] : d.address;
    const address = addr || '';
    const { lat, lng } = d.location;
    const city = isNullCity(d.city) ? void 0 : d.city;
    const key = [name, address, lat, lng].join(',');
    return { ...d, name, address, lat, lng, city, key };
  };

  /** 列表滚动顶部 */
  const scrollToTop = () => {
    const listEl = listRef.value;
    if (listEl) {
      listEl.scrollTop = 0;
    }
  };

  /** 列表滚动到选中位置 */
  const scrollToActive = () => {
    const listEl = listRef.value;
    if (listEl) {
      const el = listEl.querySelector('.ele-map-view-item.is-active');
      if (el) {
        if (typeof el['scrollIntoViewIfNeeded'] === 'function') {
          (el as any).scrollIntoViewIfNeeded(true);
        } else {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }
  };

  /** 设置选中 */
  const setSelected = (item: PoiItem | null, trigger?: boolean) => {
    if (current.value !== item) {
      current.value = item;
      if (trigger) {
        emit('select', current.value);
      }
    }
  };

  /** 关键字检索 */
  const searchKeywords = (keyword: string): Promise<PoiItem[]> => {
    return new Promise((resolve, reject) => {
      if (!state.autoCompleteIns) {
        reject(new Error('AutoComplete instance is null'));
        return;
      }
      state.autoCompleteIns.search(keyword, (status: any, result: any) => {
        if (status === 'error') {
          const msg = `${status} ${result ? JSON.stringify(result) : ''}`;
          reject(new Error(msg));
          return;
        }
        if (!result?.tips) {
          resolve([]);
          return;
        }
        const tips = (result.tips as PoiItem[]).filter((d) => !!d.location);
        resolve(tips.map((d) => formatPOI(d)));
      });
    });
  };

  /** 检索附近兴趣点 */
  const searchNearBy = (lng: number, lat: number): Promise<PoiItem[]> => {
    return new Promise((resolve, reject) => {
      if (!state.placeSearchIns) {
        reject(new Error('PlaceSearch instance is null'));
        return;
      }
      state.placeSearchIns.searchNearBy(
        props.poiKeywords,
        [lng, lat],
        props.poiRadius,
        (status: string, result: any) => {
          if (status === 'complete' && result?.poiList?.pois) {
            const ps = result.poiList.pois.filter((d: any) => !!d.location);
            resolve((ps as PoiItem[]).map((d) => formatPOI(d)));
            return;
          }
          if (status === 'no_data') {
            resolve([]);
            return;
          }
          const msg = `${status} ${result ? JSON.stringify(result) : ''}`;
          reject(new Error(msg));
        }
      );
    });
  };

  /** 检索POI数据 */
  const searchPOI = (lng: number, lat: number) => {
    loading.value = true;
    poiLoading.value = true;
    searchNearBy(lng, lat)
      .then((result) => {
        poiLoading.value = false;
        loading.value = false;
        if (!state.selectedSuggestion) {
          data.value = result;
          setSelected(null, true);
          scrollToTop();
          return;
        }
        // 选中的输入建议不在POI中则添加
        data.value = addFirstPOI(state.selectedSuggestion, result);
        setSelected(state.selectedSuggestion, true);
        state.selectedSuggestion = null;
        nextTick(() => {
          scrollToActive;
        });
      })
      .catch((e) => {
        console.error(e);
        poiLoading.value = false;
        loading.value = false;
        const selectedSuggestion = state.selectedSuggestion;
        data.value = selectedSuggestion ? [selectedSuggestion] : [];
        setSelected(selectedSuggestion ? selectedSuggestion : null, true);
      });
  };

  /** 让地图中心图标跳动 */
  const bounceIcon = () => {
    centerIconClass.value = [ICON_CLASS];
    nextTick(() => {
      setTimeout(() => {
        centerIconClass.value = [ICON_CLASS, 'ele-map-view-anim-bounce'];
      }, 0);
    });
  };

  /** 移除地图中心标记点 */
  const removeCenterMarker = () => {
    if (state.centerMarker && state.mapIns) {
      state.mapIns.remove(state.centerMarker);
    }
  };

  /** 添加地图中心标记点 */
  const showCenterMarker = (lng?: number, lat?: number) => {
    if (!state.centerMarker) {
      console.error('centerMarker is null');
      return;
    }
    if (!state.mapIns) {
      console.error('map instance is null');
      return;
    }
    removeCenterMarker();
    if (lng != null && lat != null) {
      state.centerMarker.setPosition([lng, lat]);
      state.mapIns.add(state.centerMarker);
    }
  };

  /** 设置地图中心点 */
  const setMapCenter = (lng?: number, lat?: number, zoom?: number) => {
    if (state.mapIns && lng != null && lat != null) {
      if (zoom == null) {
        state.mapIns.setCenter([lng, lat]);
      } else {
        state.mapIns.setZoomAndCenter(zoom, [lng, lat]);
      }
    }
  };

  /** 获取地图中心点 */
  const getMapCenter = (returnRegions: boolean): Promise<PoiItem> => {
    return new Promise((resolve, reject) => {
      if (!state.mapIns) {
        reject(new Error('map instance is null'));
        return;
      }
      const result = state.mapIns.getCenter();
      if (!returnRegions) {
        resolve(result || {});
        return;
      }
      state.mapIns.getCity((city: City) => {
        resolve({ ...(result || {}), city });
      });
    });
  };

  /** 切换地图主题 */
  const changeMapStyle = (style: string | boolean) => {
    if (state.mapIns) {
      if (typeof style === 'boolean') {
        if (style) {
          state.mapIns.setMapStyle('amap://styles/dark');
        } else {
          state.mapIns.setMapStyle('amap://styles/normal');
        }
      } else if (style) {
        state.mapIns.setMapStyle(style);
      }
    }
  };

  /** 销毁地图 */
  const destroyMap = () => {
    state.mapIns && state.mapIns.destroy();
    state.centerMarker = null;
    state.placeSearchIns = null;
    state.autoCompleteIns = null;
    state.mapIns = null;
  };

  /** 销毁数据 */
  const destroyAll = () => {
    destroyMap();
    state.lastSuggestion = '';
    state.selectedSuggestion = null;
    state.isItemClickMove = false;
    data.value = [];
    suggestionData.value = [];
    keywords.value = '';
    setSelected(null);
  };

  /** 渲染地图 */
  const renderMap = () => {
    if (!props.mapKey || state.mapIns) {
      return;
    }
    AMapLoader.load({
      key: props.mapKey,
      version: props.mapVersion,
      plugins: ['AMap.PlaceSearch', 'AMap.AutoComplete']
    })
      .then((AMap) => {
        destroyAll();

        // 地图中心标记点
        state.centerMarker = new AMap.Marker({
          icon: new AMap.Icon({
            image: props.markerSrc,
            size: new AMap.Size(26, 36.5),
            imageSize: new AMap.Size(26, 36.5)
          }),
          offset: new AMap.Pixel(-13, -36.5)
        });

        // 获取输入建议实例
        state.autoCompleteIns = new AMap.AutoComplete({
          city: props.suggestionCity
        });

        // 获取POI检索实例
        state.placeSearchIns = new AMap.PlaceSearch({
          type: props.poiType,
          pageSize: props.poiLimit,
          pageIndex: 1
        });

        // 渲染地图
        const selected = getInitSelected();
        const selCenter = selected ? [selected.lng, selected.lat] : void 0;
        const defaultStyle = props.darkMode ? 'amap://styles/dark' : void 0;
        state.mapIns = new AMap.Map(mapRef.value, {
          zoom: selected == null ? props.zoom : props.selectedZoom, // 初缩放级别
          center: selCenter || props.center, // 初始中心点
          resizeEnable: true, // 监控地图容器尺寸变化
          mapStyle: props.mapStyle || defaultStyle
        });

        // 地图加载完成事件
        state.mapIns.on('complete', () => {
          const selected = getInitSelected();
          if (selected != null) {
            setSelected(selected);
            if (!poiMode.value) {
              const { lng, lat } = selected;
              showCenterMarker(lng, lat);
            }
          }
          if (poiMode.value || keywordMode.value) {
            state.selectedSuggestion = selected;
            const { lng, lat } = state.mapIns.getCenter();
            searchPOI(lng, lat);
            return;
          }
          loading.value = false;
        });

        // 地图移动结束事件
        state.mapIns.on('moveend', () => {
          if (state.isItemClickMove || !poiMode.value) {
            state.isItemClickMove = false;
            return;
          }
          bounceIcon();
          const { lng, lat } = state.mapIns.getCenter();
          searchPOI(lng, lat);
        });

        // 地图点击事件
        state.mapIns.on('click', (e: any) => {
          if (poiMode.value || keywordMode.value) {
            return;
          }
          if (e.lnglat == null || typeof e.lnglat !== 'object') {
            console.error(e);
            return;
          }
          const { lng, lat } = e.lnglat;
          setSelected(formatPOI({ location: { lat, lng } }), true);
          setMapCenter(lng, lat, props.selectedZoom);
          showCenterMarker(lng, lat);
        });

        // 地图渲染完成
        emit('mapDone', state.mapIns);
      })
      .catch((e) => {
        console.error(e);
      });
  };

  /** 获取地图实例 */
  const getMapIns = () => {
    return state.mapIns;
  };

  /** 展示初始回显位置 */
  const showInitSelected = () => {
    const selected = getInitSelected();
    if (state.mapIns == null || selected == null) {
      return;
    }
    setSelected(selected);
    const { lng, lat } = selected;
    state.isItemClickMove = true;
    setMapCenter(lng, lat, props.selectedZoom);
    if (!poiMode.value) {
      showCenterMarker(lng, lat);
    }
    if (
      (keywordMode.value || poiMode.value) &&
      !data.value.includes(selected)
    ) {
      data.value = addFirstPOI(selected, data.value);
    }
    nextTick(() => {
      scrollToActive();
    });
  };

  /** 搜索建议获取数据 */
  const handleSearch = (keyword: string, callback?: any) => {
    if (!keyword || state.lastSuggestion === keyword) {
      callback && callback(suggestionData.value);
      return;
    }
    state.lastSuggestion = keyword;
    if (keywordMode.value) {
      poiLoading.value = true;
    }
    searchKeywords(keyword)
      .then((result) => {
        // 关键字检索模式
        if (keywordMode.value) {
          data.value = result;
          poiLoading.value = false;
          setSelected(null, true);
          removeCenterMarker();
          scrollToTop();
          return;
        }
        suggestionData.value = result;
        callback && callback(suggestionData.value);
      })
      .catch((e: Error) => {
        console.error(e);
        poiLoading.value = false;
        callback && callback(suggestionData.value);
      });
  };

  /** 搜索建议选中事件 */
  const handleSearchSelect = (item: PoiItem) => {
    autocompleteRef.value && autocompleteRef.value.blur();
    if (!item) {
      return;
    }
    const { lng, lat } = item;
    if (lng == null || lat == null) {
      return;
    }
    if (!poiMode.value) {
      showCenterMarker(lng, lat);
      setMapCenter(lng, lat, props.selectedZoom);
      setSelected(item, true);
      return;
    }
    loading.value = true;
    state.selectedSuggestion = item;
    state.isItemClickMove = true;
    setMapCenter(lng, lat, props.selectedZoom);
    bounceIcon();
    searchPOI(lng, lat);
  };

  /** POI列表条目点击事件 */
  const handleItemClick = (item: PoiItem) => {
    state.isItemClickMove = true;
    setSelected(item, true);
    const { lng, lat } = item;
    setMapCenter(lng, lat, props.selectedZoom);
    if (poiMode.value) {
      bounceIcon(); // POI检索类型地图中心图标跳动
      return;
    }
    showCenterMarker(lng, lat); // 非POI检索类型地图中心添加标记
  };

  /** 确定按钮点击事件 */
  const handleConfirm = () => {
    if (!state.context?.label) {
      return;
    }
    // 未选择使用地图中心点
    if (!current.value) {
      confirmLoading.value = true;
      getMapCenter(props.returnRegions)
        .then((result) => {
          confirmLoading.value = false;
          emit('done', result);
        })
        .catch((e) => {
          console.error(e);
          confirmLoading.value = false;
          emit('done', {});
        });
      return;
    }
    if (!props.returnRegions || !isNullCity(current.value.city)) {
      emit('done', current.value);
      return;
    }
    // 获取行政区
    confirmLoading.value = true;
    state.isItemClickMove = true;
    setMapCenter(current.value.lng, current.value.lat);
    getMapCenter(true)
      .then(({ city }) => {
        confirmLoading.value = false;
        emit('done', { ...(current.value || {}), city });
      })
      .catch((e) => {
        console.error(e);
        confirmLoading.value = false;
        emit('done', current.value || {});
      });
  };

  watch(
    () => props.selected,
    () => {
      showInitSelected();
    }
  );

  watch(
    () => props.darkMode,
    (darkMode) => {
      if (!props.mapStyle) {
        changeMapStyle(darkMode);
      }
    }
  );

  watch(
    () => props.mapStyle,
    (mapStyle) => {
      if (mapStyle) {
        changeMapStyle(mapStyle);
      }
    }
  );

  watch(
    () => props.mode,
    (mode) => {
      keywords.value = '';
      suggestionData.value = [];
      state.selectedSuggestion = null;
      state.lastSuggestion = '';
      removeCenterMarker();
      if (mode !== 'poi' && current.value) {
        const { lng, lat } = current.value.location;
        showCenterMarker(lng, lat);
      }
      if (!data.value.length && (mode === 'poi' || mode === 'keyword')) {
        if (current.value) {
          const { lng, lat } = current.value.location;
          searchPOI(lng, lat);
        } else {
          const { lng, lat } = state.mapIns.getCenter();
          searchPOI(lng, lat);
        }
      }
    }
  );

  watch(
    () => props.mapKey,
    () => {
      destroyAll();
      renderMap();
    }
  );

  onMounted(() => {
    renderMap();
  });

  onBeforeUnmount(() => {
    destroyAll();
  });

  defineExpose({
    autocompleteRef,
    getMapIns,
    showInitSelected
  });
</script>
