<template>
  <el-dialog
    :title="isEdit ? '编辑线路' : '新增线路'"
    :model-value="visible"
    width="1100px"
    draggable
    class="route-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    append-to-body
    destroy-on-close
    @update:model-value="updateVisible"
  >
    <el-row :gutter="16" class="route-edit-layout">
      <el-col :xs="24" :sm="12" class="route-edit-left">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          class="route-edit-form"
          :validate-on-rule-change="false"
          @submit.prevent=""
        >
          <el-row :gutter="10">
            <template v-if="isEdit">
              <el-col :span="24">
                <el-form-item prop="routeCode">
                  <floating-label
                    label="线路编码"
                    type="input"
                    v-model="form.routeCode"
                    disabled
                    :clearable="false"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item prop="routeName">
                  <floating-label
                    label="线路名称"
                    type="input"
                    v-model.trim="form.routeName"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </template>
            <el-col :span="24">
              <el-form-item prop="originCode">
                <floating-label
                  label="请选择出发地"
                  type="cascader"
                  v-model="originCodes"
                  :cascader-options="regionTree"
                  :cascader-option-props="regionCascaderProps"
                  :cascader-filterable="true"
                  @change="onOriginChange"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item prop="destinationCode">
                <floating-label
                  label="请选择目的地"
                  type="cascader"
                  v-model="destCodes"
                  :cascader-options="regionTree"
                  :cascader-option-props="regionCascaderProps"
                  :cascader-filterable="true"
                  @change="onDestChange"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item prop="distance">
                <floating-label
                  label="里程(km)"
                  type="input-number"
                  v-model="form.distance"
                  :input-number-min="0"
                  :input-number-precision="1"
                  :clearable="false"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item prop="estimatedHours">
                <floating-label
                  label="预计时长(h)"
                  type="input-number"
                  v-model="form.estimatedHours"
                  :input-number-min="0"
                  :input-number-precision="1"
                  :clearable="false"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item prop="remark">
                <floating-label
                  label="备注"
                  type="input"
                  input-type="textarea"
                  v-model="form.remark"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <div
            v-if="canFetchMetrics"
            class="route-amap-suggest"
            v-loading="metricsLoading"
          >
            <div class="route-amap-suggest-head">
              <span class="route-amap-suggest-title">
                {{ suggestTitle }}
              </span>
              <span class="route-amap-suggest-tag">高速优先</span>
            </div>

            <template v-if="drivingMetrics">
              <div class="route-amap-suggest-metrics">
                <div class="route-amap-metric">
                  <span class="route-amap-metric-label">里程</span>
                  <span class="route-amap-metric-value">
                    {{ drivingMetrics.distanceKm }}
                    <small>km</small>
                  </span>
                </div>
                <div class="route-amap-metric">
                  <span class="route-amap-metric-label">预计时长</span>
                  <span class="route-amap-metric-value">
                    {{ drivingMetrics.estimatedHours }}
                    <small>h</small>
                  </span>
                </div>
              </div>
              <p class="route-amap-suggest-note">{{ amapSuggestNote }}</p>
              <el-button
                v-if="!metricsAdopted"
                type="primary"
                size="small"
                :disabled="metricsLoading"
                @click="applyDrivingMetrics"
              >
                采纳建议
              </el-button>
              <el-button
                v-else
                type="success"
                size="small"
                disabled
                class="route-amap-adopted-btn"
              >
                已采纳
              </el-button>
            </template>

            <template v-else-if="showSavedMetricsHint">
              <div class="route-amap-suggest-metrics route-amap-suggest-metrics--saved">
                <div v-if="form.distance != null" class="route-amap-metric">
                  <span class="route-amap-metric-label">里程</span>
                  <span class="route-amap-metric-value">
                    {{ form.distance }}
                    <small>km</small>
                  </span>
                </div>
                <div v-if="form.estimatedHours != null" class="route-amap-metric">
                  <span class="route-amap-metric-label">预计时长</span>
                  <span class="route-amap-metric-value">
                    {{ form.estimatedHours }}
                    <small>h</small>
                  </span>
                </div>
                <p
                  v-if="form.distance == null && form.estimatedHours == null"
                  class="route-amap-suggest-empty"
                >
                  暂无已保存的里程与时长
                </p>
              </div>
              <p class="route-amap-suggest-note">{{ amapSuggestNote }}</p>
              <el-button
                type="primary"
                plain
                size="small"
                :disabled="metricsLoading"
                @click="fetchDrivingMetrics"
              >
                重新获取高德建议
              </el-button>
            </template>

            <template v-else-if="metricsError">
              <p class="route-amap-suggest-error">{{ metricsError }}</p>
              <p class="route-amap-suggest-note">{{ amapSuggestNote }}</p>
            </template>

            <template v-else-if="metricsLoading">
              <p class="route-amap-suggest-status">正在获取高德建议…</p>
              <p class="route-amap-suggest-note">{{ amapSuggestNote }}</p>
            </template>

            <template v-else>
              <p class="route-amap-suggest-status">
                修改起终点后将自动获取高德建议
              </p>
              <p class="route-amap-suggest-note">{{ amapSuggestNote }}</p>
            </template>
          </div>
        </el-form>
      </el-col>

      <el-col :xs="24" :sm="12" class="route-edit-right">
        <route-map-preview
          :visible="visible"
          :origin="mapOrigin"
          :destination="mapDestination"
          :path="mapPolylinePath"
        />
      </el-col>
    </el-row>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { CascaderProps, FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    addRoute,
    updateRoute,
    getRouteDrivingMetrics
  } from '@/api/resource/route';
  import type {
    Route,
    RouteDrivingMetrics,
    RouteRegionPoint
  } from '@/api/resource/route/model';
  import { getRegionNavTree, getRegion } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';
  import RouteMapPreview from './route-map-preview.vue';

  const props = defineProps<{
    visible: boolean;
    data: Route | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Route>({});
  const regionTree = ref<RegionNavNode[]>([]);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  const drivingMetrics = ref<RouteDrivingMetrics | null>(null);
  const metricsLoading = ref(false);
  const metricsError = ref('');
  const metricsAdopted = ref(false);
  /** 编辑打开时用地区库坐标展示地图标点（不调高德） */
  const mapPreview = ref<{
    origin: RouteRegionPoint | null;
    destination: RouteRegionPoint | null;
  } | null>(null);
  const initialRegionPair = ref<{
    originRegionId?: number;
    destinationRegionId?: number;
  } | null>(null);
  /** 编辑打开时从库中回显的折线（不调高德） */
  const savedPolyline = ref<number[][] | null>(null);
  let metricsTimer: ReturnType<typeof setTimeout> | null = null;
  let metricsRequestId = 0;

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const canFetchMetrics = computed(
    () =>
      !!(
        form.originRegionId &&
        form.destinationRegionId &&
        form.originRegionId !== form.destinationRegionId
      )
  );

  const regionPairChanged = computed(() => {
    if (!initialRegionPair.value) return true;
    const init = initialRegionPair.value;
    return (
      form.originRegionId !== init.originRegionId ||
      form.destinationRegionId !== init.destinationRegionId
    );
  });

  const showSavedMetricsHint = computed(
    () =>
      isEdit.value &&
      !regionPairChanged.value &&
      !drivingMetrics.value &&
      !metricsLoading.value &&
      !metricsError.value
  );

  const amapSuggestNote =
    '里程与路线轨迹基于驾车导航、高速优先策略统计，仅供参考，采纳后可写入标准值。';

  const suggestTitle = computed(() => {
    if (drivingMetrics.value) return '高德建议';
    if (showSavedMetricsHint.value) return '已保存标准值';
    return '路线参考';
  });

  const mapOrigin = computed(
    () => drivingMetrics.value?.origin ?? mapPreview.value?.origin ?? null
  );
  const mapDestination = computed(
    () =>
      drivingMetrics.value?.destination ?? mapPreview.value?.destination ?? null
  );
  const mapPolylinePath = computed(
    () =>
      drivingMetrics.value?.polylinePath ??
      savedPolyline.value ??
      null
  );

  const rules = computed<FormRules>(() => {
    const r: FormRules = {
      originCode: [
        { required: true, message: '请选择出发地', trigger: 'change' }
      ],
      destinationCode: [
        { required: true, message: '请选择目的地', trigger: 'change' }
      ]
    };
    if (isEdit.value) {
      r.routeName = [
        { required: true, message: '请输入线路名称', trigger: 'blur' }
      ];
    }
    return r;
  });

  const clearMetricsState = () => {
    drivingMetrics.value = null;
    metricsError.value = '';
    metricsLoading.value = false;
    metricsAdopted.value = false;
    mapPreview.value = null;
    savedPolyline.value = null;
    if (metricsTimer) {
      clearTimeout(metricsTimer);
      metricsTimer = null;
    }
  };

  const buildPolylinePayload = (): Pick<
    Route,
    'routePolyline' | 'clearRoutePolyline'
  > => {
    const path = drivingMetrics.value?.polylinePath;
    if (path && path.length >= 2) {
      return { routePolyline: path };
    }
    if (isEdit.value && regionPairChanged.value) {
      return { clearRoutePolyline: true };
    }
    return {};
  };

  const toRegionPoint = (
    regionId: number,
    name: string,
    r: { longitude?: number | null; latitude?: number | null; name?: string }
  ): RouteRegionPoint | null => {
    if (r.longitude == null || r.latitude == null) return null;
    return {
      regionId,
      name: name || r.name || '',
      longitude: Number(r.longitude),
      latitude: Number(r.latitude)
    };
  };

  /** 编辑态打开：仅用地区库经纬度标点，不请求高德 */
  async function hydrateMapPreviewFromRegions() {
    const oId = form.originRegionId;
    const dId = form.destinationRegionId;
    if (!oId || !dId) {
      mapPreview.value = null;
      return;
    }
    const [o, d] = await Promise.all([
      getRegion(oId).catch(() => null),
      getRegion(dId).catch(() => null)
    ]);
    mapPreview.value = {
      origin: o ? toRegionPoint(oId, form.origin || '', o) : null,
      destination: d ? toRegionPoint(dId, form.destination || '', d) : null
    };
  }

  const scheduleFetchMetrics = () => {
    if (metricsTimer) {
      clearTimeout(metricsTimer);
    }
    if (!canFetchMetrics.value) {
      clearMetricsState();
      return;
    }
    // 编辑且起终点未改：不自动调高德（仅展示已保存值 + 手动刷新）
    if (isEdit.value && !regionPairChanged.value) {
      return;
    }
    metricsTimer = setTimeout(() => {
      fetchDrivingMetrics();
    }, 400);
  };

  const fetchDrivingMetrics = async () => {
    const oId = form.originRegionId;
    const dId = form.destinationRegionId;
    if (!oId || !dId || oId === dId) {
      clearMetricsState();
      return;
    }

    const reqId = ++metricsRequestId;
    metricsLoading.value = true;
    metricsError.value = '';
    drivingMetrics.value = null;
    metricsAdopted.value = false;

    try {
      const data = await getRouteDrivingMetrics(oId, dId);
      if (reqId !== metricsRequestId) return;
      drivingMetrics.value = data;
    } catch (e: unknown) {
      if (reqId !== metricsRequestId) return;
      metricsError.value =
        e instanceof Error ? e.message : '获取高德建议失败';
    } finally {
      if (reqId === metricsRequestId) {
        metricsLoading.value = false;
      }
    }
  };

  const applyDrivingMetrics = () => {
    if (!drivingMetrics.value) return;
    form.distance = drivingMetrics.value.distanceKm;
    form.estimatedHours = drivingMetrics.value.estimatedHours;
    if ((drivingMetrics.value.polylinePath?.length ?? 0) >= 2) {
      savedPolyline.value = drivingMetrics.value.polylinePath!;
    }
    metricsAdopted.value = true;
    EleMessage.success({ message: '已采纳高德建议', plain: true });
  };

  const findRegionName = (codes: string[]): string => {
    if (!codes.length) return '';
    const names: string[] = [];
    let nodes = regionTree.value;
    for (const code of codes) {
      const node = nodes.find((n) => n.code === code);
      if (node) {
        names.push(node.name);
        nodes = node.children ?? [];
      }
    }
    return names.join('/');
  };

  const onRegionSelectionChanged = async () => {
    drivingMetrics.value = null;
    metricsError.value = '';
    metricsAdopted.value = false;
    if (regionPairChanged.value) {
      savedPolyline.value = null;
    }
    if (canFetchMetrics.value) {
      await hydrateMapPreviewFromRegions();
    } else {
      mapPreview.value = null;
    }
    scheduleFetchMetrics();
  };

  const onOriginChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.originCode = val[val.length - 1];
      form.origin = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.originRegionId = leaf?.regionId ?? undefined;
    } else {
      form.originCode = undefined;
      form.origin = undefined;
      form.originRegionId = undefined;
    }
    onRegionSelectionChanged();
  };

  const onDestChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.destinationRegionId = leaf?.regionId ?? undefined;
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
      form.destinationRegionId = undefined;
    }
    onRegionSelectionChanged();
  };

  async function hydrateRegionCodesFromIds() {
    const oId = form.originRegionId;
    if (oId && !form.originCode) {
      const r = await getRegion(oId).catch(() => null);
      if (r?.code) form.originCode = r.code;
    }
    const dId = form.destinationRegionId;
    if (dId && !form.destinationCode) {
      const r = await getRegion(dId).catch(() => null);
      if (r?.code) form.destinationCode = r.code;
    }
  }

  watch(
    () => props.visible,
    async (val) => {
      if (!val) {
        clearMetricsState();
        metricsRequestId++;
        return;
      }
      try {
        regionTree.value = (await getRegionNavTree()) ?? [];
      } catch {
        regionTree.value = [];
      }
      originCodes.value = [];
      destCodes.value = [];
      clearMetricsState();
      initialRegionPair.value = null;

      if (props.data?.id) {
        Object.assign(form, props.data);
        await hydrateRegionCodesFromIds();
        if (form.originCode) {
          const op = findRegionCodePath(regionTree.value, form.originCode);
          originCodes.value = op ?? [form.originCode];
        }
        if (form.destinationCode) {
          const dp = findRegionCodePath(regionTree.value, form.destinationCode);
          destCodes.value = dp ?? [form.destinationCode];
        }
        const oLeaf = findLeafRegionByCodePath(
          regionTree.value,
          originCodes.value
        );
        const dLeaf = findLeafRegionByCodePath(
          regionTree.value,
          destCodes.value
        );
        if (oLeaf) form.originRegionId = oLeaf.regionId;
        if (dLeaf) form.destinationRegionId = dLeaf.regionId;
        initialRegionPair.value = {
          originRegionId: form.originRegionId,
          destinationRegionId: form.destinationRegionId
        };
        const stored = props.data?.polylinePath;
        savedPolyline.value =
          stored && stored.length >= 2 ? stored : null;
        await hydrateMapPreviewFromRegions();
      } else {
        Object.keys(form).forEach((k) => {
          (form as Record<string, unknown>)[k] = undefined;
        });
      }
      formRef.value?.clearValidate();
    }
  );

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      if (!form.originRegionId || !form.destinationRegionId) {
        EleMessage.warning({ message: '请选择出发地与目的地', plain: true });
        return;
      }
      loading.value = true;
      try {
        const polylinePayload = buildPolylinePayload();
        if (isEdit.value) {
          await updateRoute({
            id: form.id,
            routeName: form.routeName?.trim(),
            originRegionId: form.originRegionId,
            destinationRegionId: form.destinationRegionId,
            distance: form.distance,
            estimatedHours: form.estimatedHours,
            remark: form.remark,
            ...polylinePayload
          });
        } else {
          await addRoute({
            originRegionId: form.originRegionId,
            destinationRegionId: form.destinationRegionId,
            distance: form.distance,
            estimatedHours: form.estimatedHours,
            remark: form.remark,
            ...polylinePayload
          });
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : '操作失败';
        EleMessage.error({ message: msg, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .route-edit-form :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  .route-edit-left {
    padding-right: 4px;
  }

  .route-edit-right {
    width: 100%;
  }

  .route-amap-suggest {
    margin-top: 8px;
    padding: 14px 14px 12px;
    border-radius: 8px;
    background: linear-gradient(
      135deg,
      var(--el-color-primary-light-9) 0%,
      var(--el-fill-color-blank) 48%
    );
    border: 1px solid var(--el-color-primary-light-7);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  }

  .route-amap-suggest-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 10px;
  }

  .route-amap-suggest-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.3;
  }

  .route-amap-suggest-tag {
    flex-shrink: 0;
    padding: 2px 8px;
    font-size: 11px;
    line-height: 18px;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-8);
    border-radius: 4px;
  }

  .route-amap-suggest-metrics {
    display: flex;
    gap: 20px;
    margin-bottom: 10px;
  }

  .route-amap-suggest-metrics--saved .route-amap-metric-value {
    color: var(--el-text-color-primary);
  }

  .route-amap-metric {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .route-amap-metric-label {
    font-size: 12px;
    color: var(--el-text-color-regular);
  }

  .route-amap-metric-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
    line-height: 1.2;
  }

  .route-amap-metric-value small {
    margin-left: 2px;
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
  }

  .route-amap-suggest-note {
    margin: 0 0 10px;
    font-size: 12px;
    line-height: 1.55;
    color: var(--el-text-color-regular);
  }

  .route-amap-suggest-status,
  .route-amap-suggest-empty {
    margin: 0 0 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.5;
  }

  .route-amap-suggest-error {
    margin: 0 0 8px;
    font-size: 13px;
    color: var(--el-color-danger);
    line-height: 1.5;
  }

  .route-amap-adopted-btn.is-disabled {
    opacity: 1;
    color: #fff;
    background-color: var(--el-color-success);
    border-color: var(--el-color-success);
  }
</style>
