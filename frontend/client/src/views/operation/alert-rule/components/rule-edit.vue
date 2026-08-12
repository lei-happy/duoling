<!--
  覆盖规则编辑

  三段式：先选「管哪一种预警」，再划「管哪批任务」，最后填「阈值放宽还是收紧」。
  保存前会做一次冲突预检：如果已有一条适用范围和优先级完全相同的规则，
  两条会互相盖来盖去，先提示再让用户决定要不要继续。
-->
<template>
  <el-dialog
    :title="isEdit ? '编辑覆盖规则' : '新增覆盖规则'"
    :model-value="visible"
    width="760px"
    draggable
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    class="rule-edit-dialog"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="110px"
      class="rule-edit"
      @submit.prevent=""
    >
      <section class="rule-edit__section">
        <h4 class="rule-edit__section-title">管哪一种预警</h4>
        <el-form-item label="预警类型" prop="ruleCode">
          <el-select
            v-model="form.ruleCode"
            placeholder="请选择预警类型"
            style="width: 100%"
            @change="onRuleCodeChange"
          >
            <el-option
              v-for="item in catalog"
              :key="item.ruleCode"
              :value="item.ruleCode"
              :label="item.ruleName"
            >
              <span>{{ item.ruleName }}</span>
              <span class="ele-text-secondary" style="margin-left: 8px">
                {{ item.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="currentDef?.stageScoped"
          label="限定阶段"
          prop="stage"
        >
          <el-select
            v-model="form.stage"
            placeholder="请选择阶段"
            style="width: 100%"
          >
            <el-option
              v-for="s in currentDef?.stages ?? []"
              :key="s"
              :value="s"
              :label="alertStageLabel(s)"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="规则名称">
          <el-input
            v-model.trim="form.ruleName"
            maxlength="100"
            placeholder="给这条规则起个好认的名字，例如「上汽大众更严」"
          />
        </el-form-item>
      </section>

      <section class="rule-edit__section">
        <h4 class="rule-edit__section-title">管哪批任务</h4>
        <p class="rule-edit__section-hint">
          至少填一项。多项同时填表示都要满足；命中多条时，范围越具体的那条生效。
        </p>
        <div
          class="rule-edit__scope-preview"
          :class="{ 'is-empty': !liveScopeSummary }"
        >
          {{ liveScopeSummary || '还没限定范围，请至少选一项' }}
        </div>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="指定客户">
              <el-select
                v-model="form.customerId"
                filterable
                clearable
                placeholder="不限"
                style="width: 100%"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :value="c.id"
                  :label="c.customerName"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户类型">
              <el-select
                v-model="form.customerType"
                clearable
                placeholder="不限"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in CUSTOMER_TYPE_OPTIONS"
                  :key="opt.value"
                  :value="opt.value"
                  :label="opt.label"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出发地">
              <el-cascader
                v-model="originCodes"
                :options="regionTree"
                :props="regionCascaderProps"
                filterable
                clearable
                placeholder="不限"
                style="width: 100%"
                @change="onOriginChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目的地">
              <el-cascader
                v-model="destCodes"
                :options="regionTree"
                :props="regionCascaderProps"
                filterable
                clearable
                placeholder="不限"
                style="width: 100%"
                @change="onDestChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="里程范围">
              <div class="rule-edit__range">
                <el-input-number
                  v-model="form.distanceMin"
                  :min="0"
                  :step="100"
                  controls-position="right"
                  placeholder="不限"
                />
                <span class="rule-edit__range-sep">至</span>
                <el-input-number
                  v-model="form.distanceMax"
                  :min="0"
                  :step="100"
                  controls-position="right"
                  placeholder="不限"
                />
                <span class="ele-text-secondary">公里</span>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="承运方式">
              <el-select
                v-model="form.carrierType"
                clearable
                placeholder="不限"
                style="width: 100%"
              >
                <el-option
                  v-for="opt in CARRIER_TYPE_OPTIONS"
                  :key="opt.value"
                  :value="opt.value"
                  :label="opt.label"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品车品牌">
              <el-select
                v-model="form.brandId"
                filterable
                clearable
                placeholder="不限"
                style="width: 100%"
                @change="onBrandChange"
              >
                <el-option
                  v-for="b in brands"
                  :key="b.brandId"
                  :value="b.brandId"
                  :label="b.brandNameCn"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品车车系">
              <el-select
                v-model="form.seriesId"
                filterable
                clearable
                :disabled="!form.brandId"
                :placeholder="form.brandId ? '不限' : '请先选品牌'"
                style="width: 100%"
              >
                <el-option
                  v-for="s in seriesList"
                  :key="s.seriesId"
                  :value="s.seriesId"
                  :label="s.seriesName"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </section>

      <section class="rule-edit__section">
        <h4 class="rule-edit__section-title">阈值怎么定</h4>
        <template v-if="currentDef?.supportsTimeBasis">
          <div class="rule-edit__clocks">
            <section
              class="rule-edit__clock"
              :class="{ 'is-off': !form.planEnabled }"
            >
              <el-checkbox
                :model-value="!!form.planEnabled"
                @change="(v: boolean) => setClock('plan', v)"
              >
                内部计划时间
              </el-checkbox>
              <threshold-track
                v-if="form.planEnabled"
                :kind="currentDef.kind"
                v-model:warn-ahead-minutes="form.warnAheadMinutes"
                v-model:critical-after-minutes="form.criticalAfterMinutes"
                time-basis-label="内部计划时间"
              />
            </section>
            <section
              class="rule-edit__clock"
              :class="{ 'is-off': !form.requiredEnabled }"
            >
              <el-checkbox
                :model-value="!!form.requiredEnabled"
                @change="(v: boolean) => setClock('required', v)"
              >
                客户要求时间
              </el-checkbox>
              <threshold-track
                v-if="form.requiredEnabled"
                :kind="currentDef.kind"
                v-model:warn-ahead-minutes="form.warnAheadRequiredMinutes"
                v-model:critical-after-minutes="
                  form.criticalAfterRequiredMinutes
                "
                time-basis-label="客户要求时间"
              />
            </section>
          </div>
          <p class="rule-edit__hint">
            两路都开时，谁先碰到阈值听谁的。任务没填的那路会自动跳过。
          </p>
        </template>
        <threshold-track
          v-else-if="currentDef && currentDef.kind !== 'execution'"
          :kind="currentDef.kind"
          v-model:warn-ahead-minutes="form.warnAheadMinutes"
          v-model:critical-after-minutes="form.criticalAfterMinutes"
          v-model:anchor-offset-minutes="form.anchorOffsetMinutes"
          v-model:stagnant-hours="form.stagnantHours"
        />
        <p v-else-if="currentDef?.kind === 'execution'" class="rule-edit__hint">
          这类预警一旦发现就提醒，没有时间阈值；这里只用来限定适用范围和是否启用。
        </p>
      </section>

      <section class="rule-edit__section">
        <h4 class="rule-edit__section-title">生效控制</h4>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-input-number
                v-model="form.priority"
                :min="0"
                :step="1"
                controls-position="right"
              />
              <el-tooltip
                content="范围一样具体时，数字大的先生效；一般保持 0 即可"
                placement="top"
              >
                <el-icon class="rule-edit__help"><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch v-model="enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生效日期">
              <el-date-picker
                v-model="form.effectiveDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="立即生效"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="失效日期">
              <el-date-picker
                v-model="form.expiryDate"
                type="date"
                value-format="YYYY-MM-DD"
                placeholder="长期有效"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model.trim="form.remark"
                type="textarea"
                :rows="2"
                maxlength="255"
                placeholder="写清为什么要给这批任务单独设阈值，方便后续复盘"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </section>
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import type { CascaderProps, FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { QuestionFilled } from '@element-plus/icons-vue';
  import {
    addTaskAlertRule,
    checkTaskAlertRuleConflict,
    updateTaskAlertRule
  } from '@/api/operation/task-alert';
  import type {
    TaskAlertRule,
    TaskAlertRuleCatalogItem
  } from '@/api/operation/task-alert/model';
  import { selectCustomers } from '@/api/partner/customer';
  import type { CustomerSelectItem } from '@/api/partner/customer/model';
  import { listVehicleBrandOptions } from '@/api/basic-data/vehicle-brand';
  import type { VehicleBrandOption } from '@/api/basic-data/vehicle-brand/model';
  import { pageVehicleSeries } from '@/api/basic-data/vehicle-series';
  import type { VehicleSeries } from '@/api/basic-data/vehicle-series/model';
  import { getRegionNavTree } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';
  import { CARRIER_TYPE_OPTIONS } from '../../task/status-config';
  import { alertStageLabel, deriveTimeBasis } from '../../task/alert-config';
  import ThresholdTrack from './threshold-track.vue';

  const props = defineProps<{
    visible: boolean;
    data: TaskAlertRule | null;
    catalog: TaskAlertRuleCatalogItem[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const CUSTOMER_TYPE_OPTIONS = [
    { value: 0, label: '主机厂' },
    { value: 1, label: '贸易商' },
    { value: 2, label: '经销商' },
    { value: 3, label: '个人' },
    { value: 4, label: '其他' }
  ];

  const formRef = ref<FormInstance>();
  const saving = ref(false);
  const enabled = ref(true);
  const customers = ref<CustomerSelectItem[]>([]);
  const brands = ref<VehicleBrandOption[]>([]);
  const seriesList = ref<VehicleSeries[]>([]);
  const regionTree = ref<RegionNavNode[]>([]);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  const emptyForm = (): TaskAlertRule => ({
    ruleCode: '',
    ruleName: undefined,
    stage: null,
    customerId: null,
    customerType: null,
    originRegionId: null,
    destinationRegionId: null,
    distanceMin: undefined,
    distanceMax: undefined,
    brandId: null,
    seriesId: null,
    carrierType: null,
    timeBasis: 2,
    planEnabled: true,
    requiredEnabled: true,
    anchorOffsetMinutes: undefined,
    warnAheadMinutes: undefined,
    criticalAfterMinutes: undefined,
    warnAheadRequiredMinutes: undefined,
    criticalAfterRequiredMinutes: undefined,
    stagnantHours: undefined,
    priority: 0,
    status: 1,
    effectiveDate: null,
    expiryDate: null,
    remark: null
  });

  const form = reactive<TaskAlertRule>(emptyForm());

  const isEdit = computed(() => !!props.data?.id);

  const currentDef = computed(() =>
    props.catalog.find((c) => c.ruleCode === form.ruleCode)
  );

  const setClock = (which: 'plan' | 'required', on: boolean) => {
    if (!on) {
      const other = which === 'plan' ? form.requiredEnabled : form.planEnabled;
      if (!other) return;
    }
    if (which === 'plan') form.planEnabled = on;
    else form.requiredEnabled = on;
  };

  const regionNameOf = (codes: string[]): string => {
    if (!codes.length) return '';
    let nodes: RegionNavNode[] = regionTree.value;
    let name = '';
    for (const code of codes) {
      const hit = nodes.find((n) => n.code === code);
      if (!hit) break;
      name = hit.name;
      nodes = hit.children ?? [];
    }
    return name;
  };

  const liveScopeSummary = computed(() => {
    const parts: string[] = [];
    if (form.customerId) {
      const c = customers.value.find((x) => x.id === form.customerId);
      parts.push(c?.customerName || '指定客户');
    }
    if (form.customerType != null) {
      const t = CUSTOMER_TYPE_OPTIONS.find(
        (o) => o.value === form.customerType
      );
      if (t) parts.push(t.label);
    }
    const origin = regionNameOf(originCodes.value);
    const dest = regionNameOf(destCodes.value);
    if (origin || dest) {
      parts.push(`${origin || '不限出发地'} → ${dest || '不限目的地'}`);
    }
    if (form.distanceMin != null || form.distanceMax != null) {
      if (form.distanceMin != null && form.distanceMax != null) {
        parts.push(`${form.distanceMin}–${form.distanceMax} 公里`);
      } else if (form.distanceMin != null) {
        parts.push(`${form.distanceMin} 公里以上`);
      } else {
        parts.push(`${form.distanceMax} 公里以内`);
      }
    }
    if (form.carrierType != null) {
      const t = CARRIER_TYPE_OPTIONS.find((o) => o.value === form.carrierType);
      if (t) parts.push(t.label);
    }
    if (form.brandId) {
      const b = brands.value.find((x) => x.brandId === form.brandId);
      parts.push(b?.brandNameCn || '指定品牌');
    }
    if (form.seriesId) {
      const s = seriesList.value.find((x) => x.seriesId === form.seriesId);
      if (s) parts.push(s.seriesName);
    }
    return parts.join(' · ');
  });

  const rules: FormRules = {
    ruleCode: [
      { required: true, message: '请选择预警类型', trigger: 'change' }
    ],
    stage: [{ required: true, message: '请选择阶段', trigger: 'change' }]
  };

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const hasScope = () =>
    [
      form.customerId,
      form.customerType,
      form.originRegionId,
      form.destinationRegionId,
      form.distanceMin,
      form.distanceMax,
      form.brandId,
      form.seriesId,
      form.carrierType
    ].some((v) => v !== null && v !== undefined);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const onRuleCodeChange = () => {
    const def = currentDef.value;
    if (!def) return;
    // 换了预警类型，原来的阈值大概率不再适用，直接回落到该类型的系统默认值
    form.stage = def.stageScoped ? (def.stages[0] ?? null) : null;
    form.timeBasis = def.defaults.timeBasis;
    form.planEnabled = def.defaults.planEnabled ?? true;
    form.requiredEnabled = def.defaults.requiredEnabled ?? true;
    form.anchorOffsetMinutes = def.defaults.anchorOffsetMinutes ?? undefined;
    form.warnAheadMinutes = def.defaults.warnAheadMinutes ?? 0;
    form.criticalAfterMinutes = def.defaults.criticalAfterMinutes ?? 0;
    form.warnAheadRequiredMinutes =
      def.defaults.warnAheadRequiredMinutes ??
      def.defaults.warnAheadMinutes ??
      0;
    form.criticalAfterRequiredMinutes =
      def.defaults.criticalAfterRequiredMinutes ??
      def.defaults.criticalAfterMinutes ??
      0;
    form.stagnantHours =
      form.stage != null
        ? (def.defaults.stagnantHours?.[String(form.stage)] ?? undefined)
        : undefined;
  };

  const loadSeries = async (brandId?: number | null) => {
    if (!brandId) {
      seriesList.value = [];
      return;
    }
    try {
      const res = await pageVehicleSeries({ brandId, page: 1, limit: 200 });
      seriesList.value = res?.list ?? [];
    } catch {
      seriesList.value = [];
    }
  };

  const onBrandChange = () => {
    form.seriesId = null;
    loadSeries(form.brandId);
  };

  const regionIdOf = (codes: string[]): number | null =>
    findLeafRegionByCodePath(regionTree.value, codes)?.regionId ?? null;

  const onOriginChange = (val: string[] | undefined) => {
    form.originRegionId = val?.length ? regionIdOf(val) : null;
  };

  const onDestChange = (val: string[] | undefined) => {
    form.destinationRegionId = val?.length ? regionIdOf(val) : null;
  };

  const loadOptions = async () => {
    if (customers.value.length === 0) {
      selectCustomers()
        .then((res) => (customers.value = res ?? []))
        .catch(() => (customers.value = []));
    }
    if (brands.value.length === 0) {
      listVehicleBrandOptions({ limit: 500 })
        .then((res) => (brands.value = res ?? []))
        .catch(() => (brands.value = []));
    }
    if (regionTree.value.length === 0) {
      getRegionNavTree()
        .then((res) => (regionTree.value = res ?? []))
        .catch(() => (regionTree.value = []));
    }
  };

  /** 回显行政区级联：树是异步来的，拿到后再按 regionId 找 code 路径 */
  const hydrateRegionCodes = () => {
    const findCodes = (regionId?: number | null): string[] => {
      if (!regionId) return [];
      const walk = (nodes: RegionNavNode[]): RegionNavNode | null => {
        for (const n of nodes) {
          if (n.regionId === regionId) return n;
          const hit = walk(n.children ?? []);
          if (hit) return hit;
        }
        return null;
      };
      const node = walk(regionTree.value);
      return node
        ? (findRegionCodePath(regionTree.value, node.code) ?? [])
        : [];
    };
    originCodes.value = findCodes(form.originRegionId);
    destCodes.value = findCodes(form.destinationRegionId);
  };

  watch(
    () => regionTree.value.length,
    () => hydrateRegionCodes()
  );

  watch(
    () => props.visible,
    (v) => {
      if (!v) return;
      Object.assign(form, emptyForm(), props.data ?? {});
      enabled.value = (props.data?.status ?? 1) === 1;
      originCodes.value = [];
      destCodes.value = [];
      loadOptions();
      loadSeries(form.brandId);
      hydrateRegionCodes();
      formRef.value?.clearValidate?.();
    }
  );

  const buildPayload = (): TaskAlertRule => ({
    ...form,
    timeBasis: deriveTimeBasis(!!form.planEnabled, !!form.requiredEnabled),
    planEnabled: !!form.planEnabled,
    requiredEnabled: !!form.requiredEnabled,
    status: enabled.value ? 1 : 0,
    // 表单上的「不限」是空值，别把 undefined 当成 0 传下去
    distanceMin: form.distanceMin ?? null,
    distanceMax: form.distanceMax ?? null
  });

  const submit = async () => {
    try {
      await formRef.value?.validate();
    } catch {
      return;
    }
    if (
      currentDef.value?.supportsTimeBasis &&
      !form.planEnabled &&
      !form.requiredEnabled
    ) {
      EleMessage.warning({
        message: '内部计划和客户要求至少要开一路，否则这条预警不会生效',
        plain: true
      });
      return;
    }
    if (!hasScope()) {
      EleMessage.warning({
        message: '请至少限定一个适用范围，否则它就等同于默认阈值了',
        plain: true
      });
      return;
    }
    if (
      form.distanceMin != null &&
      form.distanceMax != null &&
      form.distanceMin >= form.distanceMax
    ) {
      EleMessage.warning({
        message: '里程下限要小于上限，请检查后重新填写',
        plain: true
      });
      return;
    }

    const payload = buildPayload();
    try {
      const conflict = await checkTaskAlertRuleConflict(
        payload,
        props.data?.id
      );
      if (conflict?.hasConflict) {
        await ElMessageBox.confirm(
          conflict.message ||
            '已有一条适用范围和优先级完全相同的规则，两条会互相覆盖。',
          '发现重复的规则',
          {
            type: 'warning',
            confirmButtonText: '仍然保存',
            cancelButtonText: '返回修改'
          }
        );
      }
    } catch (e: unknown) {
      // 用户在冲突提示里点了「返回修改」时不算错误，直接停在表单上
      if (e === 'cancel' || e === 'close') return;
    }

    saving.value = true;
    try {
      if (props.data?.id) {
        await updateTaskAlertRule(props.data.id, payload);
      } else {
        await addTaskAlertRule(payload);
      }
      EleMessage.success({
        message: '已保存，下一轮预警计算即生效',
        plain: true
      });
      updateVisible(false);
      emit('done');
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message || '保存失败，请稍后重试';
      EleMessage.error({ message: msg, plain: true });
    } finally {
      saving.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .rule-edit {
    &__section {
      padding: 4px 0 16px;

      & + & {
        border-top: 1px solid var(--el-border-color-extra-light);
        padding-top: 16px;
      }
    }

    &__section-title {
      margin: 0 0 12px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.04em;
      color: var(--el-text-color-primary);
    }

    &__section-hint {
      margin: -4px 0 10px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__scope-preview {
      margin-bottom: 12px;
      padding: 8px 12px;
      border-radius: 8px;
      background: var(--el-color-primary-light-9);
      color: var(--el-text-color-primary);
      font-size: 13px;
      line-height: 1.5;

      &.is-empty {
        background: var(--el-fill-color-light);
        color: var(--el-text-color-secondary);
      }
    }

    &__range {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    &__range-sep {
      color: var(--el-text-color-secondary);
    }

    &__hint {
      margin-top: 4px;
      font-size: 12px;
      line-height: 1.5;
      color: var(--el-text-color-secondary);
    }

    &__clocks {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    &__clock {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 10px 12px 12px;
      border-radius: 10px;
      border: 1px solid var(--el-border-color-extra-light);

      &.is-off {
        background: var(--el-fill-color-lighter);
        border-color: transparent;
      }
    }

    &__help {
      margin-left: 6px;
      color: var(--el-text-color-placeholder);
      cursor: help;
    }
  }

  .rule-edit :deep(.el-input-number) {
    width: 130px;
  }
</style>
