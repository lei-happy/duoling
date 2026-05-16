<template>
  <el-dialog
    :title="isEdit ? '编辑任务单' : '新增任务单'"
    :model-value="visible"
    width="880px"
    draggable
    class="waybill-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    append-to-body
    destroy-on-close
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="110px"
      class="waybill-edit-form"
      :validate-on-rule-change="false"
      v-loading="submitting"
      @submit.prevent=""
    >
      <div v-if="isEdit" class="task-edit-meta-bar">
        <span class="task-edit-meta-bar__item"
          >任务单号：<b>{{ form.taskNo || '—' }}</b></span
        >
        <span class="task-edit-meta-bar__item"
          >任务名称：<b>{{ form.taskName || '—' }}</b></span
        >
      </div>
      <el-tabs
        v-model="activeTab"
        class="waybill-edit-tabs"
        @tab-change="onTabChange"
      >
        <el-tab-pane name="cargo">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': cargoStepDone }"
              >
                <el-icon v-if="cargoStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('cargo') }}</template>
              </span>
              <span class="waybill-tab-text">
                选择商品车
                <span v-if="cargoTabSubVisible" class="waybill-tab-sub">
                  · {{ form.waybillItems.length }} 条 / {{ cargoTotalQty }} 台
                </span>
              </span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <el-alert
              v-if="!isEdit"
              type="info"
              :closable="false"
              show-icon
              class="task-cargo-open-tip"
              title="任务单号、任务名称将在保存时由系统自动生成；若各段填写了计划装车/到达时间，将同步为任务计划时间。"
            />
            <task-cargo-picker
              v-model="form.waybillItems"
              :segments="form.segments"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane name="segments">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': segmentsStepDone }"
              >
                <el-icon v-if="segmentsStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('segments') }}</template>
              </span>
              <span class="waybill-tab-text">
                运输路线规划
                <span v-if="form.segments?.length" class="waybill-tab-sub">
                  · {{ form.segments.length }} 段
                </span>
              </span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <task-segment-table v-model="form.segments" />
          </div>
        </el-tab-pane>

        <el-tab-pane name="carrier">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': carrierStepDone }"
              >
                <el-icon v-if="carrierStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('carrier') }}</template>
              </span>
              <span class="waybill-tab-text">选择承运方</span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <task-carrier-picker ref="carrierRef" v-model="form.carrier" />
          </div>
        </el-tab-pane>

        <el-tab-pane name="remark">
          <template #label>
            <span class="waybill-tab-label">
              <span
                class="waybill-tab-idx"
                :class="{ 'is-done': remarkStepDone }"
              >
                <el-icon v-if="remarkStepDone" class="waybill-tab-check"
                  ><CircleCheck
                /></el-icon>
                <template v-else>{{ tabStepNo('remark') }}</template>
              </span>
              <span class="waybill-tab-text">备注</span>
            </span>
          </template>
          <div class="waybill-tab-pane">
            <el-alert
              type="info"
              :closable="false"
              show-icon
              class="task-remark-tip"
              title="可选。承运成本等由系统/后续流程计算，此处仅作说明性备注。"
            />
            <el-form-item label="备注" label-position="top">
              <el-input
                v-model="form.remark"
                type="textarea"
                :rows="5"
                maxlength="500"
                show-word-limit
                placeholder="调度说明、客户特殊要求等（选填）"
              />
            </el-form-item>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <div class="waybill-edit-dialog__footer">
        <el-button @click="updateVisible(false)">取消</el-button>
        <el-button :disabled="stepActive <= 0" @click="prevStep">
          上一步
        </el-button>
        <el-button
          :disabled="isLastTabStep"
          type="primary"
          plain
          @click="onClickNextStep"
        >
          下一步
        </el-button>
        <el-button type="primary" :loading="saveLoading" @click="submit">
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { CircleCheck } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import TaskSegmentTable from './task-segment-table.vue';
  import TaskCargoPicker from './task-cargo-picker.vue';
  import TaskCarrierPicker from './task-carrier-picker.vue';
  import { addTask, getTask, updateTask } from '@/api/operation/task';
  import type {
    Task,
    TaskCarrierInfo,
    TaskCreatePayload,
    TaskSegment,
    TaskWaybillItem
  } from '@/api/operation/task/model';

  const TAB_ORDER = ['cargo', 'segments', 'carrier', 'remark'] as const;
  type TabName = (typeof TAB_ORDER)[number];

  const props = defineProps<{ visible: boolean; data: Task | null }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const carrierRef = ref<{ init: () => void } | null>(null);
  const submitting = ref(false);
  const saveLoading = ref(false);

  const isEdit = computed(() => Boolean(props.data?.id));
  const activeTab = ref<TabName>('cargo');

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const visibleTabOrder = computed((): TabName[] => [...TAB_ORDER]);

  function tabStepNo(tab: TabName): number {
    const order = visibleTabOrder.value;
    const i = order.indexOf(tab);
    return i >= 0 ? i + 1 : 1;
  }

  const stepActive = computed(() => {
    const i = visibleTabOrder.value.indexOf(activeTab.value);
    return i >= 0 ? i : 0;
  });

  const isLastTabStep = computed(() => {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i < 0) return true;
    return i >= order.length - 1;
  });

  const defaultForm = (): TaskCreatePayload => ({
    taskNo: '',
    taskName: '',
    source: 1,
    plannedLoadTime: undefined,
    plannedArriveTime: undefined,
    remark: '',
    carrier: {
      carrierType: 1,
      capacityId: undefined,
      carrierId: undefined,
      mainDriverName: '',
      mainDriverPhone: '',
      mainDriverIdCard: '',
      plateNumber: '',
      trailerPlateNumber: '',
      carrierName: '',
      carrierShortName: ''
    },
    segments: [
      {
        segmentNo: 1,
        fromLocation: '',
        toLocation: '',
        plannedLoadTime: undefined,
        plannedArriveTime: undefined
      }
    ],
    waybillItems: []
  });

  const form = reactive<TaskCreatePayload>(defaultForm());

  const rules: FormRules = {};

  const segmentsStepDone = computed(() => {
    if (!form.segments?.length) return false;
    return form.segments.every(
      (s) => !!s.fromLocation?.trim() && !!s.toLocation?.trim()
    );
  });

  const cargoTotalQty = computed(() =>
    (form.waybillItems || []).reduce(
      (sum, it) => sum + (Number(it.quantity) || 0),
      0
    )
  );

  const cargoStepDone = computed(() => {
    if (!form.waybillItems?.length) return false;
    return form.waybillItems.every((it) => Number(it.quantity) > 0);
  });

  const cargoTabSubVisible = computed(
    () => form.waybillItems.length > 0 && cargoTotalQty.value > 0
  );

  const carrierStepDone = computed(() => {
    const c = form.carrier!;
    if (c.carrierType === 1) {
      return !!(
        c.capacityId ||
        (c.mainDriverName?.trim() && c.plateNumber?.trim())
      );
    }
    if (c.carrierType === 2) {
      return !!(c.carrierId || c.carrierName?.trim());
    }
    if (c.carrierType === 3) {
      return !!(
        c.mainDriverName?.trim() &&
        c.mainDriverPhone?.trim() &&
        c.plateNumber?.trim()
      );
    }
    return false;
  });

  /** 备注为选填：填写内容后 Tab 上显示完成态 */
  const remarkStepDone = computed(() => !!form.remark?.trim());

  watch(
    () => props.visible,
    async (v) => {
      if (!v) return;
      activeTab.value = 'cargo';
      Object.assign(form, defaultForm());
      if (props.data?.id) {
        await loadDetail(props.data.id);
      }
      await nextTick(() => {
        formRef.value?.clearValidate();
        carrierRef.value?.init();
      });
    }
  );

  const loadDetail = async (id: number) => {
    submitting.value = true;
    try {
      const detail = await getTask(id);
      if (!detail) return;
      form.taskNo = detail.taskNo || '';
      form.taskName = detail.taskName || '';
      form.source = detail.source || 1;
      form.plannedLoadTime = detail.plannedLoadTime;
      form.plannedArriveTime = detail.plannedArriveTime;
      form.remark = detail.remark || '';
      form.carrier = {
        carrierType: detail.carrierType || 1,
        capacityId: detail.capacityId ?? undefined,
        carrierId: detail.carrierId ?? undefined,
        socialDriverId: detail.socialDriverId ?? undefined,
        mainDriverName: detail.mainDriverName || '',
        mainDriverPhone: detail.mainDriverPhone || '',
        mainDriverIdCard: detail.mainDriverIdCard || '',
        plateNumber: detail.plateNumber || '',
        trailerPlateNumber: detail.trailerPlateNumber || '',
        carrierName: detail.carrierName || '',
        carrierShortName: detail.carrierShortName || ''
      };
      form.segments = (detail.segments || []).map((s: TaskSegment) => ({
        segmentNo: s.segmentNo,
        fromLocation: s.fromLocation,
        fromCode: s.fromCode,
        fromRegionId: s.fromRegionId,
        toLocation: s.toLocation,
        toCode: s.toCode,
        toRegionId: s.toRegionId,
        mileage: s.mileage,
        plannedLoadTime: s.plannedLoadTime,
        plannedArriveTime: s.plannedArriveTime,
        remark: s.remark
      }));
      form.waybillItems = (detail.waybillItems || []).map(
        (w: TaskWaybillItem) =>
          ({
            waybillId: w.waybillId,
            waybillCargoId: w.waybillCargoId,
            quantity: w.quantity,
            segmentId: w.segmentId,
            remark: w.remark,
            waybillNo: w.waybillNo,
            customerName: w.customerName,
            vehicleBrand: w.vehicleBrand,
            vehicleModel: w.vehicleModel,
            dealerName: w.dealerName,
            _availableRemaining: w.quantity
          }) as never
      );
    } finally {
      submitting.value = false;
    }
  };

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  function validateSegments(): boolean {
    if (form.segments.length < 1) {
      EleMessage.warning({ message: '至少需要 1 段运输路线', plain: true });
      activeTab.value = 'segments';
      return false;
    }
    for (const s of form.segments) {
      if (!s.fromLocation?.trim() || !s.toLocation?.trim()) {
        EleMessage.warning({
          message: `第 ${s.segmentNo} 段起点/终点不能为空`,
          plain: true
        });
        activeTab.value = 'segments';
        return false;
      }
    }
    return true;
  }

  function validateCargoTab(): boolean {
    if (form.waybillItems.length < 1) {
      EleMessage.warning({ message: '请至少选择一条商品车挂接', plain: true });
      activeTab.value = 'cargo';
      return false;
    }
    for (const it of form.waybillItems) {
      if (!it.quantity || it.quantity <= 0) {
        EleMessage.warning({
          message: '所有挂接商品车台数必须大于 0',
          plain: true
        });
        activeTab.value = 'cargo';
        return false;
      }
    }
    return true;
  }

  function validateCarrierTab(): boolean {
    const c = form.carrier!;
    if (c.carrierType === 1) {
      if (!c.capacityId && !(c.mainDriverName && c.plateNumber)) {
        EleMessage.error({
          message: '自有车任务请选择运力或填写主驾+车牌',
          plain: true
        });
        activeTab.value = 'carrier';
        return false;
      }
    } else if (c.carrierType === 2) {
      if (!c.carrierId && !c.carrierName) {
        EleMessage.error({
          message: '请选择承运商或填写承运商名称',
          plain: true
        });
        activeTab.value = 'carrier';
        return false;
      }
    } else if (c.carrierType === 3) {
      if (!c.mainDriverName || !c.mainDriverPhone || !c.plateNumber) {
        EleMessage.error({
          message: '社会运力需填写司机姓名/电话/车牌',
          plain: true
        });
        activeTab.value = 'carrier';
        return false;
      }
    }
    return true;
  }

  function prevStep() {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i > 0) activeTab.value = order[i - 1]!;
  }

  function onClickNextStep() {
    const order = visibleTabOrder.value;
    const i = order.indexOf(activeTab.value);
    if (i < 0) return;
    const tab = order[i]!;
    let ok = true;
    if (tab === 'cargo') {
      ok = validateCargoTab();
    } else if (tab === 'segments') {
      ok = validateSegments();
    } else if (tab === 'carrier') {
      ok = validateCarrierTab();
    } else if (tab === 'remark') {
      ok = true;
    }
    if (!ok) return;
    if (i < order.length - 1) activeTab.value = order[i + 1]!;
  }

  function onTabChange(name: string | number) {
    const n = String(name) as TabName;
    if (visibleTabOrder.value.includes(n)) activeTab.value = n;
    if (n === 'carrier') {
      nextTick(() => carrierRef.value?.init());
    }
  }

  const validateAllSteps = (): boolean => {
    if (!validateCargoTab()) return false;
    if (!validateSegments()) return false;
    if (!validateCarrierTab()) return false;
    return true;
  };

  /** 任务级计划时间：优先取首段装车、末段到达（与后端 _replace_segments 回填一致） */
  function syncTaskScheduleFromSegments() {
    const segs = form.segments || [];
    if (!segs.length) return;
    const head = segs[0]!;
    const tail = segs[segs.length - 1]!;
    if (head.plannedLoadTime) form.plannedLoadTime = head.plannedLoadTime;
    if (tail.plannedArriveTime) form.plannedArriveTime = tail.plannedArriveTime;
  }

  const buildSegmentsPayload = () =>
    form.segments.map((s) => ({
      segmentNo: s.segmentNo,
      fromLocation: s.fromLocation,
      fromCode: s.fromCode,
      fromRegionId: s.fromRegionId,
      toLocation: s.toLocation,
      toCode: s.toCode,
      toRegionId: s.toRegionId,
      mileage: s.mileage ?? undefined,
      plannedLoadTime: s.plannedLoadTime,
      plannedArriveTime: s.plannedArriveTime,
      remark: s.remark
    }));

  const buildWaybillItemsPayload = () =>
    form.waybillItems.map((w) => ({
      waybillId: w.waybillId,
      waybillCargoId: w.waybillCargoId,
      quantity: w.quantity,
      segmentId: w.segmentId ?? undefined,
      remark: w.remark
    }));

  const submit = async () => {
    if (!validateAllSteps()) {
      return;
    }
    syncTaskScheduleFromSegments();

    saveLoading.value = true;
    try {
      const carrier = cleanCarrier(form.carrier);
      const segments = buildSegmentsPayload();
      const waybillItems = buildWaybillItemsPayload();

      if (isEdit.value && props.data?.id) {
        await updateTask(props.data.id, {
          plannedLoadTime: form.plannedLoadTime,
          plannedArriveTime: form.plannedArriveTime,
          remark: form.remark,
          carrier,
          segments,
          waybillItems
        });
        EleMessage.success({ message: '已保存', plain: true });
      } else {
        await addTask({
          source: form.source || 1,
          plannedLoadTime: form.plannedLoadTime,
          plannedArriveTime: form.plannedArriveTime,
          remark: form.remark,
          carrier,
          segments,
          waybillItems
        } as TaskCreatePayload);
        EleMessage.success({ message: '已创建', plain: true });
      }
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saveLoading.value = false;
    }
  };

  const cleanCarrier = (c?: TaskCarrierInfo): TaskCarrierInfo | undefined => {
    if (!c) return undefined;
    const out: TaskCarrierInfo = { carrierType: c.carrierType };
    if (c.capacityId) out.capacityId = c.capacityId;
    if (c.carrierId) out.carrierId = c.carrierId;
    if (c.socialDriverId) out.socialDriverId = c.socialDriverId;
    if (c.mainDriverName?.trim()) out.mainDriverName = c.mainDriverName.trim();
    if (c.mainDriverPhone?.trim())
      out.mainDriverPhone = c.mainDriverPhone.trim();
    if (c.mainDriverIdCard?.trim())
      out.mainDriverIdCard = c.mainDriverIdCard.trim();
    if (c.plateNumber?.trim()) out.plateNumber = c.plateNumber.trim();
    if (c.trailerPlateNumber?.trim())
      out.trailerPlateNumber = c.trailerPlateNumber.trim();
    if (c.carrierName?.trim()) out.carrierName = c.carrierName.trim();
    if (c.carrierShortName?.trim())
      out.carrierShortName = c.carrierShortName.trim();
    return out;
  };
</script>

<style scoped>
  .task-edit-meta-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 16px 24px;
    padding: 10px 12px;
    margin-bottom: 10px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    background: var(--el-fill-color-light);
    border-radius: 8px;
    border: 1px solid var(--el-border-color-lighter);
  }

  .task-edit-meta-bar__item b {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .task-cargo-open-tip {
    margin-bottom: 14px;
  }

  .task-cargo-open-tip :deep(.el-alert__title) {
    line-height: 1.5;
    font-size: 13px;
  }

  .task-remark-tip {
    margin-bottom: 14px;
  }

  .task-remark-tip :deep(.el-alert__title) {
    line-height: 1.5;
    font-size: 13px;
  }

  .waybill-edit-dialog__footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
  }

  .waybill-tab-label {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    max-width: 100%;
    white-space: nowrap;
  }

  .waybill-tab-idx {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 22px;
    min-width: 22px;
    height: 22px;
    padding: 0;
    box-sizing: border-box;
    border-radius: 50%;
    font-size: 12px;
    font-weight: 600;
    line-height: 1;
    background: var(--el-fill-color-dark);
    color: var(--el-text-color-secondary);
  }

  .waybill-tab-idx.is-done {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }

  .waybill-tab-check {
    font-size: 14px;
  }

  .waybill-tab-sub {
    font-size: 11px;
    font-weight: 400;
    color: var(--el-text-color-secondary);
  }

  .waybill-tab-text {
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .waybill-edit-tabs :deep(.el-tabs__item.is-active) .waybill-tab-idx {
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }

  .waybill-edit-form {
    margin: 0;
  }

  .waybill-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .waybill-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .waybill-edit-tabs :deep(.el-tabs__item) {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0 6px;
    height: 36px;
    line-height: 36px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition:
      color 0.2s,
      background 0.2s,
      box-shadow 0.2s;
  }

  .waybill-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .waybill-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .waybill-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .waybill-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .waybill-tab-pane {
    max-height: min(420px, calc(100vh - 320px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .waybill-edit-dialog
    :deep(.waybill-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }
</style>
