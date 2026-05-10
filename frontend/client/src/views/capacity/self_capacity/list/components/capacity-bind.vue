<template>
  <el-dialog
    :model-value="visible"
    width="960px"
    draggable
    align-center
    class="capacity-bind-dialog"
    :close-on-click-modal="false"
    :body-style="{ padding: '8px 16px 12px' }"
    @update:model-value="updateVisible"
  >
    <template #header>
      <div class="capacity-bind-header">
        <span class="capacity-bind-title">新建运力</span>
        <el-tooltip placement="top-start" :show-after="200" :max-width="420">
          <template #content>
            <div class="capacity-bind-tooltip-text">
              请选择一名在职司机与一辆可用车辆，将创建一条「司机 + 车辆」运力绑定。同一司机或同一车辆在同一时刻仅能参与一条在绑运力。
            </div>
          </template>
          <el-icon class="capacity-bind-help" :size="18">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
    </template>

    <el-row :gutter="16" class="capacity-bind-split">
      <el-col :xs="24" :md="12">
        <div class="capacity-bind-panel-title">选择司机</div>
        <el-input
          v-model.trim="driverSearchInput"
          clearable
          placeholder="搜索：姓名 / 手机号（全库）"
          class="capacity-bind-filter"
        />
        <div class="capacity-bind-table-wrap capacity-bind-table-card">
          <el-table
            ref="driverTableRef"
            v-loading="loadingDrivers && drivers.length === 0"
            :data="drivers"
            :row-class-name="driverRowClassName"
            row-key="id"
            height="320"
            highlight-current-row
            border
            size="small"
            empty-text="暂无在职司机"
            @current-change="onDriverCurrentChange"
          >
            <el-table-column label="姓名" min-width="96">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isDriverRowBound(row)"
                  :content="driverRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">{{ row.name }}</span>
                </el-tooltip>
                <span v-else class="capacity-bind-tt-plain">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="手机号" min-width="130">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isDriverRowBound(row)"
                  :content="driverRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">{{ row.phone }}</span>
                </el-tooltip>
                <span v-else class="capacity-bind-tt-plain">{{ row.phone }}</span>
              </template>
            </el-table-column>
            <el-table-column label="运力" width="72" align="center">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isDriverRowBound(row)"
                  :content="driverRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">
                    <el-tag type="warning" size="small">已绑车</el-tag>
                  </span>
                </el-tooltip>
                <span v-else class="capacity-bind-free">空闲</span>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="loadingDriversMore" class="capacity-bind-more-hint">加载更多中…</div>
          <transition name="el-fade-in-linear">
            <div
              v-show="showDriverAllLoaded"
              class="capacity-bind-more-hint muted capacity-bind-toast-hint"
            >
              已加载全部
            </div>
          </transition>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="capacity-bind-panel-title">选择车辆</div>
        <el-input
          v-model.trim="vehicleSearchInput"
          clearable
          placeholder="搜索：车牌 / 品牌 / 型号 / 挂车（全库）"
          class="capacity-bind-filter"
        />
        <div class="capacity-bind-table-wrap capacity-bind-table-card">
          <el-table
            ref="vehicleTableRef"
            v-loading="loadingVehicles && vehicles.length === 0"
            :data="vehicles"
            :row-class-name="vehicleRowClassName"
            row-key="id"
            height="320"
            highlight-current-row
            border
            size="small"
            empty-text="暂无可用车辆"
            @current-change="onVehicleCurrentChange"
          >
            <el-table-column label="车牌号" min-width="110">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isVehicleRowBound(row)"
                  :content="vehicleRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">{{ row.plateNumber }}</span>
                </el-tooltip>
                <span v-else class="capacity-bind-tt-plain">{{ row.plateNumber }}</span>
              </template>
            </el-table-column>
            <el-table-column label="挂车" min-width="120">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isVehicleRowBound(row)"
                  :content="vehicleRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">
                    <span v-if="row.trailerPlateNumber">{{ row.trailerPlateNumber }}</span>
                    <span v-else class="capacity-bind-muted">—</span>
                  </span>
                </el-tooltip>
                <template v-else>
                  <span v-if="row.trailerPlateNumber">{{ row.trailerPlateNumber }}</span>
                  <span v-else class="capacity-bind-muted">—</span>
                </template>
              </template>
            </el-table-column>
            <el-table-column label="运力" width="72" align="center">
              <template #default="{ row }">
                <el-tooltip
                  v-if="isVehicleRowBound(row)"
                  :content="vehicleRowDisabledTip(row)"
                  placement="top"
                  :show-after="150"
                >
                  <span class="capacity-bind-tt-cell">
                    <el-tag type="warning" size="small">已绑人</el-tag>
                  </span>
                </el-tooltip>
                <span v-else class="capacity-bind-free">空闲</span>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="loadingVehiclesMore" class="capacity-bind-more-hint">加载更多中…</div>
          <transition name="el-fade-in-linear">
            <div
              v-show="showVehicleAllLoaded"
              class="capacity-bind-more-hint muted capacity-bind-toast-hint"
            >
              已加载全部
            </div>
          </transition>
        </div>
      </el-col>
    </el-row>

    <el-alert
      v-if="driverBoundPlate"
      type="warning"
      show-icon
      :closable="false"
      class="capacity-bind-alert"
      :title="`该司机当前已绑定车辆「${driverBoundPlate}」，请先下车后再新建运力。`"
    />
    <el-alert
      v-if="vehicleBoundDriver"
      type="warning"
      show-icon
      :closable="false"
      class="capacity-bind-alert"
      :title="`该车辆当前已由「${vehicleBoundDriver.name}」${vehicleBoundDriver.phone ? `（${vehicleBoundDriver.phone}）` : ''}驾驶，请先解绑后再分配。`"
    />

    <div class="capacity-bind-preview-title">即将创建的运力</div>
    <div class="capacity-bind-preview-card">
      <div class="capacity-bind-preview-main">
        <template v-if="!selectedDriver && !selectedVehicle">
          <span class="capacity-bind-preview-empty">请在上表选择司机与车辆</span>
        </template>
        <template v-else-if="selectedDriver && selectedVehicle">
          <span class="capacity-bind-preview-name">{{ selectedDriver.name }}</span>
          <span v-if="phoneDigits4Only(selectedDriver.phone)" class="capacity-bind-preview-sub">
            （{{ phoneDigits4Only(selectedDriver.phone) }}）
          </span>
          <span class="capacity-bind-preview-dot" aria-hidden="true">·</span>
          <span class="capacity-bind-preview-plate">{{ selectedVehicle.plateNumber }}</span>
          <span v-if="selectedVehicle.trailerPlateNumber" class="capacity-bind-preview-sub">
            （{{ selectedVehicle.trailerPlateNumber }}）
          </span>
        </template>
        <template v-else-if="selectedDriver">
          <span class="capacity-bind-preview-name">{{ selectedDriver.name }}</span>
          <span v-if="phoneDigits4Only(selectedDriver.phone)" class="capacity-bind-preview-sub">
            （{{ phoneDigits4Only(selectedDriver.phone) }}）
          </span>
          <span class="capacity-bind-preview-hint">请选择右侧车辆</span>
        </template>
        <template v-else>
          <span class="capacity-bind-preview-plate">{{ selectedVehicle?.plateNumber }}</span>
          <span class="capacity-bind-preview-hint">请选择左侧司机</span>
        </template>
      </div>
      <div class="capacity-bind-remark-wrap">
        <el-input
          v-model.trim="remark"
          class="capacity-bind-remark-input"
          type="textarea"
          :rows="2"
          maxlength="500"
          show-word-limit
          placeholder="备注（选填）"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button
        type="primary"
        :loading="loadingSubmit"
        :disabled="submitDisabled"
        @click="handleSubmit"
      >
        确认创建运力
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, shallowRef, computed, watch, nextTick, onBeforeUnmount } from 'vue';
  import { watchDebounced } from '@vueuse/core';
  import { EleMessage } from 'ele-admin-plus';
  import { QuestionFilled } from '@element-plus/icons-vue';
  import type { TableInstance } from 'element-plus';
  import { pageDrivers } from '@/api/capacity/self_capacity/driver';
  import { pageVehicles } from '@/api/capacity/self_capacity/vehicle';
  import type { Driver } from '@/api/capacity/self_capacity/driver/model';
  import type { Vehicle } from '@/api/capacity/self_capacity/vehicle/model';
  import { bindCapacity, pageCapacities } from '@/api/capacity/self_capacity/list';
  import type { Capacity } from '@/api/capacity/self_capacity/list/model';

  const PAGE_SIZE = 30;

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const loadingSubmit = ref(false);
  /** 打开弹窗后短时间内忽略搜索防抖，避免与首次拉取重复请求 */
  const initGuardUntil = ref(0);

  const drivers = ref<Driver[]>([]);
  const driverSearchInput = ref('');
  const driverNextPage = ref(1);
  const driverTotal = ref(0);
  const loadingDrivers = ref(false);
  const loadingDriversMore = ref(false);

  const vehicles = ref<Vehicle[]>([]);
  const vehicleSearchInput = ref('');
  const vehicleNextPage = ref(1);
  const vehicleTotal = ref(0);
  const loadingVehicles = ref(false);
  const loadingVehiclesMore = ref(false);

  const remark = ref('');

  const driverToBoundPlate = ref<Record<number, string>>({});
  const vehicleToBoundDriver = ref<Record<number, { name: string; phone: string }>>({});

  const selectedDriver = shallowRef<Driver | undefined>();
  const selectedVehicle = shallowRef<Vehicle | undefined>();
  const driverTableRef = ref<TableInstance>();
  const vehicleTableRef = ref<TableInstance>();

  let driverScrollEl: HTMLElement | null = null;
  let vehicleScrollEl: HTMLElement | null = null;

  const driverHasMore = computed(
    () => driverTotal.value > 0 && drivers.value.length < driverTotal.value
  );
  const vehicleHasMore = computed(
    () => vehicleTotal.value > 0 && vehicles.value.length < vehicleTotal.value
  );

  const showDriverAllLoaded = ref(false);
  const showVehicleAllLoaded = ref(false);
  let driverAllLoadedTimer: ReturnType<typeof setTimeout> | null = null;
  let vehicleAllLoadedTimer: ReturnType<typeof setTimeout> | null = null;

  function clearDriverAllLoadedFlash() {
    if (driverAllLoadedTimer) {
      clearTimeout(driverAllLoadedTimer);
      driverAllLoadedTimer = null;
    }
    showDriverAllLoaded.value = false;
  }

  function clearVehicleAllLoadedFlash() {
    if (vehicleAllLoadedTimer) {
      clearTimeout(vehicleAllLoadedTimer);
      vehicleAllLoadedTimer = null;
    }
    showVehicleAllLoaded.value = false;
  }

  function clearAllLoadedFlashes() {
    clearDriverAllLoadedFlash();
    clearVehicleAllLoadedFlash();
  }

  function scheduleDriverAllLoadedFlash() {
    clearDriverAllLoadedFlash();
    if (
      drivers.value.length === 0 ||
      driverHasMore.value ||
      loadingDriversMore.value ||
      loadingDrivers.value
    ) {
      return;
    }
    showDriverAllLoaded.value = true;
    driverAllLoadedTimer = setTimeout(() => {
      showDriverAllLoaded.value = false;
      driverAllLoadedTimer = null;
    }, 2200);
  }

  function scheduleVehicleAllLoadedFlash() {
    clearVehicleAllLoadedFlash();
    if (
      vehicles.value.length === 0 ||
      vehicleHasMore.value ||
      loadingVehiclesMore.value ||
      loadingVehicles.value
    ) {
      return;
    }
    showVehicleAllLoaded.value = true;
    vehicleAllLoadedTimer = setTimeout(() => {
      showVehicleAllLoaded.value = false;
      vehicleAllLoadedTimer = null;
    }, 2200);
  }

  function phoneDigits4Only(phone: string | undefined | null): string {
    const digits = String(phone ?? '').replace(/\D/g, '');
    if (digits.length < 4) return '';
    return digits.slice(-4);
  }

  function isDriverRowBound(row: Driver | undefined): boolean {
    const id = row?.id;
    return id != null && !!driverToBoundPlate.value[id];
  }

  function isVehicleRowBound(row: Vehicle | undefined): boolean {
    const id = row?.id;
    return id != null && !!vehicleToBoundDriver.value[id];
  }

  function driverRowClassName({ row }: { row: Driver }) {
    return isDriverRowBound(row) ? 'capacity-bind-row-disabled' : '';
  }

  function vehicleRowClassName({ row }: { row: Vehicle }) {
    return isVehicleRowBound(row) ? 'capacity-bind-row-disabled' : '';
  }

  function driverRowDisabledTip(row: Driver): string {
    const id = row.id;
    if (id == null) return '';
    const plate = driverToBoundPlate.value[id] ?? '';
    return `该司机当前已绑定车辆「${plate}」，请先下车后再新建运力。`;
  }

  function vehicleRowDisabledTip(row: Vehicle): string {
    const id = row.id;
    if (id == null) return '';
    const o = vehicleToBoundDriver.value[id];
    if (!o) return '';
    const phone = o.phone ? `（${o.phone}）` : '';
    return `该车辆当前已由「${o.name}」${phone}驾驶，请先解绑后再分配。`;
  }

  const driverBoundPlate = computed(() => {
    const id = selectedDriver.value?.id;
    if (id == null) return '';
    return driverToBoundPlate.value[id] ?? '';
  });

  const vehicleBoundDriver = computed(() => {
    const id = selectedVehicle.value?.id;
    if (id == null) return null as { name: string; phone: string } | null;
    return vehicleToBoundDriver.value[id] ?? null;
  });

  const submitDisabled = computed(
    () =>
      !selectedDriver.value?.id ||
      !selectedVehicle.value?.id ||
      !!driverBoundPlate.value ||
      !!vehicleBoundDriver.value
  );

  function listTotal(res: { total?: number; count?: number } | undefined | null): number {
    if (!res) return 0;
    return Number(res.count ?? res.total ?? 0);
  }

  function rebuildOccupancy(rows: Capacity[]) {
    const dp: Record<number, string> = {};
    const vd: Record<number, { name: string; phone: string }> = {};
    for (const r of rows) {
      if (r.driverId != null && r.vehicleId != null) {
        dp[r.driverId] = r.plateNumber ?? '';
        vd[r.vehicleId] = {
          name: r.driverName ?? '',
          phone: r.driverPhone ?? ''
        };
      }
    }
    driverToBoundPlate.value = dp;
    vehicleToBoundDriver.value = vd;
  }

  async function loadFullOccupancy() {
    const all: Capacity[] = [];
    let page = 1;
    const limit = 100;
    try {
      while (true) {
        const res = await pageCapacities({ page, limit });
        const chunk = res?.list ?? [];
        all.push(...chunk);
        if (chunk.length < limit) break;
        page += 1;
      }
      rebuildOccupancy(all);
    } catch {
      rebuildOccupancy([]);
    }
  }

  async function loadDrivers(options: { reset: boolean }) {
    if (loadingDrivers.value || loadingDriversMore.value) return;
    if (!options.reset && !driverHasMore.value) return;

    if (options.reset) {
      driverNextPage.value = 1;
      drivers.value = [];
      driverTotal.value = 0;
    }

    const firstChunk = drivers.value.length === 0;
    if (firstChunk) loadingDrivers.value = true;
    else loadingDriversMore.value = true;

    try {
      const res = await pageDrivers({
        status: 1,
        page: driverNextPage.value,
        limit: PAGE_SIZE,
        keyword: driverSearchInput.value.trim() || undefined
      });
      const list = res?.list ?? [];
      driverTotal.value = listTotal(res as { total?: number; count?: number });
      drivers.value = [...drivers.value, ...list];
      driverNextPage.value += 1;
    } catch {
      if (options.reset) {
        drivers.value = [];
        driverTotal.value = 0;
      }
    } finally {
      loadingDrivers.value = false;
      loadingDriversMore.value = false;
      void nextTick(() => attachDriverScroll());
    }
  }

  async function loadVehicles(options: { reset: boolean }) {
    if (loadingVehicles.value || loadingVehiclesMore.value) return;
    if (!options.reset && !vehicleHasMore.value) return;

    if (options.reset) {
      vehicleNextPage.value = 1;
      vehicles.value = [];
      vehicleTotal.value = 0;
    }

    const firstChunk = vehicles.value.length === 0;
    if (firstChunk) loadingVehicles.value = true;
    else loadingVehiclesMore.value = true;

    try {
      const res = await pageVehicles({
        status: 1,
        page: vehicleNextPage.value,
        limit: PAGE_SIZE,
        keyword: vehicleSearchInput.value.trim() || undefined
      });
      const list = res?.list ?? [];
      vehicleTotal.value = listTotal(res as { total?: number; count?: number });
      vehicles.value = [...vehicles.value, ...list];
      vehicleNextPage.value += 1;
    } catch {
      if (options.reset) {
        vehicles.value = [];
        vehicleTotal.value = 0;
      }
    } finally {
      loadingVehicles.value = false;
      loadingVehiclesMore.value = false;
      void nextTick(() => attachVehicleScroll());
    }
  }

  function onDriverScroll() {
    const el = driverScrollEl;
    if (!el || loadingDrivers.value || loadingDriversMore.value) return;
    if (!driverHasMore.value) return;
    if (el.scrollHeight - el.scrollTop - el.clientHeight < 48) {
      void loadDrivers({ reset: false });
    }
  }

  function onVehicleScroll() {
    const el = vehicleScrollEl;
    if (!el || loadingVehicles.value || loadingVehiclesMore.value) return;
    if (!vehicleHasMore.value) return;
    if (el.scrollHeight - el.scrollTop - el.clientHeight < 48) {
      void loadVehicles({ reset: false });
    }
  }

  function detachDriverScroll() {
    driverScrollEl?.removeEventListener('scroll', onDriverScroll);
    driverScrollEl = null;
  }

  function detachVehicleScroll() {
    vehicleScrollEl?.removeEventListener('scroll', onVehicleScroll);
    vehicleScrollEl = null;
  }

  function attachDriverScroll() {
    void nextTick(() => {
      const el = driverTableRef.value?.$el?.querySelector(
        '.el-scrollbar__wrap'
      ) as HTMLElement | null;
      if (!el) return;
      if (el !== driverScrollEl) {
        detachDriverScroll();
        driverScrollEl = el;
        el.addEventListener('scroll', onDriverScroll, { passive: true });
      }
    });
  }

  function attachVehicleScroll() {
    void nextTick(() => {
      const el = vehicleTableRef.value?.$el?.querySelector(
        '.el-scrollbar__wrap'
      ) as HTMLElement | null;
      if (!el) return;
      if (el !== vehicleScrollEl) {
        detachVehicleScroll();
        vehicleScrollEl = el;
        el.addEventListener('scroll', onVehicleScroll, { passive: true });
      }
    });
  }

  function resetDialog() {
    clearAllLoadedFlashes();
    driverSearchInput.value = '';
    vehicleSearchInput.value = '';
    remark.value = '';
    selectedDriver.value = undefined;
    selectedVehicle.value = undefined;
    drivers.value = [];
    vehicles.value = [];
    driverNextPage.value = 1;
    vehicleNextPage.value = 1;
    driverTotal.value = 0;
    vehicleTotal.value = 0;
    detachDriverScroll();
    detachVehicleScroll();
  }

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        initGuardUntil.value = Date.now() + 500;
        resetDialog();
        void loadFullOccupancy();
        void loadDrivers({ reset: true });
        void loadVehicles({ reset: true });
        void nextTick(() => {
          driverTableRef.value?.setCurrentRow();
          vehicleTableRef.value?.setCurrentRow();
        });
      } else {
        clearAllLoadedFlashes();
        detachDriverScroll();
        detachVehicleScroll();
      }
    }
  );

  watchDebounced(
    driverSearchInput,
    () => {
      if (!props.visible) return;
      if (Date.now() < initGuardUntil.value) return;
      void loadDrivers({ reset: true });
    },
    { debounce: 320 }
  );

  watchDebounced(
    vehicleSearchInput,
    () => {
      if (!props.visible) return;
      if (Date.now() < initGuardUntil.value) return;
      void loadVehicles({ reset: true });
    },
    { debounce: 320 }
  );

  watch(
    () =>
      [
        drivers.value.length,
        driverHasMore.value,
        loadingDriversMore.value,
        loadingDrivers.value
      ] as const,
    () => {
      scheduleDriverAllLoadedFlash();
    }
  );

  watch(
    () =>
      [
        vehicles.value.length,
        vehicleHasMore.value,
        loadingVehiclesMore.value,
        loadingVehicles.value
      ] as const,
    () => {
      scheduleVehicleAllLoadedFlash();
    }
  );

  watch(drivers, (list) => {
    const sid = selectedDriver.value?.id;
    if (sid != null && !list.some((d) => d.id === sid)) {
      selectedDriver.value = undefined;
      void nextTick(() => driverTableRef.value?.setCurrentRow());
    }
  });

  watch(vehicles, (list) => {
    const sid = selectedVehicle.value?.id;
    if (sid != null && !list.some((v) => v.id === sid)) {
      selectedVehicle.value = undefined;
      void nextTick(() => vehicleTableRef.value?.setCurrentRow());
    }
  });

  const onDriverCurrentChange = (row: Driver | undefined) => {
    if (isDriverRowBound(row)) {
      void nextTick(() => {
        const prev = selectedDriver.value;
        driverTableRef.value?.setCurrentRow(
          prev?.id != null ? drivers.value.find((d) => d.id === prev.id) : undefined
        );
      });
      return;
    }
    selectedDriver.value = row ?? undefined;
  };

  const onVehicleCurrentChange = (row: Vehicle | undefined) => {
    if (isVehicleRowBound(row)) {
      void nextTick(() => {
        const prev = selectedVehicle.value;
        vehicleTableRef.value?.setCurrentRow(
          prev?.id != null ? vehicles.value.find((v) => v.id === prev.id) : undefined
        );
      });
      return;
    }
    selectedVehicle.value = row ?? undefined;
  };

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = async () => {
    if (submitDisabled.value) return;
    loadingSubmit.value = true;
    try {
      await bindCapacity({
        driverId: selectedDriver.value!.id!,
        vehicleId: selectedVehicle.value!.id!,
        remark: remark.value || undefined
      });
      EleMessage.success({ message: '运力创建成功', plain: true });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loadingSubmit.value = false;
    }
  };

  onBeforeUnmount(() => {
    clearAllLoadedFlashes();
    detachDriverScroll();
    detachVehicleScroll();
  });
</script>

<style scoped>
  .capacity-bind-header {
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }

  .capacity-bind-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .capacity-bind-help {
    cursor: help;
    color: var(--el-text-color-secondary);
    vertical-align: middle;
    outline: none;
  }

  .capacity-bind-help:hover {
    color: var(--el-color-primary);
  }

  .capacity-bind-tooltip-text {
    line-height: 1.6;
    font-size: 13px;
  }

  .capacity-bind-split {
    margin-bottom: 8px;
  }

  .capacity-bind-panel-title {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 8px;
    color: var(--el-text-color-primary);
  }

  .capacity-bind-filter {
    margin-bottom: 8px;
  }

  .capacity-bind-table-wrap {
    position: relative;
  }

  .capacity-bind-table-card {
    border-radius: 10px;
    overflow: hidden;
    background: var(--el-bg-color);
    /* 仅由表格自身描边，避免与外层 1px 叠成「粗边框」 */
    outline: none;
  }

  .capacity-bind-table-card :deep(.el-table) {
    --el-table-border-color: var(--el-border-color-lighter);
  }

  .capacity-bind-table-card :deep(.el-table__inner-wrapper::before) {
    display: none;
  }

  .capacity-bind-table-card
    :deep(
      .el-table__body tr.current-row:not(.capacity-bind-row-disabled) > td.el-table__cell
    ) {
    background-color: var(--el-color-primary-light-9) !important;
  }

  .capacity-bind-table-card
    :deep(
      .el-table__body tr.current-row:not(.capacity-bind-row-disabled) > td.el-table__cell .cell
    ) {
    color: var(--el-color-primary-dark-2);
    font-weight: 600;
  }

  .capacity-bind-table-card
    :deep(
      .el-table__body tr.current-row:not(.capacity-bind-row-disabled) > td.el-table__cell .el-tag
    ) {
    font-weight: 500;
  }

  .capacity-bind-tt-cell {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: middle;
  }

  .capacity-bind-tt-plain {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    vertical-align: middle;
  }

  .capacity-bind-table-card :deep(tr.capacity-bind-row-disabled) {
    cursor: not-allowed;
  }

  .capacity-bind-table-card :deep(tr.capacity-bind-row-disabled > td.el-table__cell) {
    background-color: var(--el-fill-color-light) !important;
    color: var(--el-text-color-disabled);
  }

  .capacity-bind-table-card :deep(tr.capacity-bind-row-disabled .el-tag) {
    opacity: 0.9;
  }

  .capacity-bind-table-card :deep(tr.capacity-bind-row-disabled.current-row > td.el-table__cell) {
    background-color: var(--el-fill-color-light) !important;
  }

  .capacity-bind-table-card :deep(tr.capacity-bind-row-disabled.current-row > td.el-table__cell .cell) {
    color: var(--el-text-color-disabled);
    font-weight: 400;
  }

  .capacity-bind-muted {
    color: var(--el-text-color-placeholder);
  }

  .capacity-bind-free {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .capacity-bind-more-hint {
    text-align: center;
    font-size: 12px;
    padding: 6px 0 4px;
    color: var(--el-text-color-secondary);
  }

  .capacity-bind-toast-hint {
    position: absolute;
    left: 50%;
    bottom: 10px;
    transform: translateX(-50%);
    z-index: 3;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    color: var(--el-color-info-dark-2);
    background: var(--el-fill-color-light);
    box-shadow: 0 1px 8px rgba(0, 0, 0, 0.08);
    pointer-events: none;
    white-space: nowrap;
  }

  .capacity-bind-toast-hint.muted {
    color: var(--el-text-color-secondary);
  }

  .capacity-bind-alert {
    margin-bottom: 10px;
  }

  .capacity-bind-preview-title {
    font-weight: 600;
    font-size: 14px;
    margin: 12px 0 8px;
  }

  .capacity-bind-preview-card {
    border-radius: 10px;
    padding: 12px 14px 14px;
    background: var(--el-fill-color-light);
    border: 1px solid var(--el-border-color-lighter);
  }

  .capacity-bind-preview-main {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 6px 10px;
    min-height: 28px;
    line-height: 1.45;
  }

  .capacity-bind-preview-name {
    font-size: 16px;
    font-weight: 700;
    color: var(--el-text-color-primary);
  }

  .capacity-bind-preview-sub {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-secondary);
  }

  .capacity-bind-preview-plate {
    font-size: 16px;
    font-weight: 700;
    color: var(--el-color-primary);
    letter-spacing: 0.02em;
  }

  .capacity-bind-preview-dot {
    font-size: 18px;
    font-weight: 700;
    color: var(--el-text-color-placeholder);
    user-select: none;
  }

  .capacity-bind-preview-empty {
    font-size: 13px;
    color: var(--el-text-color-placeholder);
  }

  .capacity-bind-preview-hint {
    font-size: 13px;
    color: var(--el-color-warning);
    font-weight: 500;
  }

  .capacity-bind-preview-card .capacity-bind-remark-wrap {
    margin-top: 12px;
  }

  .capacity-bind-remark-input :deep(.el-textarea__inner) {
    border: none;
    box-shadow: none;
    background: var(--el-bg-color);
    border-radius: 8px;
    padding: 10px 12px;
    line-height: 1.5;
    resize: vertical;
    min-height: 64px;
  }

  .capacity-bind-remark-input :deep(.el-textarea__inner:hover),
  .capacity-bind-remark-input :deep(.el-textarea__inner:focus) {
    box-shadow: none;
    background: var(--el-fill-color);
  }

  .capacity-bind-remark-input :deep(.el-input__count) {
    background: transparent;
    color: var(--el-text-color-placeholder);
  }

  .capacity-bind-preview-card :deep(.el-textarea) {
    --el-input-bg-color: var(--el-bg-color);
  }
</style>
