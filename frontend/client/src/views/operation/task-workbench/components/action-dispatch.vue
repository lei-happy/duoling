<!--
  派车弹窗（任务单 status 0 → 1，或已派车后换车）

  改造要点：
  - 锁定承运方式：本步只能选具体运力，不允许改 carrierType（在「待分配」阶段已确定）。
  - 移除"承运成本"块：成本归属已下沉到调令/财务模块，此处不再录入。
  - 三类承运方式分支：
    * 自有车 → 选择具体运力（capacity）+ 自动回填司机/车牌；可手动覆盖
    * 承运商 → 等待承运商通过 lite 端上报运力；提供"调度员代填"兜底面板（isProxy=true）
    * 社会运力 → 从社会运力池选择 + 自动回填司机/车牌；可手动覆盖
-->
<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="780px"
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    @open="onOpen"
  >
    <el-alert
      v-if="task"
      type="info"
      :closable="false"
      style="margin-bottom: 12px"
      :title="`任务单 ${task.taskNo} · ${task.origin || '--'} → ${task.destination || '--'} · ${task.totalQuantity || 0} 台`"
    />

    <el-descriptions
      :column="2"
      border
      size="small"
      style="margin-bottom: 12px"
    >
      <el-descriptions-item label="承运方式">
        <el-tag :type="carrierTypeTag" disable-transitions>
          {{ carrierTypeLabel }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item
        v-if="form.carrier.carrierType === CARRIER_TYPE.CARRIER"
        label="承运商"
      >
        {{ task?.carrierName || '--' }}
      </el-descriptions-item>
    </el-descriptions>

    <el-form
      ref="formRef"
      :model="form"
      label-width="100px"
      v-loading="submitting"
    >
      <!-- 自有车：选具体运力 -->
      <template v-if="form.carrier.carrierType === CARRIER_TYPE.SELF">
        <el-form-item label="选择运力" required>
          <el-select
            v-model="form.carrier.capacityId"
            remote
            filterable
            clearable
            :remote-method="searchCapacities"
            placeholder="搜索司机/车牌"
            style="width: 100%"
            @change="onCapacityChange"
          >
            <el-option
              v-for="c in capacities"
              :key="c.id"
              :value="c.id!"
              :label="`${c.driverName} / ${c.plateNumber}`"
            >
              <span>{{ c.driverName }}</span>
              <span class="ele-text-secondary" style="margin-left: 8px">
                {{ c.plateNumber }} · {{ c.driverPhone }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="主驾姓名">
              <el-input v-model="form.carrier.mainDriverName" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="主驾电话">
              <el-input v-model="form.carrier.mainDriverPhone" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车牌号">
              <el-input v-model="form.carrier.plateNumber" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>

      <!-- 承运商：等待 lite 上报 + 调度员代填兜底 -->
      <template v-if="form.carrier.carrierType === CARRIER_TYPE.CARRIER">
        <el-alert
          type="info"
          :closable="false"
          style="margin-bottom: 12px"
          :title="`该任务已分配给 ${task?.carrierName || '承运商'}，等待承运商通过 LITE 端上报运力。`"
          description="若承运商暂未响应，可展开下方面板由调度员代填运力（兜底）。"
        />
        <el-collapse v-model="proxyPanelOpen">
          <el-collapse-item title="调度员代填运力（兜底）" name="proxy">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="主驾姓名" required>
                  <el-input v-model="form.carrier.mainDriverName" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="主驾电话" required>
                  <el-input v-model="form.carrier.mainDriverPhone" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="车牌号" required>
                  <el-input v-model="form.carrier.plateNumber" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="挂车牌号">
                  <el-input v-model="form.carrier.trailerPlateNumber" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
      </template>

      <!-- 社会运力 -->
      <template v-if="form.carrier.carrierType === CARRIER_TYPE.SOCIAL">
        <el-form-item label="选择运力" required>
          <el-select
            v-model="form.carrier.socialDriverId"
            remote
            filterable
            clearable
            :remote-method="searchSocialCapacities"
            placeholder="搜索姓名/手机号/车牌/编号"
            style="width: 100%"
            @change="onSocialCapacityChange"
          >
            <el-option
              v-for="c in socialCapacities"
              :key="c.id"
              :value="c.id!"
              :label="`${c.driverName} / ${c.plateNumber}`"
            >
              <span>{{ c.driverName }}</span>
              <span class="ele-text-secondary" style="margin-left: 8px">
                {{ c.plateNumber }} · {{ c.driverPhone }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="司机姓名">
              <el-input
                v-model="form.carrier.mainDriverName"
                placeholder="可手动覆盖"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="司机电话">
              <el-input v-model="form.carrier.mainDriverPhone" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="身份证号">
              <el-input v-model="form.carrier.mainDriverIdCard" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="车牌号">
              <el-input v-model="form.carrier.plateNumber" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="挂车牌号">
              <el-input v-model="form.carrier.trailerPlateNumber" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">
        {{ confirmLabel }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref } from 'vue';
  import type { FormInstance } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { assignCarrier } from '@/api/operation/task';
  import type { Task, TaskCarrierInfo } from '@/api/operation/task/model';
  import {
    CARRIER_TYPE,
    CARRIER_TYPE_OPTIONS,
    TASK_STATUS
  } from '../../task/status-config';
  import { pageCapacities } from '@/api/capacity/self-capacity/list';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';
  import {
    getSocialCapacity,
    listForDispatch
  } from '@/api/capacity/social-capacity/list';
  import type { SocialCapacitySelectItem } from '@/api/capacity/social-capacity/list/model';

  const props = defineProps<{
    visible: boolean;
    task: Task | null;
  }>();
  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const formRef = ref<FormInstance | null>(null);
  const submitting = ref(false);
  const capacities = ref<Capacity[]>([]);
  const socialCapacities = ref<SocialCapacitySelectItem[]>([]);
  const proxyPanelOpen = ref<string[]>([]);

  const defaultCarrier = (): TaskCarrierInfo => ({
    carrierType: CARRIER_TYPE.SELF,
    capacityId: undefined,
    carrierId: undefined,
    mainDriverName: '',
    mainDriverPhone: '',
    plateNumber: '',
    trailerPlateNumber: '',
    carrierName: '',
    carrierShortName: ''
  });

  const form = reactive({
    carrier: defaultCarrier(),
    isProxy: false
  });

  const isReassign = computed(
    () =>
      (props.task?.status ?? TASK_STATUS.PENDING_DISPATCH) ===
        TASK_STATUS.DISPATCHED && !!props.task?.carrierType
  );
  const title = computed(() => (isReassign.value ? '重新派车' : '派车'));
  const confirmLabel = computed(() => {
    if (form.carrier.carrierType === CARRIER_TYPE.CARRIER) {
      return form.isProxy ? '提交代填运力' : '通知承运商上报';
    }
    return isReassign.value ? '确认换车' : '确认派车';
  });

  const carrierTypeLabel = computed(() => {
    const o = CARRIER_TYPE_OPTIONS.find(
      (x) => x.value === form.carrier.carrierType
    );
    return o?.label || '--';
  });
  const carrierTypeTag = computed<'primary' | 'success' | 'warning'>(() => {
    switch (form.carrier.carrierType) {
      case 1:
        return 'primary';
      case 2:
        return 'success';
      default:
        return 'warning';
    }
  });

  const onOpen = async () => {
    if (props.task) {
      form.carrier = {
        carrierType: props.task.carrierType || 1,
        capacityId: props.task.capacityId ?? undefined,
        carrierId: props.task.carrierId ?? undefined,
        socialDriverId: props.task.socialDriverId ?? undefined,
        mainDriverName: props.task.mainDriverName || '',
        mainDriverPhone: props.task.mainDriverPhone || '',
        mainDriverIdCard: props.task.mainDriverIdCard || '',
        plateNumber: props.task.plateNumber || '',
        trailerPlateNumber: props.task.trailerPlateNumber || '',
        carrierName: props.task.carrierName || '',
        carrierShortName: props.task.carrierShortName || ''
      };
      form.isProxy = false;
      proxyPanelOpen.value = [];
      if (
        form.carrier.carrierType === CARRIER_TYPE.SELF &&
        capacities.value.length === 0
      ) {
        searchCapacities('');
      }
      if (form.carrier.carrierType === CARRIER_TYPE.SOCIAL) {
        if (socialCapacities.value.length === 0) {
          await searchSocialCapacities('');
        }
        if (form.carrier.socialDriverId) {
          await ensureSocialOptionInList(form.carrier.socialDriverId);
        }
      }
    } else {
      form.carrier = defaultCarrier();
      form.isProxy = false;
    }
  };

  const searchCapacities = async (kw: string) => {
    try {
      const res = await pageCapacities({
        keyword: kw,
        page: 1,
        limit: 20
      });
      capacities.value = res?.list || [];
    } catch {
      capacities.value = [];
    }
  };

  const onCapacityChange = (id: number) => {
    const c = capacities.value.find((x) => x.id === id);
    if (c) {
      form.carrier.mainDriverName = c.driverName;
      form.carrier.mainDriverPhone = c.driverPhone;
      form.carrier.plateNumber = c.plateNumber;
      form.carrier.trailerPlateNumber = c.trailerPlateNumber || '';
    }
  };

  const searchSocialCapacities = async (kw: string) => {
    try {
      socialCapacities.value = (await listForDispatch(kw, 50)) || [];
    } catch {
      socialCapacities.value = [];
    }
  };

  const ensureSocialOptionInList = async (id: number) => {
    if (socialCapacities.value.some((x) => x.id === id)) return;
    try {
      const detail = await getSocialCapacity(id);
      if (!detail?.id) return;
      socialCapacities.value.unshift({
        id: detail.id,
        socialCode: detail.socialCode,
        driverName: detail.driverName,
        driverPhone: detail.driverPhone,
        plateNumber: detail.plateNumber,
        vehicleType: detail.vehicleTypeLabel || detail.vehicle?.vehicleType,
        loadCapacity: detail.vehicle?.loadCapacity,
        ratingLevel: detail.ratingLevel,
        defaultAccount: detail.defaultAccount
      });
    } catch {
      // ignore
    }
  };

  const onSocialCapacityChange = async (id: number | undefined) => {
    if (!id) {
      form.carrier.mainDriverName = '';
      form.carrier.mainDriverPhone = '';
      form.carrier.mainDriverIdCard = '';
      form.carrier.plateNumber = '';
      form.carrier.trailerPlateNumber = '';
      return;
    }
    const item = socialCapacities.value.find((x) => x.id === id);
    if (item) {
      form.carrier.mainDriverName = item.driverName || '';
      form.carrier.mainDriverPhone = item.driverPhone || '';
      form.carrier.plateNumber = item.plateNumber || '';
    }
    try {
      const detail = await getSocialCapacity(id);
      if (!detail) return;
      if (detail.driver?.idCard) {
        form.carrier.mainDriverIdCard = detail.driver.idCard;
      }
      if (detail.vehicle?.trailerPlate) {
        form.carrier.trailerPlateNumber = detail.vehicle.trailerPlate;
      }
    } catch {
      // ignore
    }
  };

  const validate = (): string | null => {
    const c = form.carrier;
    if (c.carrierType === CARRIER_TYPE.SELF) {
      if (!c.capacityId && !c.mainDriverName?.trim()) {
        return '请选择运力或手动填写主驾姓名+车牌';
      }
      if (!c.plateNumber?.trim()) return '请填写车牌号';
    } else if (c.carrierType === CARRIER_TYPE.CARRIER) {
      // 承运商类型：调度员是否代填
      const hasProxyData =
        c.mainDriverName?.trim() &&
        c.mainDriverPhone?.trim() &&
        c.plateNumber?.trim();
      if (hasProxyData) {
        form.isProxy = true;
      } else if (proxyPanelOpen.value.includes('proxy')) {
        return '请填写完整的主驾/电话/车牌或关闭代填面板';
      }
      // 不填运力则提交后等待 lite 上报，无需校验
    } else if (c.carrierType === CARRIER_TYPE.SOCIAL) {
      if (!c.socialDriverId) {
        return '请选择社会运力';
      }
      if (!c.mainDriverName?.trim()) return '请填写司机姓名';
      if (!c.mainDriverPhone?.trim()) return '请填写司机电话';
      if (!c.plateNumber?.trim()) return '请填写车牌号';
    }
    return null;
  };

  const submit = async () => {
    if (!props.task?.id) {
      emit('update:visible', false);
      return;
    }
    const err = validate();
    if (err) {
      EleMessage.error({ message: err, plain: true });
      return;
    }

    // 承运商类型未代填运力时：仅提示等待 lite 上报，不发请求
    if (
      form.carrier.carrierType === CARRIER_TYPE.CARRIER &&
      !form.isProxy &&
      !form.carrier.mainDriverName?.trim()
    ) {
      EleMessage.info({
        message: '已通知承运商上报运力，请耐心等待。',
        plain: true
      });
      emit('update:visible', false);
      return;
    }

    submitting.value = true;
    try {
      await assignCarrier(props.task.id, {
        carrier: form.carrier,
        isProxy: form.isProxy
      });
      EleMessage.success({
        message: isReassign.value ? '换车成功' : '派车成功',
        plain: true
      });
      emit('done');
      emit('update:visible', false);
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '派车失败';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>
