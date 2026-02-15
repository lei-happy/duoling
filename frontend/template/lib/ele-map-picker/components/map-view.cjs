"use strict";
const vue = require("vue");
const AMapLoader = require("@amap/amap-jsapi-loader");
const elementPlus = require("element-plus");
const index = require("../../icons/index");
const hook = require("../../utils/hook");
const EleLoading = require("../../ele-loading/index");
const props = require("../props");
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
const _sfc_main = /* @__PURE__ */ vue.defineComponent({
  ...{ name: "MapView" },
  __name: "map-view",
  props: props.mapProps,
  emits: {
    mapDone: (_ins) => true,
    select: (_selected) => true,
    done: (_result) => true
  },
  setup(__props, { expose: __expose, emit: __emit }) {
    const props2 = __props;
    const emit = __emit;
    const state = { context: vue.inject(hook.modalItemContextKey, null) };
    const mapRef = vue.ref(null);
    const autocompleteRef = vue.ref(null);
    const listRef = vue.ref(null);
    const loading = vue.ref(true);
    const poiLoading = vue.ref(false);
    const confirmLoading = vue.ref(false);
    const data = vue.ref([]);
    const suggestionData = vue.ref([]);
    const centerIconClass = vue.ref([ICON_CLASS]);
    const keywords = vue.ref("");
    const current = vue.ref(null);
    const confirmDisabled = vue.computed(() => props2.required && !current.value);
    const keywordMode = vue.computed(() => "keyword" === props2.mode);
    const poiMode = vue.computed(() => "poi" === props2.mode);
    const getInitSelected = () => {
      if (props2.selected != null) {
        const { lng, lat } = props2.selected;
        if (lat != null && lng != null) {
          return props2.selected;
        }
      }
    };
    const isSamePOI = (poi, item) => {
      return item.lat === poi.lat && item.lng === poi.lng && item.name === poi.name && item.address === poi.address;
    };
    const addFirstPOI = (poi, list) => {
      const index2 = list.findIndex((d) => isSamePOI(poi, d));
      if (index2 == -1) {
        return [poi, ...list];
      }
      const result = [...list];
      result[index2] = poi;
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
          props2.poiKeywords,
          [lng, lat],
          props2.poiRadius,
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
        vue.nextTick(() => {
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
      vue.nextTick(() => {
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
      if (!props2.mapKey || state.mapIns) {
        return;
      }
      AMapLoader.load({
        key: props2.mapKey,
        version: props2.mapVersion,
        plugins: ["AMap.PlaceSearch", "AMap.AutoComplete"]
      }).then((AMap) => {
        destroyAll();
        state.centerMarker = new AMap.Marker({
          icon: new AMap.Icon({
            image: props2.markerSrc,
            size: new AMap.Size(26, 36.5),
            imageSize: new AMap.Size(26, 36.5)
          }),
          offset: new AMap.Pixel(-13, -36.5)
        });
        state.autoCompleteIns = new AMap.AutoComplete({
          city: props2.suggestionCity
        });
        state.placeSearchIns = new AMap.PlaceSearch({
          type: props2.poiType,
          pageSize: props2.poiLimit,
          pageIndex: 1
        });
        const selected = getInitSelected();
        const selCenter = selected ? [selected.lng, selected.lat] : void 0;
        const defaultStyle = props2.darkMode ? "amap://styles/dark" : void 0;
        state.mapIns = new AMap.Map(mapRef.value, {
          zoom: selected == null ? props2.zoom : props2.selectedZoom,
          // 初缩放级别
          center: selCenter || props2.center,
          // 初始中心点
          resizeEnable: true,
          // 监控地图容器尺寸变化
          mapStyle: props2.mapStyle || defaultStyle
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
          setMapCenter(lng, lat, props2.selectedZoom);
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
      setMapCenter(lng, lat, props2.selectedZoom);
      if (!poiMode.value) {
        showCenterMarker(lng, lat);
      }
      if ((keywordMode.value || poiMode.value) && !data.value.includes(selected)) {
        data.value = addFirstPOI(selected, data.value);
      }
      vue.nextTick(() => {
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
        setMapCenter(lng, lat, props2.selectedZoom);
        setSelected(item, true);
        return;
      }
      loading.value = true;
      state.selectedSuggestion = item;
      state.isItemClickMove = true;
      setMapCenter(lng, lat, props2.selectedZoom);
      bounceIcon();
      searchPOI(lng, lat);
    };
    const handleItemClick = (item) => {
      state.isItemClickMove = true;
      setSelected(item, true);
      const { lng, lat } = item;
      setMapCenter(lng, lat, props2.selectedZoom);
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
        getMapCenter(props2.returnRegions).then((result) => {
          confirmLoading.value = false;
          emit("done", result);
        }).catch((e) => {
          console.error(e);
          confirmLoading.value = false;
          emit("done", {});
        });
        return;
      }
      if (!props2.returnRegions || !isNullCity(current.value.city)) {
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
    vue.watch(
      () => props2.selected,
      () => {
        showInitSelected();
      }
    );
    vue.watch(
      () => props2.darkMode,
      (darkMode) => {
        if (!props2.mapStyle) {
          changeMapStyle(darkMode);
        }
      }
    );
    vue.watch(
      () => props2.mapStyle,
      (mapStyle) => {
        if (mapStyle) {
          changeMapStyle(mapStyle);
        }
      }
    );
    vue.watch(
      () => props2.mode,
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
    vue.watch(
      () => props2.mapKey,
      () => {
        destroyAll();
        renderMap();
      }
    );
    vue.onMounted(() => {
      renderMap();
    });
    vue.onBeforeUnmount(() => {
      destroyAll();
    });
    __expose({
      autocompleteRef,
      getMapIns,
      showInitSelected
    });
    return (_ctx, _cache) => {
      return vue.openBlock(), vue.createBlock(EleLoading, {
        loading: loading.value,
        class: vue.normalizeClass(["ele-map-view", { "is-poi-mode": poiMode.value }]),
        style: vue.normalizeStyle({ height: _ctx.height })
      }, {
        default: vue.withCtx(() => [
          vue.createElementVNode("div", _hoisted_1, [
            vue.createElementVNode("div", {
              ref_key: "mapRef",
              ref: mapRef,
              style: { height: "100%" }
            }, null, 512),
            poiMode.value ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 0 }, [
              vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-map-view-icon-plus" }, {
                default: vue.withCtx(() => [
                  vue.createVNode(vue.unref(index.PlusOutlined))
                ]),
                _: 1
              }),
              vue.createElementVNode("img", {
                src: _ctx.markerSrc,
                class: vue.normalizeClass(centerIconClass.value)
              }, null, 10, _hoisted_2)
            ], 64)) : vue.createCommentVNode("", true),
            _ctx.filterable && !keywordMode.value ? (vue.openBlock(), vue.createElementBlock("div", {
              key: 1,
              class: "ele-map-view-search",
              style: vue.normalizeStyle(_ctx.searchStyle)
            }, [
              vue.createVNode(vue.unref(elementPlus.ElAutocomplete), {
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
                prefix: vue.withCtx(() => [
                  vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "el-input__icon" }, {
                    default: vue.withCtx(() => [
                      vue.createVNode(vue.unref(index.SearchOutlined))
                    ]),
                    _: 1
                  })
                ]),
                default: vue.withCtx(({ item }) => [
                  vue.createElementVNode("div", _hoisted_3, [
                    vue.createElementVNode("div", _hoisted_4, vue.toDisplayString(item.name), 1),
                    vue.createElementVNode("div", _hoisted_5, vue.toDisplayString(item.district), 1)
                  ])
                ]),
                _: 1
              }, 8, ["modelValue", "placeholder"])
            ], 4)) : vue.createCommentVNode("", true),
            !poiMode.value && !keywordMode.value ? (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 2 }, [
              confirmDisabled.value && _ctx.clickMessage ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_6, vue.toDisplayString(_ctx.clickMessage), 1)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                key: 1,
                type: "primary",
                loading: confirmLoading.value,
                disabled: confirmDisabled.value,
                class: "ele-map-view-btn-ok",
                onClick: handleConfirm
              }, {
                default: vue.withCtx(() => [
                  vue.createTextVNode(vue.toDisplayString(_ctx.okText), 1)
                ]),
                _: 1
              }, 8, ["loading", "disabled"]))
            ], 64)) : vue.createCommentVNode("", true)
          ]),
          keywordMode.value || poiMode.value ? (vue.openBlock(), vue.createBlock(EleLoading, {
            key: 0,
            loading: poiLoading.value,
            style: vue.normalizeStyle(_ctx.sideStyle),
            class: "ele-map-view-side"
          }, {
            default: vue.withCtx(() => [
              keywordMode.value ? (vue.openBlock(), vue.createElementBlock("div", {
                key: 0,
                class: "ele-map-view-search",
                style: vue.normalizeStyle(_ctx.searchStyle)
              }, [
                vue.createVNode(vue.unref(elementPlus.ElInput), {
                  clearable: true,
                  modelValue: keywords.value,
                  "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => keywords.value = $event),
                  prefixIcon: vue.unref(index.SearchOutlined),
                  placeholder: _ctx.searchPlaceholder,
                  validateEvent: false,
                  onChange: handleSearch
                }, null, 8, ["modelValue", "prefixIcon", "placeholder"])
              ], 4)) : vue.createCommentVNode("", true),
              vue.createElementVNode("div", {
                ref_key: "listRef",
                ref: listRef,
                class: "ele-map-view-list"
              }, [
                (vue.openBlock(true), vue.createElementBlock(vue.Fragment, null, vue.renderList(data.value, (item) => {
                  return vue.openBlock(), vue.createElementBlock("div", {
                    key: item.key,
                    class: vue.normalizeClass(["ele-map-view-item", { "is-active": item === current.value }]),
                    onClick: ($event) => handleItemClick(item)
                  }, [
                    vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-map-view-item-icon" }, {
                      default: vue.withCtx(() => [
                        vue.createVNode(vue.unref(index.EnvironmentOutlined))
                      ]),
                      _: 1
                    }),
                    vue.createElementVNode("div", _hoisted_8, [
                      !item.name && !item.address ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_9, [
                        vue.createElementVNode("span", null, vue.toDisplayString(item.lng), 1),
                        _cache[2] || (_cache[2] = vue.createElementVNode("span", null, ",", -1)),
                        vue.createElementVNode("span", null, vue.toDisplayString(item.lat), 1)
                      ])) : (vue.openBlock(), vue.createElementBlock(vue.Fragment, { key: 1 }, [
                        vue.createElementVNode("div", _hoisted_10, vue.toDisplayString(item.name), 1),
                        item.address ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_11, vue.toDisplayString(item.address), 1)) : vue.createCommentVNode("", true)
                      ], 64))
                    ]),
                    vue.createVNode(vue.unref(elementPlus.ElIcon), { class: "ele-map-view-item-radio" }, {
                      default: vue.withCtx(() => [
                        vue.createVNode(vue.unref(index.CheckCircleOutlined))
                      ]),
                      _: 1
                    })
                  ], 10, _hoisted_7);
                }), 128)),
                !data.value || !data.value.length ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_12, [
                  vue.createVNode(vue.unref(elementPlus.ElEmpty), vue.mergeProps({ imageSize: 80 }, _ctx.emptyProps || {}), null, 16)
                ])) : vue.createCommentVNode("", true)
              ], 512),
              vue.createElementVNode("div", _hoisted_13, [
                confirmDisabled.value && _ctx.message ? (vue.openBlock(), vue.createElementBlock("div", _hoisted_14, vue.toDisplayString(_ctx.message), 1)) : (vue.openBlock(), vue.createBlock(vue.unref(elementPlus.ElButton), {
                  key: 1,
                  type: "primary",
                  loading: confirmLoading.value,
                  disabled: confirmDisabled.value,
                  class: "ele-map-view-btn-ok",
                  onClick: handleConfirm
                }, {
                  default: vue.withCtx(() => [
                    vue.createTextVNode(vue.toDisplayString(_ctx.okText), 1)
                  ]),
                  _: 1
                }, 8, ["loading", "disabled"]))
              ])
            ]),
            _: 1
          }, 8, ["loading", "style"])) : vue.createCommentVNode("", true)
        ]),
        _: 1
      }, 8, ["loading", "class", "style"]);
    };
  }
});
module.exports = _sfc_main;
