import { defineComponent, inject, ref, computed, watch, onMounted, onBeforeUnmount, createBlock, openBlock, normalizeStyle, normalizeClass, withCtx, createElementVNode, createCommentVNode, createElementBlock, Fragment, createVNode, unref, toDisplayString, createTextVNode, renderList, mergeProps, nextTick } from "vue";
import AMapLoader from "@amap/amap-jsapi-loader";
import { ElIcon, ElAutocomplete, ElButton, ElInput, ElEmpty } from "element-plus";
import { PlusOutlined, SearchOutlined, EnvironmentOutlined, CheckCircleOutlined } from "../../icons/index";
import { modalItemContextKey } from "../../utils/hook";
import EleLoading from "../../ele-loading/index";
import { mapProps } from "../props";
const _hoisted_1 = { class: "ele-map-view-body" };
const _hoisted_2 = ["src"];
const _hoisted_3 = { class: "ele-map-suggest-item" };
const _hoisted_4 = { class: "ele-map-suggest-title" };
const _hoisted_5 = { class: "ele-map-suggest-text" };
const _hoisted_6 = {
  key: 0,
  class: "ele-map-view-message"
};
const _hoisted_7 = ["onClick"];
const _hoisted_8 = { class: "ele-map-view-item-body" };
const _hoisted_9 = {
  key: 0,
  class: "ele-map-view-item-title"
};
const _hoisted_10 = { class: "ele-map-view-item-title" };
const _hoisted_11 = {
  key: 0,
  class: "ele-map-view-item-text"
};
const _hoisted_12 = {
  key: 0,
  class: "ele-map-view-empty"
};
const _hoisted_13 = { class: "ele-map-view-extra" };
const _hoisted_14 = {
  key: 0,
  class: "ele-map-view-message"
};
const ICON_CLASS = "ele-map-view-body-icon";
const _sfc_main = /* @__PURE__ */ defineComponent({
  ...{ name: "MapView" },
  __name: "map-view",
  props: mapProps,
  emits: {
    mapDone: (_ins) => true,
    select: (_selected) => true,
    done: (_result) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const state = { context: inject(modalItemContextKey, null) };
    const mapRef = ref(null);
    const autocompleteRef = ref(null);
    const listRef = ref(null);
    const loading = ref(true);
    const poiLoading = ref(false);
    const confirmLoading = ref(false);
    const data = ref([]);
    const suggestionData = ref([]);
    const centerIconClass = ref([ICON_CLASS]);
    const keywords = ref("");
    const current = ref(null);
    const confirmDisabled = computed(() => props.required && !current.value);
    const keywordMode = computed(() => "keyword" === props.mode);
    const poiMode = computed(() => "poi" === props.mode);
    const getInitSelected = () => {
      if (props.selected != null) {
        const { lng, lat } = props.selected;
        if (lat != null && lng != null) {
          return props.selected;
        }
      }
    };
    const isSamePOI = (poi, item) => {
      return item.lat === poi.lat && item.lng === poi.lng && item.name === poi.name && item.address === poi.address;
    };
    const addFirstPOI = (poi, list) => {
      const index = list.findIndex((d) => isSamePOI(poi, d));
      if (index == -1) {
        return [poi, ...list];
      }
      const result = [...list];
      result[index] = poi;
      return result;
    };
    const isNullCity = (city) => {
      if (city == null || typeof city !== "object" || city.province == null && city.city == null && city.district == null && city.citycode == null) {
        return true;
      }
      return false;
    };
    const formatPOI = (d) => {
      const name = d.name || "";
      const addr = Array.isArray(d.address) ? d.address[0] : d.address;
      const address = addr || "";
      const { lat, lng } = d.location;
      const city = isNullCity(d.city) ? void 0 : d.city;
      const key = [name, address, lat, lng].join(",");
      return { ...d, name, address, lat, lng, city, key };
    };
    const scrollToTop = () => {
      const listEl = listRef.value;
      if (listEl) {
        listEl.scrollTop = 0;
      }
    };
    const scrollToActive = () => {
      const listEl = listRef.value;
      if (listEl) {
        const el = listEl.querySelector(".ele-map-view-item.is-active");
        if (el) {
          if (typeof el["scrollIntoViewIfNeeded"] === "function") {
            el.scrollIntoViewIfNeeded(true);
          } else {
            el.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }
      }
    };
    const setSelected = (item, trigger) => {
      if (current.value !== item) {
        current.value = item;
        if (trigger) {
          emit("select", current.value);
        }
      }
    };
    const searchKeywords = (keyword) => {
      return new Promise((resolve, reject) => {
        if (!state.autoCompleteIns) {
          reject(new Error("AutoComplete instance is null"));
          return;
        }
        state.autoCompleteIns.search(keyword, (status, result) => {
          if (status === "error") {
            const msg = `${status} ${result ? JSON.stringify(result) : ""}`;
            reject(new Error(msg));
            return;
          }
          if (!result?.tips) {
            resolve([]);
            return;
          }
          const tips = result.tips.filter((d) => !!d.location);
          resolve(tips.map((d) => formatPOI(d)));
        });
      });
    };
    const searchNearBy = (lng, lat) => {
      return new Promise((resolve, reject) => {
        if (!state.placeSearchIns) {
          reject(new Error("PlaceSearch instance is null"));
          return;
        }
        state.placeSearchIns.searchNearBy(
          props.poiKeywords,
          [lng, lat],
          props.poiRadius,
          (status, result) => {
            if (status === "complete" && result?.poiList?.pois) {
              const ps = result.poiList.pois.filter((d) => !!d.location);
              resolve(ps.map((d) => formatPOI(d)));
              return;
            }
            if (status === "no_data") {
              resolve([]);
              return;
            }
            const msg = `${status} ${result ? JSON.stringify(result) : ""}`;
            reject(new Error(msg));
          }
        );
      });
    };
    const searchPOI = (lng, lat) => {
      loading.value = true;
      poiLoading.value = true;
      searchNearBy(lng, lat).then((result) => {
        poiLoading.value = false;
        loading.value = false;
        if (!state.selectedSuggestion) {
          data.value = result;
          setSelected(null, true);
          scrollToTop();
          return;
        }
        data.value = addFirstPOI(state.selectedSuggestion, result);
        setSelected(state.selectedSuggestion, true);
        state.selectedSuggestion = null;
        nextTick(() => {
        });
      }).catch((e) => {
        console.error(e);
        poiLoading.value = false;
        loading.value = false;
        const selectedSuggestion = state.selectedSuggestion;
        data.value = selectedSuggestion ? [selectedSuggestion] : [];
        setSelected(selectedSuggestion ? selectedSuggestion : null, true);
      });
    };
    const bounceIcon = () => {
      centerIconClass.value = [ICON_CLASS];
      nextTick(() => {
        setTimeout(() => {
          centerIconClass.value = [ICON_CLASS, "ele-map-view-anim-bounce"];
        }, 0);
      });
    };
    const removeCenterMarker = () => {
      if (state.centerMarker && state.mapIns) {
        state.mapIns.remove(state.centerMarker);
      }
    };
    const showCenterMarker = (lng, lat) => {
      if (!state.centerMarker) {
        console.error("centerMarker is null");
        return;
      }
      if (!state.mapIns) {
        console.error("map instance is null");
        return;
      }
      removeCenterMarker();
      if (lng != null && lat != null) {
        state.centerMarker.setPosition([lng, lat]);
        state.mapIns.add(state.centerMarker);
      }
    };
    const setMapCenter = (lng, lat, zoom) => {
      if (state.mapIns && lng != null && lat != null) {
        if (zoom == null) {
          state.mapIns.setCenter([lng, lat]);
        } else {
          state.mapIns.setZoomAndCenter(zoom, [lng, lat]);
        }
      }
    };
    const getMapCenter = (returnRegions) => {
      return new Promise((resolve, reject) => {
        if (!state.mapIns) {
          reject(new Error("map instance is null"));
          return;
        }
        const result = state.mapIns.getCenter();
        if (!returnRegions) {
          resolve(result || {});
          return;
        }
        state.mapIns.getCity((city) => {
          resolve({ ...result || {}, city });
        });
      });
    };
    const changeMapStyle = (style) => {
      if (state.mapIns) {
        if (typeof style === "boolean") {
          if (style) {
            state.mapIns.setMapStyle("amap://styles/dark");
          } else {
            state.mapIns.setMapStyle("amap://styles/normal");
          }
        } else if (style) {
          state.mapIns.setMapStyle(style);
        }
      }
    };
    const destroyMap = () => {
      state.mapIns && state.mapIns.destroy();
      state.centerMarker = null;
      state.placeSearchIns = null;
      state.autoCompleteIns = null;
      state.mapIns = null;
    };
    const destroyAll = () => {
      destroyMap();
      state.lastSuggestion = "";
      state.selectedSuggestion = null;
      state.isItemClickMove = false;
      data.value = [];
      suggestionData.value = [];
      keywords.value = "";
      setSelected(null);
    };
    const renderMap = () => {
      if (!props.mapKey || state.mapIns) {
        return;
      }
      AMapLoader.load({
        key: props.mapKey,
        version: props.mapVersion,
        plugins: ["AMap.PlaceSearch", "AMap.AutoComplete"]
      }).then((AMap) => {
        destroyAll();
        state.centerMarker = new AMap.Marker({
          icon: new AMap.Icon({
            image: props.markerSrc,
            size: new AMap.Size(26, 36.5),
            imageSize: new AMap.Size(26, 36.5)
          }),
          offset: new AMap.Pixel(-13, -36.5)
        });
        state.autoCompleteIns = new AMap.AutoComplete({
          city: props.suggestionCity
        });
        state.placeSearchIns = new AMap.PlaceSearch({
          type: props.poiType,
          pageSize: props.poiLimit,
          pageIndex: 1
        });
        const selected = getInitSelected();
        const selCenter = selected ? [selected.lng, selected.lat] : void 0;
        const defaultStyle = props.darkMode ? "amap://styles/dark" : void 0;
        state.mapIns = new AMap.Map(mapRef.value, {
          zoom: selected == null ? props.zoom : props.selectedZoom,
          // 初缩放级别
          center: selCenter || props.center,
          // 初始中心点
          resizeEnable: true,
          // 监控地图容器尺寸变化
          mapStyle: props.mapStyle || defaultStyle
        });
        state.mapIns.on("complete", () => {
          const selected2 = getInitSelected();
          if (selected2 != null) {
            setSelected(selected2);
            if (!poiMode.value) {
              const { lng, lat } = selected2;
              showCenterMarker(lng, lat);
            }
          }
          if (poiMode.value || keywordMode.value) {
            state.selectedSuggestion = selected2;
            const { lng, lat } = state.mapIns.getCenter();
            searchPOI(lng, lat);
            return;
          }
          loading.value = false;
        });
        state.mapIns.on("moveend", () => {
          if (state.isItemClickMove || !poiMode.value) {
            state.isItemClickMove = false;
            return;
          }
          bounceIcon();
          const { lng, lat } = state.mapIns.getCenter();
          searchPOI(lng, lat);
        });
        state.mapIns.on("click", (e) => {
          if (poiMode.value || keywordMode.value) {
            return;
          }
          if (e.lnglat == null || typeof e.lnglat !== "object") {
            console.error(e);
            return;
          }
          const { lng, lat } = e.lnglat;
          setSelected(formatPOI({ location: { lat, lng } }), true);
          setMapCenter(lng, lat, props.selectedZoom);
          showCenterMarker(lng, lat);
        });
        emit("mapDone", state.mapIns);
      }).catch((e) => {
        console.error(e);
      });
    };
    const getMapIns = () => {
      return state.mapIns;
    };
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
      if ((keywordMode.value || poiMode.value) && !data.value.includes(selected)) {
        data.value = addFirstPOI(selected, data.value);
      }
      nextTick(() => {
        scrollToActive();
      });
    };
    const handleSearch = (keyword, callback) => {
      if (!keyword || state.lastSuggestion === keyword) {
        callback && callback(suggestionData.value);
        return;
      }
      state.lastSuggestion = keyword;
      if (keywordMode.value) {
        poiLoading.value = true;
      }
      searchKeywords(keyword).then((result) => {
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
      }).catch((e) => {
        console.error(e);
        poiLoading.value = false;
        callback && callback(suggestionData.value);
      });
    };
    const handleSearchSelect = (item) => {
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
    const handleItemClick = (item) => {
      state.isItemClickMove = true;
      setSelected(item, true);
      const { lng, lat } = item;
      setMapCenter(lng, lat, props.selectedZoom);
      if (poiMode.value) {
        bounceIcon();
        return;
      }
      showCenterMarker(lng, lat);
    };
    const handleConfirm = () => {
      if (!state.context?.label) {
        return;
      }
      if (!current.value) {
        confirmLoading.value = true;
        getMapCenter(props.returnRegions).then((result) => {
          confirmLoading.value = false;
          emit("done", result);
        }).catch((e) => {
          console.error(e);
          confirmLoading.value = false;
          emit("done", {});
        });
        return;
      }
      if (!props.returnRegions || !isNullCity(current.value.city)) {
        emit("done", current.value);
        return;
      }
      confirmLoading.value = true;
      state.isItemClickMove = true;
      setMapCenter(current.value.lng, current.value.lat);
      getMapCenter(true).then(({ city }) => {
        confirmLoading.value = false;
        emit("done", { ...current.value || {}, city });
      }).catch((e) => {
        console.error(e);
        confirmLoading.value = false;
        emit("done", current.value || {});
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
        keywords.value = "";
        suggestionData.value = [];
        state.selectedSuggestion = null;
        state.lastSuggestion = "";
        removeCenterMarker();
        if (mode !== "poi" && current.value) {
          const { lng, lat } = current.value.location;
          showCenterMarker(lng, lat);
        }
        if (!data.value.length && (mode === "poi" || mode === "keyword")) {
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
    __expose({
      autocompleteRef,
      getMapIns,
      showInitSelected
    });
    return (_ctx, _cache) => {
      return openBlock(), createBlock(EleLoading, {
        loading: loading.value,
        class: normalizeClass(["ele-map-view", { "is-poi-mode": poiMode.value }]),
        style: normalizeStyle({ height: _ctx.height })
      }, {
        default: withCtx(() => [
          createElementVNode("div", _hoisted_1, [
            createElementVNode("div", {
              ref_key: "mapRef",
              ref: mapRef,
              style: { height: "100%" }
            }, null, 512),
            poiMode.value ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
              createVNode(unref(ElIcon), { class: "ele-map-view-icon-plus" }, {
                default: withCtx(() => [
                  createVNode(unref(PlusOutlined))
                ]),
                _: 1
              }),
              createElementVNode("img", {
                src: _ctx.markerSrc,
                class: normalizeClass(centerIconClass.value)
              }, null, 10, _hoisted_2)
            ], 64)) : createCommentVNode("", true),
            _ctx.filterable && !keywordMode.value ? (openBlock(), createElementBlock("div", {
              key: 1,
              class: "ele-map-view-search",
              style: normalizeStyle(_ctx.searchStyle)
            }, [
              createVNode(unref(ElAutocomplete), {
                ref_key: "autocompleteRef",
                ref: autocompleteRef,
                valueKey: "name",
                clearable: true,
                modelValue: keywords.value,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => keywords.value = $event),
                placeholder: _ctx.searchPlaceholder,
                popperClass: "ele-map-suggest-popper",
                fetchSuggestions: handleSearch,
                onSelect: handleSearchSelect
              }, {
                prefix: withCtx(() => [
                  createVNode(unref(ElIcon), { class: "el-input__icon" }, {
                    default: withCtx(() => [
                      createVNode(unref(SearchOutlined))
                    ]),
                    _: 1
                  })
                ]),
                default: withCtx(({ item }) => [
                  createElementVNode("div", _hoisted_3, [
                    createElementVNode("div", _hoisted_4, toDisplayString(item.name), 1),
                    createElementVNode("div", _hoisted_5, toDisplayString(item.district), 1)
                  ])
                ]),
                _: 1
              }, 8, ["modelValue", "placeholder"])
            ], 4)) : createCommentVNode("", true),
            !poiMode.value && !keywordMode.value ? (openBlock(), createElementBlock(Fragment, { key: 2 }, [
              confirmDisabled.value && _ctx.clickMessage ? (openBlock(), createElementBlock("div", _hoisted_6, toDisplayString(_ctx.clickMessage), 1)) : (openBlock(), createBlock(unref(ElButton), {
                key: 1,
                type: "primary",
                loading: confirmLoading.value,
                disabled: confirmDisabled.value,
                class: "ele-map-view-btn-ok",
                onClick: handleConfirm
              }, {
                default: withCtx(() => [
                  createTextVNode(toDisplayString(_ctx.okText), 1)
                ]),
                _: 1
              }, 8, ["loading", "disabled"]))
            ], 64)) : createCommentVNode("", true)
          ]),
          keywordMode.value || poiMode.value ? (openBlock(), createBlock(EleLoading, {
            key: 0,
            loading: poiLoading.value,
            style: normalizeStyle(_ctx.sideStyle),
            class: "ele-map-view-side"
          }, {
            default: withCtx(() => [
              keywordMode.value ? (openBlock(), createElementBlock("div", {
                key: 0,
                class: "ele-map-view-search",
                style: normalizeStyle(_ctx.searchStyle)
              }, [
                createVNode(unref(ElInput), {
                  clearable: true,
                  modelValue: keywords.value,
                  "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => keywords.value = $event),
                  prefixIcon: unref(SearchOutlined),
                  placeholder: _ctx.searchPlaceholder,
                  validateEvent: false,
                  onChange: handleSearch
                }, null, 8, ["modelValue", "prefixIcon", "placeholder"])
              ], 4)) : createCommentVNode("", true),
              createElementVNode("div", {
                ref_key: "listRef",
                ref: listRef,
                class: "ele-map-view-list"
              }, [
                (openBlock(true), createElementBlock(Fragment, null, renderList(data.value, (item) => {
                  return openBlock(), createElementBlock("div", {
                    key: item.key,
                    class: normalizeClass(["ele-map-view-item", { "is-active": item === current.value }]),
                    onClick: ($event) => handleItemClick(item)
                  }, [
                    createVNode(unref(ElIcon), { class: "ele-map-view-item-icon" }, {
                      default: withCtx(() => [
                        createVNode(unref(EnvironmentOutlined))
                      ]),
                      _: 1
                    }),
                    createElementVNode("div", _hoisted_8, [
                      !item.name && !item.address ? (openBlock(), createElementBlock("div", _hoisted_9, [
                        createElementVNode("span", null, toDisplayString(item.lng), 1),
                        _cache[2] || (_cache[2] = createElementVNode("span", null, ",", -1)),
                        createElementVNode("span", null, toDisplayString(item.lat), 1)
                      ])) : (openBlock(), createElementBlock(Fragment, { key: 1 }, [
                        createElementVNode("div", _hoisted_10, toDisplayString(item.name), 1),
                        item.address ? (openBlock(), createElementBlock("div", _hoisted_11, toDisplayString(item.address), 1)) : createCommentVNode("", true)
                      ], 64))
                    ]),
                    createVNode(unref(ElIcon), { class: "ele-map-view-item-radio" }, {
                      default: withCtx(() => [
                        createVNode(unref(CheckCircleOutlined))
                      ]),
                      _: 1
                    })
                  ], 10, _hoisted_7);
                }), 128)),
                !data.value || !data.value.length ? (openBlock(), createElementBlock("div", _hoisted_12, [
                  createVNode(unref(ElEmpty), mergeProps({ imageSize: 80 }, _ctx.emptyProps || {}), null, 16)
                ])) : createCommentVNode("", true)
              ], 512),
              createElementVNode("div", _hoisted_13, [
                confirmDisabled.value && _ctx.message ? (openBlock(), createElementBlock("div", _hoisted_14, toDisplayString(_ctx.message), 1)) : (openBlock(), createBlock(unref(ElButton), {
                  key: 1,
                  type: "primary",
                  loading: confirmLoading.value,
                  disabled: confirmDisabled.value,
                  class: "ele-map-view-btn-ok",
                  onClick: handleConfirm
                }, {
                  default: withCtx(() => [
                    createTextVNode(toDisplayString(_ctx.okText), 1)
                  ]),
                  _: 1
                }, 8, ["loading", "disabled"]))
              ])
            ]),
            _: 1
          }, 8, ["loading", "style"])) : createCommentVNode("", true)
        ]),
        _: 1
      }, 8, ["loading", "class", "style"]);
    };
  }
});
export {
  _sfc_main as default
};
