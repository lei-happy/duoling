<!-- 承运商 Tab 编辑弹窗：基础信息 / 结算账户 / 备注 -->
<template>
  <el-dialog
    :title="isEdit ? '编辑承运商' : '新增承运商'"
    :model-value="visible"
    width="860px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <el-tabs v-model="activeTab">
      <!-- 基础信息 -->
      <el-tab-pane label="基础信息" name="base">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          class="carrier-edit-form"
          @submit.prevent=""
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item prop="carrierName">
                <floating-label
                  label="请输入承运商全称"
                  type="input"
                  v-model.trim="form.carrierName"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="carrierType">
                <floating-label
                  v-model="form.carrierType"
                  label="请选择承运商类型"
                  type="select"
                  clearable
                >
                  <el-option label="公司车队" :value="0" />
                  <el-option label="个体司机/小车队" :value="1" />
                  <el-option label="其他" :value="2" />
                </floating-label>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item prop="contactPhone">
                <floating-label
                  label="请输入联系电话（互联激活关键字段）"
                  type="input"
                  v-model.trim="form.contactPhone"
                  clearable
                  :disabled="phoneLocked"
                />
                <div v-if="phoneLocked" class="form-tip">
                  已激活互联，电话不可修改
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="请输入主要联系人"
                  type="input"
                  v-model.trim="form.contactPerson"
                  clearable
                />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="请输入承运商编码（留空自动）"
                  type="input"
                  v-model.trim="form.carrierCode"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="请输入简称"
                  type="input"
                  v-model.trim="form.shortName"
                  clearable
                />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="统一社会信用代码（公司必填）"
                  type="input"
                  v-model.trim="form.creditCode"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="身份证号（个体场景）"
                  type="input"
                  v-model.trim="form.idCardNo"
                  clearable
                />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="法人代表/负责人"
                  type="input"
                  v-model.trim="form.legalPerson"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="联系邮箱"
                  type="input"
                  v-model.trim="form.contactEmail"
                  clearable
                />
              </el-form-item>
            </el-col>

            <el-col :span="24">
              <el-form-item>
                <floating-label
                  label="请输入详细地址"
                  type="input"
                  v-model.trim="form.address"
                  clearable
                />
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item>
                <floating-label
                  v-model="form.status"
                  label="状态"
                  type="select"
                  :clearable="false"
                >
                  <el-option label="正常" :value="1" />
                  <el-option label="停用" :value="0" />
                  <el-option label="黑名单" :value="2" />
                </floating-label>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <el-date-picker
                  v-model="form.cooperationStartDate"
                  type="date"
                  placeholder="合作起始日"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-tab-pane>

      <!-- 结算账户 -->
      <el-tab-pane label="结算账户" name="settlements">
        <carrier-settlement-table
          :carrier-id="form.id ?? null"
          v-model="settlements"
        />
      </el-tab-pane>

      <!-- 备注 -->
      <el-tab-pane label="备注" name="remark">
        <el-form label-width="0">
          <el-form-item>
            <el-input
              v-model="form.remark"
              type="textarea"
              :autosize="{ minRows: 6, maxRows: 12 }"
              placeholder="请输入备注（仅本租户可见）"
            />
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
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
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import {
    addCarrier,
    updateCarrier,
    getCarrier,
    listSettlements
  } from '@/api/partner/carrier';
  import type {
    Carrier,
    CarrierSettlement
  } from '@/api/partner/carrier/model';
  import CarrierSettlementTable from './carrier-settlement-table.vue';

  const props = defineProps<{
    visible: boolean;
    data: Carrier | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const phoneLocked = computed(
    () => isEdit.value && !!form.linkedTenantCode
  );
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const activeTab = ref('base');
  const form = reactive<Carrier>({
    carrierName: '',
    contactPhone: '',
    carrierType: 0,
    status: 1
  });
  const settlements = ref<CarrierSettlement[]>([]);

  const rules = reactive<FormRules>({
    carrierName: [
      { required: true, message: '请输入承运商全称', trigger: 'blur' }
    ],
    carrierType: [
      { required: true, message: '请选择承运商类型', trigger: 'change' }
    ],
    contactPhone: [
      { required: true, message: '请输入联系电话', trigger: 'blur' },
      {
        pattern: /^1[3-9]\d{9}$/,
        message: '请输入正确的手机号',
        trigger: 'blur'
      }
    ]
  });

  function reset() {
    Object.assign(form, {
      id: undefined,
      carrierCode: undefined,
      carrierName: '',
      shortName: undefined,
      carrierType: 0,
      creditCode: undefined,
      idCardNo: undefined,
      legalPerson: undefined,
      contactPerson: undefined,
      contactPhone: '',
      contactEmail: undefined,
      province: undefined,
      city: undefined,
      district: undefined,
      address: undefined,
      cooperationStartDate: undefined,
      status: 1,
      linkedTenantCode: null,
      inviteStatus: 0,
      remark: undefined
    });
    settlements.value = [];
    activeTab.value = 'base';
  }

  const onOpen = () => {
    nextTick(() => formRef.value?.clearValidate());
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      reset();
      if (props.data?.id) {
        const detail = await getCarrier(props.data.id);
        if (detail) {
          Object.assign(form, detail);
          settlements.value = detail.settlements ?? [];
        }
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const buildPayload = (): Carrier => {
    const payload: Carrier = { ...form };
    if (!payload.carrierCode?.trim()) {
      delete payload.carrierCode;
    }
    if (!isEdit.value) {
      // 新增时，把当前页面的草稿结算账户一次性带过去
      payload.settlements = settlements.value.map((s) => ({ ...s, id: undefined }));
    } else {
      delete payload.settlements;
    }
    return payload;
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) {
        activeTab.value = 'base';
        return;
      }
      loading.value = true;
      try {
        const payload = buildPayload();
        let saved: Carrier | undefined;
        if (isEdit.value) {
          saved = (await updateCarrier(payload)) ?? undefined;
        } else {
          saved = (await addCarrier(payload)) ?? undefined;
          if (saved?.id) {
            // 新增成功后，重新拉取 settlements 以便后续编辑可继续在子表中操作
            form.id = saved.id;
            const list = await listSettlements(saved.id);
            settlements.value = list ?? [];
          }
        }
        EleMessage.success({ message: '保存成功', plain: true });
        emit('done');
        updateVisible(false);
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .carrier-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
  .form-tip {
    font-size: 12px;
    color: var(--el-color-warning);
    margin-top: 4px;
  }
</style>
