<!-- 承运商 Tab 编辑弹窗：基础信息 / 结算账户 / 备注（与运力-车辆编辑弹窗交互一致） -->
<template>
  <el-dialog
    :title="isEdit ? '编辑承运商' : '新增承运商'"
    :model-value="visible"
    width="860px"
    draggable
    class="carrier-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="carrier-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="carrier-edit-tabs">
        <el-tab-pane label="基础信息" name="base">
          <div class="carrier-tab-pane">
            <el-row :gutter="16">
              <!-- 类型优先，与全称、简称同一行 -->
              <el-col :span="8">
                <el-form-item prop="carrierType">
                  <floating-label
                    v-model="form.carrierType"
                    label="请选择承运商类型"
                    type="select"
                    :clearable="false"
                  >
                    <el-option label="公司车队" :value="0" />
                    <el-option label="个体司机/小车队" :value="1" />
                    <el-option label="其他" :value="2" />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item prop="carrierName">
                  <floating-label
                    label="请输入承运商全称"
                    type="input"
                    v-model.trim="form.carrierName"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
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
                <el-form-item prop="contactPerson">
                  <floating-label
                    label="请输入联系人姓名"
                    type="input"
                    v-model.trim="form.contactPerson"
                    clearable
                  />
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
                    label="联系邮箱"
                    type="input"
                    v-model.trim="form.contactEmail"
                    clearable
                  />
                </el-form-item>
              </el-col>

              <!-- 公司：统一社会信用代码必填，法人选填 -->
              <template v-if="isCompanyCarrier">
                <el-col :span="12">
                  <el-form-item prop="creditCode">
                    <floating-label
                      label="请输入统一社会信用代码（必填）"
                      type="input"
                      v-model.trim="form.creditCode"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item>
                    <floating-label
                      label="法人代表/负责人（选填）"
                      type="input"
                      v-model.trim="form.legalPerson"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </template>
              <!-- 个体/其他：身份证号必填 -->
              <el-col v-else :span="24">
                <el-form-item prop="idCardNo">
                  <floating-label
                    label="请输入身份证号（必填）"
                    type="input"
                    v-model.trim="form.idCardNo"
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
                  <floating-label
                    label="合作起始日"
                    type="date"
                    date-type="date"
                    v-model="form.cooperationStartDate"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="结算账户" name="settlements">
          <div class="carrier-tab-pane">
            <carrier-settlement-table
              :carrier-id="form.id ?? null"
              v-model="settlements"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="备注" name="remark">
          <div class="carrier-tab-pane">
            <el-form-item>
              <floating-label
                label="请输入备注（仅本租户可见）"
                type="input"
                input-type="textarea"
                v-model.trim="form.remark"
                clearable
              />
            </el-form-item>
          </div>
        </el-tab-pane>
      </el-tabs>
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
  /** 公司车队 */
  const isCompanyCarrier = computed(() => form.carrierType === 0);
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

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  /** 统一社会信用代码 18 位（数字与大写字母，不含 I/O/Z/S/V） */
  const USCC_PATTERN =
    /^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$/i;

  /** 大陆 18 位身份证号 */
  const ID_CARD_18_PATTERN =
    /^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;

  /** 大陆 15 位一代身份证 */
  const ID_CARD_15_PATTERN =
    /^[1-9]\d{7}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}$/;

  const validateIdCardNo = (
    _rule: unknown,
    value: string | undefined,
    callback: (e?: Error) => void
  ) => {
    const v = value?.trim() ?? '';
    if (!v) {
      callback(new Error('请输入身份证号'));
      return;
    }
    if (ID_CARD_18_PATTERN.test(v) || ID_CARD_15_PATTERN.test(v)) {
      callback();
      return;
    }
    callback(new Error('请输入正确的 15 或 18 位身份证号'));
  };

  const rules = computed<FormRules>(() => {
    const r: FormRules = {
      carrierName: [
        { required: true, message: '请输入承运商全称', trigger: 'blur' }
      ],
      carrierType: [
        { required: true, message: '请选择承运商类型', trigger: 'change' }
      ],
      contactPerson: [
        { required: true, message: '请输入联系人姓名', trigger: 'blur' }
      ],
      contactPhone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' },
        {
          pattern: /^1[3-9]\d{9}$/,
          message: '请输入正确的手机号',
          trigger: 'blur'
        }
      ]
    };
    if (form.carrierType === 0) {
      r.creditCode = [
        {
          required: true,
          message: '请输入统一社会信用代码',
          trigger: 'blur'
        },
        {
          pattern: USCC_PATTERN,
          message: '请输入正确的 18 位统一社会信用代码',
          trigger: 'blur'
        }
      ];
    } else {
      r.idCardNo = [
        { required: true, message: '请输入身份证号', trigger: 'blur' },
        { validator: validateIdCardNo, trigger: 'blur' }
      ];
    }
    return r;
  });

  watch(
    () => form.carrierType,
    () => {
      void nextTick(() => {
        formRef.value?.clearValidate([
          'creditCode',
          'idCardNo',
          'legalPerson'
        ]);
      });
    }
  );

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

  watch(
    () => props.visible,
    async (val) => {
      if (!val) {
        void nextTick(() => {
          formRef.value?.clearValidate();
        });
        return;
      }
      activeTab.value = 'base';
      reset();
      if (props.data?.id) {
        const detail = await getCarrier(props.data.id);
        if (detail) {
          Object.assign(form, detail);
          settlements.value = detail.settlements ?? [];
        }
      }
      void nextTick(() => {
        formRef.value?.clearValidate();
      });
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const buildPayload = (): Carrier => {
    const payload: Carrier = { ...form };
    if (payload.carrierType === 0) {
      delete payload.idCardNo;
    } else {
      delete payload.creditCode;
    }
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
        EleMessage.success({ message: '操作成功', plain: true });
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
  .carrier-edit-form {
    margin: 0;
  }

  .carrier-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .carrier-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .carrier-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .carrier-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .carrier-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .carrier-edit-tabs :deep(.el-tabs__item) {
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

  .carrier-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .carrier-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .carrier-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .carrier-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .carrier-tab-pane {
    max-height: min(420px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .carrier-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .carrier-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .carrier-edit-dialog :deep(.carrier-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .carrier-edit-dialog :deep(.carrier-tab-pane > .el-form-item) {
    margin-bottom: 14px;
  }

  .form-tip {
    font-size: 12px;
    color: var(--el-color-warning);
    margin-top: 4px;
  }
</style>
