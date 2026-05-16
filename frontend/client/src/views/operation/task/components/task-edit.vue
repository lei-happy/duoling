<template>
  <el-drawer
    :model-value="visible"
    :title="isEdit ? '编辑任务单' : '新增任务单'"
    direction="rtl"
    size="1080px"
    :destroy-on-close="true"
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="110px"
      v-loading="submitting"
    >
      <!-- 区域 1: 基础信息 -->
      <el-divider content-position="left">
        <span class="section-title">① 基础信息</span>
      </el-divider>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="任务单号" prop="taskNo">
            <el-input
              v-model="form.taskNo"
              :placeholder="isEdit ? '不可修改' : '留空自动生成'"
              :disabled="isEdit"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="任务名称" prop="taskName">
            <el-input v-model="form.taskName" placeholder="便于检索的名称" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="计划装车" prop="plannedLoadTime">
            <el-date-picker
              v-model="form.plannedLoadTime"
              type="datetime"
              placeholder="选择"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="计划到达">
            <el-date-picker
              v-model="form.plannedArriveTime"
              type="datetime"
              placeholder="选择"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item label="备注">
            <el-input v-model="form.remark" placeholder="备注信息" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 区域 2: 分段路线 -->
      <el-divider content-position="left">
        <span class="section-title">② 运输分段</span>
      </el-divider>
      <task-segment-table v-model="form.segments" />

      <!-- 区域 3: 货物挂接 -->
      <el-divider content-position="left">
        <span class="section-title">③ 货物挂接（按台数）</span>
      </el-divider>
      <task-cargo-picker
        v-model="form.waybillItems"
        :segments="form.segments"
      />

      <!-- 区域 4: 承运方 -->
      <el-divider content-position="left">
        <span class="section-title">④ 承运方</span>
      </el-divider>
      <task-carrier-picker ref="carrierRef" v-model="form.carrier" />

      <!-- 区域 5: 承运成本（可选） -->
      <el-divider content-position="left">
        <span class="section-title">⑤ 承运成本（可选）</span>
      </el-divider>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="成本类型">
            <el-select
              v-model="form.carrierCostType"
              clearable
              placeholder="选择"
              style="width: 100%"
            >
              <el-option
                v-for="o in CARRIER_COST_TYPE_OPTIONS"
                :key="o.value"
                :value="o.value"
                :label="o.label"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="成本总额">
            <el-input-number
              v-model="form.carrierCostAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="成本备注">
            <el-input v-model="form.costRemark" placeholder="可选" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        保存
      </el-button>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import TaskSegmentTable from './task-segment-table.vue';
  import TaskCargoPicker from './task-cargo-picker.vue';
  import TaskCarrierPicker from './task-carrier-picker.vue';
  import {
    addTask,
    checkTaskNoAvailable,
    getTask,
    updateTask
  } from '@/api/operation/task';
  import type {
    Task,
    TaskCarrierInfo,
    TaskCreatePayload,
    TaskSegment,
    TaskWaybillItem
  } from '@/api/operation/task/model';
  import { CARRIER_COST_TYPE_OPTIONS } from '../status-config';

  const props = defineProps<{ visible: boolean; data: Task | null }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const carrierRef = ref<{ init: () => void } | null>(null);
  const submitting = ref(false);

  const isEdit = computed(() => Boolean(props.data?.id));

  const defaultForm = (): TaskCreatePayload => ({
    taskNo: '',
    taskName: '',
    source: 1,
    plannedLoadTime: undefined,
    plannedArriveTime: undefined,
    carrierCostType: null,
    carrierCostAmount: null,
    costRemark: '',
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

  const rules: FormRules = {
    plannedLoadTime: [{ required: true, message: '请选择计划装车时间' }]
  };

  watch(
    () => props.visible,
    async (v) => {
      if (!v) return;
      Object.assign(form, defaultForm());
      if (props.data?.id) {
        await loadDetail(props.data.id);
      }
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
      form.carrierCostType = detail.carrierCostType ?? null;
      form.carrierCostAmount = detail.carrierCostAmount ?? null;
      form.costRemark = detail.costRemark || '';
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
        (w: TaskWaybillItem) => ({
          waybillId: w.waybillId,
          waybillCargoId: w.waybillCargoId,
          quantity: w.quantity,
          segmentId: w.segmentId,
          remark: w.remark,
          // 携带回显字段
          waybillNo: w.waybillNo,
          customerName: w.customerName,
          vehicleBrand: w.vehicleBrand,
          vehicleModel: w.vehicleModel,
          dealerName: w.dealerName,
          _availableRemaining: w.quantity
        } as never)
      );
    } finally {
      submitting.value = false;
    }
  };

  const onOpen = () => {
    setTimeout(() => carrierRef.value?.init(), 0);
  };

  const validateBeforeSubmit = (): string | null => {
    if (form.segments.length < 1) return '至少需要 1 段运输';
    for (const s of form.segments) {
      if (!s.fromLocation?.trim() || !s.toLocation?.trim()) {
        return `第 ${s.segmentNo} 段起点/终点不能为空`;
      }
    }
    if (form.waybillItems.length < 1) return '至少需要 1 条货物挂接';
    for (const it of form.waybillItems) {
      if (!it.quantity || it.quantity <= 0) {
        return '所有挂接货物台数必须 > 0';
      }
    }
    const c = form.carrier!;
    if (c.carrierType === 1) {
      if (!c.capacityId && !(c.mainDriverName && c.plateNumber)) {
        return '自有车任务请选择运力或填写主驾+车牌';
      }
    } else if (c.carrierType === 2) {
      if (!c.carrierId && !c.carrierName) {
        return '请选择承运商或填写承运商名称';
      }
    } else if (c.carrierType === 3) {
      if (!c.mainDriverName || !c.mainDriverPhone || !c.plateNumber) {
        return '社会运力需填写司机姓名/电话/车牌';
      }
    }
    return null;
  };

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    const err = validateBeforeSubmit();
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }

    if (!isEdit.value && form.taskNo?.trim()) {
      const ok = await checkTaskNoAvailable(form.taskNo.trim());
      if (!ok) {
        EleMessage.error({ message: '任务单号已存在', plain: true });
        return;
      }
    }

    submitting.value = true;
    try {
      // 去掉前端临时字段
      const payload: TaskCreatePayload = {
        ...form,
        carrier: cleanCarrier(form.carrier),
        segments: form.segments.map((s) => ({
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
        })),
        waybillItems: form.waybillItems.map((w) => ({
          waybillId: w.waybillId,
          waybillCargoId: w.waybillCargoId,
          quantity: w.quantity,
          segmentId: w.segmentId ?? undefined,
          remark: w.remark
        }))
      };
      if (isEdit.value && props.data?.id) {
        await updateTask(props.data.id, payload);
        EleMessage.success({ message: '已保存', plain: true });
      } else {
        await addTask(payload);
        EleMessage.success({ message: '已创建', plain: true });
      }
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
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

<style lang="scss" scoped>
  .section-title {
    font-weight: 600;
    color: var(--el-color-primary);
  }
</style>
