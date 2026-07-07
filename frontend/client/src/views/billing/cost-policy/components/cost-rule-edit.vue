<template>
  <el-dialog
    :title="isEdit ? '编辑费用规则' : '新增费用规则'"
    :model-value="visible"
    width="720px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="96px"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="费用类型" prop="feeType">
            <el-select
              v-model="form.feeType"
              placeholder="请选择费用类型"
              filterable
              @change="onFeeTypeChange"
            >
              <el-option
                v-for="ft in meta.feeTypes"
                :key="ft.code"
                :label="ft.name + (ft.isRequired ? '（必算）' : '')"
                :value="ft.code"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="方向" prop="direction">
            <el-select v-model="form.direction">
              <el-option label="应付加项" :value="1" />
              <el-option label="扣减项" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="计价方式" prop="pricingMethod">
            <el-select v-model="form.pricingMethod">
              <el-option
                v-for="pm in meta.pricingMethods"
                :key="pm.value"
                :label="pm.label"
                :value="pm.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="收款方" prop="payeeType">
            <el-select v-model="form.payeeType">
              <el-option label="司机" :value="1" />
              <el-option label="承运商" :value="2" />
              <el-option label="社会运力" :value="3" />
            </el-select>
          </el-form-item>
        </el-col>

        <!-- 通用单价（tiered/percentage 除外仍可作为保底基准） -->
        <el-col :span="12" v-if="form.pricingMethod !== 'percentage'">
          <el-form-item label="单价" prop="unitPrice">
            <el-input-number
              v-model="form.unitPrice"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col
          :span="12"
          v-if="
            form.pricingMethod === 'per_km' ||
            form.pricingMethod === 'per_ton_km'
          "
        >
          <el-form-item label="核定里程">
            <el-input-number
              v-model="form.distanceKm"
              :min="0"
              :precision="2"
              controls-position="right"
              placeholder="空则取线路里程"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12" v-if="form.pricingMethod === 'per_km'">
          <el-form-item label="乘以台数">
            <el-switch
              v-model="form.multiplyByQty"
              :active-value="1"
              :inactive-value="0"
            />
          </el-form-item>
        </el-col>

        <!-- 按比例 -->
        <template v-if="form.pricingMethod === 'percentage'">
          <el-col :span="12">
            <el-form-item label="比例基数">
              <el-select v-model="form.percentBase">
                <el-option label="收入侧运费" value="freight_income" />
                <el-option label="固定基数" value="fixed_base" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="比例(%)">
              <el-input-number
                v-model="form.ratePercent"
                :min="0"
                :precision="4"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </template>

        <!-- 阶梯 -->
        <el-col :span="24" v-if="form.pricingMethod === 'tiered'">
          <el-form-item label="阶梯分段">
            <div class="tier-editor">
              <div
                v-for="(seg, idx) in form.tiersJson"
                :key="idx"
                class="tier-row"
              >
                <span>台数≤</span>
                <el-input-number
                  v-model="seg.upTo"
                  :min="0"
                  controls-position="right"
                  placeholder="空=最后一段"
                  style="width: 130px"
                />
                <span>单价</span>
                <el-input-number
                  v-model="seg.unitPrice"
                  :min="0"
                  :precision="2"
                  controls-position="right"
                  style="width: 130px"
                />
                <el-button link type="danger" @click="removeTier(idx)">
                  删除
                </el-button>
              </div>
              <el-button size="small" @click="addTier">+ 增加分段</el-button>
            </div>
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="保底金额">
            <el-input-number
              v-model="form.minAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="封顶金额">
            <el-input-number
              v-model="form.maxAmount"
              :min="0"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="取整方式">
            <el-select v-model="form.roundMode">
              <el-option label="不取整" :value="0" />
              <el-option label="四舍五入到元" :value="1" />
              <el-option label="进一法到元" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="价格类型">
            <el-select v-model="form.priceType">
              <el-option label="明确" :value="0" />
              <el-option label="预估" :value="1" />
            </el-select>
          </el-form-item>
        </el-col>

        <el-divider content-position="left">适用范围（可空=不限）</el-divider>
        <el-col :span="12">
          <el-form-item label="出发地">
            <el-input
              v-model.trim="form.origin"
              placeholder="出发地名称"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目的地">
            <el-input
              v-model.trim="form.destination"
              placeholder="目的地名称"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="出发地编码">
            <el-input v-model.trim="form.originCode" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="目的地编码">
            <el-input v-model.trim="form.destinationCode" clearable />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="双向">
            <el-switch
              v-model="form.isBidirectional"
              :active-value="1"
              :inactive-value="0"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="品牌ID">
            <el-input-number
              v-model="form.brandId"
              :min="1"
              controls-position="right"
              placeholder="不限"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="车系ID">
            <el-input-number
              v-model="form.seriesId"
              :min="1"
              controls-position="right"
              placeholder="不限"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="备注">
            <el-input v-model="form.remark" type="textarea" :rows="2" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addRule, updateRule } from '@/api/billing/cost-policy';
  import type {
    CostRule,
    CostMeta,
    TierSeg
  } from '@/api/billing/cost-policy/model';

  const props = defineProps<{
    visible: boolean;
    policyId: number;
    data: CostRule | null;
    meta: CostMeta;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);

  const defaultForm = (): CostRule => ({
    feeType: '',
    direction: 1,
    pricingMethod: 'per_vehicle',
    payeeType: 1,
    unitPrice: 0,
    multiplyByQty: 0,
    roundMode: 0,
    priceType: 0,
    isBidirectional: 0,
    tiersJson: []
  });

  const form = reactive<CostRule>(defaultForm());

  const rules = reactive<FormRules>({
    feeType: [{ required: true, message: '请选择费用类型', trigger: 'change' }],
    pricingMethod: [
      { required: true, message: '请选择计价方式', trigger: 'change' }
    ]
  });

  const onFeeTypeChange = (code: string) => {
    const ft = props.meta.feeTypes.find((f) => f.code === code);
    if (!ft) return;
    // 用户主动切换费用类型：按费用类型元数据预填收款方/计价方式/方向/名称
    form.payeeType = ft.payeeTypeDefault ?? form.payeeType;
    form.feeName = ft.name;
    if (ft.pricingMethodDefault) {
      form.pricingMethod = ft.pricingMethodDefault;
    }
    if (ft.directionDefault != null) {
      form.direction = ft.directionDefault;
    }
  };

  const addTier = () => {
    (form.tiersJson as TierSeg[]).push({ upTo: null, unitPrice: 0 });
  };
  const removeTier = (idx: number) => {
    (form.tiersJson as TierSeg[]).splice(idx, 1);
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      Object.assign(form, defaultForm());
      if (props.data?.id) {
        Object.assign(form, props.data);
        if (!Array.isArray(form.tiersJson)) form.tiersJson = [];
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      loading.value = true;
      try {
        const payload: CostRule = { ...form, policyId: props.policyId };
        if (payload.pricingMethod !== 'tiered') payload.tiersJson = null;
        if (isEdit.value) {
          await updateRule(props.data!.id!, payload);
        } else {
          await addRule(props.policyId, payload);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .tier-editor {
    width: 100%;
  }
  .tier-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }
</style>
