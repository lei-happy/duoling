<template>
  <ele-page
    class="brand-series-page"
    hide-footer
    :multi-card="false"
    flex-table="auto"
  >
    <ele-card :body-style="{ padding: 0 }" flex-table="auto">
      <ele-split-panel
        :space="0"
        :size="300"
        allow-collapse
        :collapse-btn-offset="2"
        v-model:collapse="collapse"
        :custom-style="{ borderWidth: '0 1px 0 0' }"
        flex-table="auto"
      >
        <template #sideHeader>
          <el-input
            clearable
            :maxlength="50"
            v-model="sideKeyword"
            placeholder="搜索品牌名称"
            :prefix-icon="SearchOutlined"
          />
        </template>
        <ele-loading
          :loading="sideLoading"
          :spinner-style="{ background: 'none' }"
          :style="{ flex: '1 1 60px', overflow: 'hidden', minHeight: 0 }"
        >
          <div
            ref="sideScrollRef"
            class="brand-side-scroll"
            @scroll.passive="onSideScroll"
          >
            <div class="brand-side-list">
              <div
                v-for="b in brandOptions"
                :key="b.brandId"
                :class="[
                  'brand-side-item',
                  { 'is-active': b.brandId === currentBrandId }
                ]"
                @click="selectBrand(b)"
              >
                <div class="brand-side-item__main">
                  <div class="brand-side-item__logo-wrap">
                    <div v-if="brandLogoUrl(b)" class="brand-side-logo-box">
                      <el-image
                        :src="brandLogoUrl(b)"
                        fit="contain"
                        class="brand-side-logo-el"
                        :preview-src-list="[brandLogoUrl(b)]"
                        preview-teleported
                      />
                    </div>
                    <div v-else class="brand-side-logo-box brand-side-logo--ph">
                      {{ brandNameInitial(b.brandNameCn) }}
                    </div>
                  </div>
                  <span
                    class="brand-side-item__name"
                    :title="`${b.brandNameCn}[${brandSeriesCount(b)}]`"
                  >
                    {{ b.brandNameCn }}[{{ brandSeriesCount(b) }}]
                  </span>
                </div>
                <span class="brand-side-item__id">#{{ b.brandId }}</span>
              </div>
              <div v-if="sideLoadingMore" class="brand-side-footer">
                加载中...
              </div>
              <div
                v-else-if="!sideHasMore && brandOptions.length"
                class="brand-side-footer"
              >
                已加载全部
              </div>
              <div
                v-if="!brandOptions.length && !sideLoading"
                class="brand-side-empty"
              >
                暂无品牌数据
              </div>
            </div>
          </div>
        </ele-loading>

        <template #bodyHeader>
          <series-search @search="onSeriesSearch" />
        </template>
        <template #body>
          <ele-pro-table
            ref="tableRef"
            row-key="seriesId"
            :columns="columns"
            :datasource="datasource"
            :show-overflow-tooltip="true"
            :highlight-current-row="true"
            :load-on-created="false"
            cache-key="BasicDataBrandSeriesTable"
          >
            <template #toolbar>
              <div class="brand-series-toolbar">
                <el-button
                  v-if="hasPermission(PERM_ADD)"
                  type="primary"
                  :icon="PlusOutlined"
                  @click="openBrandCreate"
                >
                  新增品牌
                </el-button>
                <el-button
                  v-if="hasPermission(PERM_EDIT) && currentBrandId != null"
                  type="warning"
                  plain
                  :icon="EditOutlined"
                  @click="openBrandEditCurrent"
                >
                  编辑品牌
                </el-button>
                <el-button
                  v-if="hasPermission(PERM_DEL) && currentBrandId != null"
                  type="danger"
                  plain
                  :icon="DeleteOutlined"
                  @click="removeCurrentBrand"
                >
                  删除品牌
                </el-button>
                <el-button
                  v-if="hasPermission(PERM_ADD) && currentBrandId != null"
                  type="success"
                  :icon="PlusOutlined"
                  @click="() => openSeriesEdit()"
                >
                  新增车系
                </el-button>
              </div>
            </template>
            <template #seriesImage="{ row }">
              <div v-if="seriesImageUrl(row)" class="series-thumb-cell">
                <el-image
                  :src="seriesImageUrl(row)"
                  fit="contain"
                  class="series-table-thumb-el"
                  :preview-src-list="[seriesImageUrl(row)]"
                  preview-teleported
                />
              </div>
              <span v-else class="series-thumb-cell series-thumb-cell--empty"
                >—</span
              >
            </template>
            <template #action="{ row }">
              <btn-items
                divider
                type="link"
                :items="[
                  {
                    preset: 'edit',
                    permission: PERM_EDIT,
                    onClick: () => openSeriesEdit(row)
                  },
                  {
                    preset: 'del',
                    permission: PERM_DEL,
                    onClick: () => removeSeries(row)
                  }
                ]"
              />
            </template>
          </ele-pro-table>
        </template>
      </ele-split-panel>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { nextTick, onUnmounted, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import type { EleProTable } from 'ele-admin-plus';
  import type {
    DatasourceFunction,
    Columns
  } from 'ele-admin-plus/es/ele-pro-table/types';
  import {
    SearchOutlined,
    PlusOutlined,
    EditOutlined,
    DeleteOutlined
  } from '@/components/icons';
  import SeriesSearch from './components/series-search.vue';
  import {
    pageVehicleBrandOptions,
    removeVehicleBrand,
    getVehicleBrand
  } from '@/api/basic-data/vehicle-brand';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import {
    pageVehicleSeries,
    removeVehicleSeries
  } from '@/api/basic-data/vehicle-series';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import { usePermission } from '@/utils/use-permission';

  defineOptions({ name: 'BasicDataBrandSeries' });

  const PERM_ADD = 'basic_data:vehicle_brand_series:add';
  const PERM_EDIT = 'basic_data:vehicle_brand_series:edit';
  const PERM_DEL = 'basic_data:vehicle_brand_series:delete';
  /** 侧栏每页条数 */
  const SIDE_PAGE_SIZE = 50;
  /** 距底部多少 px 时触发加载下一页 */
  const SCROLL_LOAD_THRESHOLD = 80;

  const { hasPermission } = usePermission();

  function uploadImageSrc(p?: string | null): string | undefined {
    const s = p?.trim();
    if (!s) return undefined;
    if (s.startsWith('http://') || s.startsWith('https://')) return s;
    return s.startsWith('/') ? s : `/${s}`;
  }

  function brandNameInitial(name?: string) {
    const t = name?.trim();
    if (!t) return '?';
    return t.charAt(0);
  }

  function brandSeriesCount(b: VehicleBrandOption) {
    const n = b.seriesCount;
    return typeof n === 'number' && !Number.isNaN(n) ? n : 0;
  }

  function brandLogoUrl(b: VehicleBrandOption): string {
    return uploadImageSrc(b.brandLogo) ?? '';
  }

  function seriesImageUrl(row: VehicleSeries): string {
    return uploadImageSrc(row.seriesImage) ?? '';
  }

  const { openModal } = useModal();

  const collapse = ref(false);
  const sideLoading = ref(true);
  const sideLoadingMore = ref(false);
  const sideHasMore = ref(true);
  const sidePage = ref(1);
  const sideKeyword = ref('');
  const brandOptions = ref<VehicleBrandOption[]>([]);
  const currentBrandId = ref<number | null>(null);
  const currentBrandName = ref('');
  const seriesKeyword = ref('');
  const sideScrollRef = ref<HTMLElement | null>(null);

  const tableRef = ref<InstanceType<typeof EleProTable> | null>(null);

  let keywordTimer: ReturnType<typeof setTimeout> | null = null;
  let sideLoadSeq = 0;

  const syncSelectionAfterLoad = (autoSelectFirst: boolean) => {
    // 分页场景下当前品牌可能尚未加载到列表，不能仅因「不在当前页」就清空选中
    if (
      autoSelectFirst &&
      brandOptions.value.length &&
      currentBrandId.value == null
    ) {
      selectBrand(brandOptions.value[0]);
    }
  };

  /** 首屏不足一屏时继续加载，直至可滚动或无更多数据 */
  const fillSideScrollViewport = () => {
    const el = sideScrollRef.value;
    if (
      !el ||
      !sideHasMore.value ||
      sideLoading.value ||
      sideLoadingMore.value
    ) {
      return;
    }
    if (el.scrollHeight <= el.clientHeight + SCROLL_LOAD_THRESHOLD) {
      loadBrandOptions(false);
    }
  };

  /**
   * 加载品牌列表
   * @param reset true=重新从第一页加载；false=追加下一页
   * @param autoSelectFirst 首屏无选中时自动选第一条
   */
  const loadBrandOptions = async (reset = true, autoSelectFirst = false) => {
    if (reset) {
      sideLoading.value = true;
      sidePage.value = 1;
      sideHasMore.value = true;
    } else {
      if (sideLoadingMore.value || !sideHasMore.value || sideLoading.value) {
        return;
      }
      sideLoadingMore.value = true;
    }

    const seq = ++sideLoadSeq;
    const page = sidePage.value;
    const kw = sideKeyword.value?.trim();

    try {
      const data = await pageVehicleBrandOptions({
        page,
        limit: SIDE_PAGE_SIZE,
        keyword: kw || undefined
      });
      if (seq !== sideLoadSeq) return;

      const list = data.list ?? [];
      const count = data.count ?? 0;
      if (reset) {
        brandOptions.value = list;
      } else {
        const exist = new Set(brandOptions.value.map((b) => b.brandId));
        brandOptions.value.push(...list.filter((b) => !exist.has(b.brandId)));
      }
      sideHasMore.value = brandOptions.value.length < count;
      if (sideHasMore.value) {
        sidePage.value = page + 1;
      }
      syncSelectionAfterLoad(autoSelectFirst);
    } catch (e: unknown) {
      if (seq !== sideLoadSeq) return;
      const msg = e instanceof Error ? e.message : '加载失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      if (seq === sideLoadSeq) {
        sideLoading.value = false;
        sideLoadingMore.value = false;
        await nextTick();
        fillSideScrollViewport();
      }
    }
  };

  const onSideScroll = () => {
    const el = sideScrollRef.value;
    if (
      !el ||
      sideLoading.value ||
      sideLoadingMore.value ||
      !sideHasMore.value
    ) {
      return;
    }
    const { scrollTop, scrollHeight, clientHeight } = el;
    if (scrollHeight - scrollTop - clientHeight <= SCROLL_LOAD_THRESHOLD) {
      loadBrandOptions(false);
    }
  };

  watch(sideKeyword, () => {
    if (keywordTimer) {
      clearTimeout(keywordTimer);
    }
    keywordTimer = setTimeout(() => {
      const kw = sideKeyword.value?.trim();
      // 全局搜索：有关键词时重置选中并自动选中首条匹配；清空关键词则保留当前选中
      if (kw) {
        currentBrandId.value = null;
        currentBrandName.value = '';
        reloadSeries(1);
        loadBrandOptions(true, true);
      } else {
        loadBrandOptions(true, currentBrandId.value == null);
      }
    }, 300);
  });

  onUnmounted(() => {
    if (keywordTimer) {
      clearTimeout(keywordTimer);
    }
  });

  const selectBrand = (b: VehicleBrandOption) => {
    currentBrandId.value = b.brandId;
    currentBrandName.value = b.brandNameCn;
    reloadSeries(1);
  };

  const columns = ref<Columns>([
    { prop: 'seriesId', label: '车系ID', width: 100, align: 'center' },
    {
      prop: 'seriesImage',
      label: '图片',
      width: 64,
      align: 'center',
      slot: 'seriesImage'
    },
    { prop: 'seriesName', label: '车系名称', minWidth: 140 },
    { prop: 'price', label: '价格范围', minWidth: 120 },
    { prop: 'energyType', label: '能源类型', width: 110 },
    {
      columnKey: 'action',
      label: '操作',
      width: 148,
      align: 'center',
      slot: 'action',
      hideInPrint: true,
      hideInExport: true
    }
  ]);

  const datasource: DatasourceFunction = ({ pages }) => {
    if (currentBrandId.value == null) {
      return Promise.resolve({ list: [], count: 0 });
    }
    const kw = seriesKeyword.value?.trim();
    return pageVehicleSeries({
      brandId: currentBrandId.value,
      ...pages,
      keyword: kw || undefined
    }).then((res) => ({
      list: res.list,
      count: res.count
    }));
  };

  const reloadSeries = (page?: number) => {
    tableRef.value?.reload?.({ page });
  };

  const onSeriesSearch = (where?: { keyword?: string }) => {
    seriesKeyword.value = where?.keyword?.trim() ?? '';
    reloadSeries(1);
  };

  const openBrandCreate = () => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/brand-edit.vue'),
      componentProps: {
        data: null,
        onDone: () => {
          loadBrandOptions(true, true);
        }
      }
    });
  };

  const openBrandEditCurrent = () => {
    if (currentBrandId.value == null) return;
    const loading = EleMessage.loading({
      message: '加载中..',
      plain: true
    });
    getVehicleBrand(currentBrandId.value)
      .then((data) => {
        loading.close();
        openModal({
          custom: true,
          asyncComponent: () => import('./components/brand-edit.vue'),
          componentProps: {
            data,
            onDone: () => {
              loadBrandOptions(true);
            }
          }
        });
      })
      .catch((e) => {
        loading.close();
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  const removeCurrentBrand = () => {
    if (currentBrandId.value == null) return;
    ElMessageBox.confirm(
      `确定要删除品牌「${currentBrandName.value}」吗？（无车系时才可删除）`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeVehicleBrand(currentBrandId.value!)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            currentBrandId.value = null;
            currentBrandName.value = '';
            loadBrandOptions(true, true);
            reloadSeries(1);
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  const openSeriesEdit = (row?: VehicleSeries) => {
    if (currentBrandId.value == null) {
      EleMessage.warning({ message: '请先选择品牌', plain: true });
      return;
    }
    openModal({
      custom: true,
      asyncComponent: () => import('./components/series-edit.vue'),
      componentProps: {
        brandId: currentBrandId.value,
        brandName: currentBrandName.value,
        data: row ?? null,
        onDone: () => {
          reloadSeries(1);
          loadBrandOptions(true);
        }
      }
    });
  };

  const removeSeries = (row: VehicleSeries) => {
    ElMessageBox.confirm(
      `确定要删除车系「${row.seriesName}」吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => {
        const loading = EleMessage.loading({
          message: '请求中..',
          plain: true
        });
        removeVehicleSeries(row.seriesId)
          .then((msg) => {
            loading.close();
            EleMessage.success({ message: msg, plain: true });
            reloadSeries(1);
            loadBrandOptions(true);
          })
          .catch((e) => {
            loading.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  loadBrandOptions(true, true);
</script>

<style scoped>
  .brand-side-scroll {
    height: 100%;
    overflow: auto;
  }
  .brand-side-list {
    padding: 8px 12px 12px;
  }
  .brand-side-footer {
    padding: 10px 8px 4px;
    text-align: center;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
  .brand-side-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 6px 10px;
    margin-bottom: 4px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
  }
  .brand-side-item__main {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    flex: 1;
  }
  .brand-side-item__logo-wrap {
    flex-shrink: 0;
    display: flex;
    align-items: center;
  }
  .brand-side-logo-box {
    width: 36px;
    height: 36px;
    border-radius: 6px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .brand-side-logo-el {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .brand-side-logo-el :deep(.el-image__inner) {
    object-fit: contain;
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
  }
  .brand-side-logo--ph {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
    border: 1px solid var(--el-border-color-lighter);
  }
  .brand-side-item__name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .brand-side-item:hover {
    background: var(--el-fill-color-light);
  }
  .brand-side-item.is-active {
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }
  .brand-side-item__id {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
  .brand-side-empty {
    padding: 24px 8px;
    text-align: center;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }
  .brand-series-toolbar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
  }
  .series-thumb-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 32px;
    line-height: 1;
  }
  .series-thumb-cell--empty {
    color: var(--el-text-color-placeholder);
    font-size: 13px;
  }
  .series-table-thumb-el {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }
  .series-table-thumb-el :deep(.el-image__inner) {
    object-fit: contain;
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
  }

  .brand-series-page
    :deep(.ele-pro-table .el-table .el-table__body .el-table__cell) {
    padding-top: 4px;
    padding-bottom: 4px;
    vertical-align: middle;
  }
  .brand-series-page
    :deep(.ele-pro-table .el-table .el-table__body .el-table__cell .cell) {
    line-height: 1.35;
  }
</style>
