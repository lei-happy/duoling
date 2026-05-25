<template>
  <el-dialog
    :title="isEdit ? '编辑社会运力' : '新增社会运力'"
    :model-value="visible"
    width="860px"
    draggable
    class="sc-edit-dialog"
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <div v-if="isEdit && form.socialCode" class="sc-edit-badges">
      <span>编号：<strong>{{ form.socialCode }}</strong></span>
      <el-tag size="small" :type="approvalTagType(form.approvalStatus)">
        {{ approvalLabel(form.approvalStatus) }}
      </el-tag>
      <el-tag
        v-if="form.approvalStatus === 2"
        size="small"
        :type="statusTagType(form.status)"
      >
        {{ statusLabel(form.status) }}
      </el-tag>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      :disabled="isApproving"
      label-width="0"
      class="sc-edit-form"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="sc-edit-tabs">
        <!-- ==== 基础信息 ==== -->
        <el-tab-pane label="基础信息" name="basic">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item>
                <dict-select-hint-wrap dict-name="社会运力来源">
                  <floating-label
                    v-model="form.source"
                    label="请选择来源"
                    type="select"
                    clearable
                  >
                    <el-option
                      v-for="item in sourceDict"
                      :key="item.dictDataCode"
                      :label="item.dictDataName"
                      :value="item.dictDataCode"
                    />
                  </floating-label>
                </dict-select-hint-wrap>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="来源备注（引荐人 / 渠道）"
                  type="input"
                  v-model.trim="form.sourceRemark"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item>
                <floating-label
                  label="备注"
                  type="input"
                  input-type="textarea"
                  v-model.trim="form.remark"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- ==== 车辆信息 ==== -->
        <el-tab-pane label="车辆信息" name="vehicle">
          <el-row :gutter="12">
            <el-col :span="8">
              <el-form-item prop="vehicle.plateNumber">
                <floating-label
                  label="车牌号"
                  type="input"
                  v-model.trim="form.vehicle.plateNumber"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  v-model="form.vehicle.plateCategory"
                  label="车牌类型"
                  type="select"
                >
                  <el-option label="蓝牌" value="BLUE" />
                  <el-option label="黄牌" value="YELLOW" />
                  <el-option label="新能源" value="NEW_ENERGY" />
                </floating-label>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <dict-select-hint-wrap dict-name="车辆类型">
                  <floating-label
                    v-model="form.vehicle.vehicleType"
                    label="车辆类型"
                    type="select"
                    clearable
                  >
                    <el-option
                      v-for="item in vehicleTypeDict"
                      :key="item.dictDataCode"
                      :label="item.dictDataName"
                      :value="item.dictDataCode"
                    />
                  </floating-label>
                </dict-select-hint-wrap>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  label="品牌"
                  type="input"
                  v-model.trim="form.vehicle.brand"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  label="型号"
                  type="input"
                  v-model.trim="form.vehicle.model"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  label="颜色"
                  type="input"
                  v-model.trim="form.vehicle.color"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="车架号 VIN"
                  type="input"
                  v-model.trim="form.vehicle.vin"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="发动机号"
                  type="input"
                  v-model.trim="form.vehicle.engineNo"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <floating-label
                  label="核定载重(吨)"
                  type="input"
                  v-model.number="form.vehicle.loadCapacity"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <floating-label
                  label="核定容积(m³)"
                  type="input"
                  v-model.number="form.vehicle.volumeCapacity"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <floating-label
                  label="车长(m)"
                  type="input"
                  v-model.number="form.vehicle.length"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <floating-label
                  label="轴数"
                  type="input"
                  v-model.number="form.vehicle.axleCount"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="注册日期"
                  v-model="form.vehicle.registrationDate"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="年检到期"
                  v-model="form.vehicle.inspectionExpire"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="保险到期"
                  v-model="form.vehicle.insuranceExpire"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="道路运输证号"
                  type="input"
                  v-model.trim="form.vehicle.transportLicenseNo"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="道路运输证有效期"
                  v-model="form.vehicle.transportLicenseExpire"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item>
                <el-checkbox v-model="hasTrailerBool">含挂车</el-checkbox>
              </el-form-item>
            </el-col>
            <template v-if="hasTrailerBool">
              <el-col :span="8">
                <el-form-item>
                  <floating-label
                    label="挂车车牌号"
                    type="input"
                    v-model.trim="form.vehicle.trailerPlate"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <dict-select-hint-wrap dict-name="挂车类型">
                    <floating-label
                      v-model="form.vehicle.trailerType"
                      label="挂车类型"
                      type="select"
                      clearable
                    >
                      <el-option
                        v-for="item in trailerTypeDict"
                        :key="item.dictDataCode"
                        :label="item.dictDataName"
                        :value="item.dictDataCode"
                      />
                    </floating-label>
                  </dict-select-hint-wrap>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <floating-label
                    label="挂车载重(吨)"
                    type="input"
                    v-model.number="form.vehicle.trailerLoadCapacity"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </template>
          </el-row>
        </el-tab-pane>

        <!-- ==== 司机信息 ==== -->
        <el-tab-pane label="司机信息" name="driver">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item prop="driver.name">
                <floating-label
                  label="姓名"
                  type="input"
                  v-model.trim="form.driver.name"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="driver.phone">
                <floating-label
                  label="手机号"
                  type="input"
                  v-model.trim="form.driver.phone"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  v-model="form.driver.gender"
                  label="性别"
                  type="select"
                  clearable
                >
                  <el-option label="男" :value="1" />
                  <el-option label="女" :value="2" />
                </floating-label>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="身份证号"
                  type="input"
                  v-model.trim="form.driver.idCard"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item>
                <floating-label
                  v-model="form.driver.licenseType"
                  label="驾驶证类型"
                  type="select"
                  clearable
                >
                  <el-option label="A1" value="A1" />
                  <el-option label="A2" value="A2" />
                  <el-option label="B1" value="B1" />
                  <el-option label="B2" value="B2" />
                  <el-option label="C1" value="C1" />
                </floating-label>
              </el-form-item>
            </el-col>
            <el-col :span="9">
              <el-form-item>
                <floating-label
                  label="驾驶证号"
                  type="input"
                  v-model.trim="form.driver.licenseNo"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="9">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="驾驶证有效期"
                  v-model="form.driver.licenseExpire"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="从业资格证号"
                  type="input"
                  v-model.trim="form.driver.qualificationNo"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  type="date"
                  date-type="date"
                  label="从业资格证有效期"
                  v-model="form.driver.qualificationExpire"
                  value-format="YYYY-MM-DD"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="紧急联系人"
                  type="input"
                  v-model.trim="form.driver.emergencyContact"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item>
                <floating-label
                  label="紧急联系电话"
                  type="input"
                  v-model.trim="form.driver.emergencyPhone"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item>
                <floating-label
                  label="居住地址"
                  type="input"
                  v-model.trim="form.driver.homeAddress"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- ==== 结算账户 ==== -->
        <el-tab-pane
          label="结算账户"
          name="account"
          :disabled="!isEdit"
        >
          <social-capacity-account
            v-if="isEdit && form.id"
            :social-capacity-id="form.id"
            :read-only="false"
          />
          <el-empty
            v-else
            description="请先保存基础 / 车辆 / 司机信息后再维护结算账户"
            :image-size="80"
          />
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">关闭</el-button>
      <el-button
        v-if="canSubmit"
        :loading="submitting"
        type="warning"
        @click="submitForApproval"
      >
        提交审核
      </el-button>
      <el-button
        v-if="canWithdraw"
        :loading="submitting"
        type="info"
        @click="withdraw"
      >
        撤回审核
      </el-button>
      <el-button
        v-if="canSave"
        :loading="saving"
        type="primary"
        @click="save"
      >
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, computed, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import DictSelectHintWrap from '@/components/DictSelectHintWrap/index.vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useDictData } from '@/utils/use-dict-data';
  import {
    DICT_CODE_VEHICLE_TYPE,
    DICT_CODE_TRAILER_TYPE,
    DICT_CODE_SOCIAL_CAPACITY_SOURCE
  } from '@/constants/dict-codes';
  import {
    addSocialCapacity,
    updateSocialCapacity,
    submitSocialCapacity,
    withdrawSocialCapacity,
    getSocialCapacity
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityDetail,
    SocialCapacityForm,
    SocialCapacityVehicleInfo,
    SocialCapacityDriverInfo
  } from '@/api/capacity/social-capacity/list/model';
  import SocialCapacityAccount from './social-capacity-account.vue';

  const props = defineProps<{
    visible: boolean;
    data?: SocialCapacityDetail | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', v: boolean): void;
    (e: 'done'): void;
  }>();

  const [vehicleTypeDict, trailerTypeDict, sourceDict] = useDictData([
    DICT_CODE_VEHICLE_TYPE,
    DICT_CODE_TRAILER_TYPE,
    DICT_CODE_SOCIAL_CAPACITY_SOURCE
  ]);

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const formRef = ref<FormInstance | null>(null);
  const activeTab = ref('basic');
  const saving = ref(false);
  const submitting = ref(false);

  type FullForm = SocialCapacityForm & {
    id?: number;
    socialCode?: string;
    approvalStatus?: number;
    status?: number;
    vehicle: SocialCapacityVehicleInfo;
    driver: SocialCapacityDriverInfo;
  };

  const buildEmptyForm = (): FullForm => ({
    source: '',
    sourceRemark: '',
    referrerUserId: undefined,
    remark: '',
    vehicle: {
      plateNumber: '',
      plateCategory: 'YELLOW',
      hasTrailer: 0
    },
    driver: {
      name: '',
      phone: '',
      gender: 0
    }
  });

  const form = reactive<FullForm>(buildEmptyForm());

  const isEdit = computed(() => !!form.id);
  const isApproving = computed(() => form.approvalStatus === 1);
  const canSave = computed(
    () => !isApproving.value && form.approvalStatus !== undefined
      ? form.approvalStatus !== 1
      : true
  );
  const canSubmit = computed(
    () =>
      isEdit.value && (form.approvalStatus === 0 || form.approvalStatus === 3)
  );
  const canWithdraw = computed(() => isEdit.value && form.approvalStatus === 1);

  const hasTrailerBool = computed({
    get: () => form.vehicle.hasTrailer === 1,
    set: (v) => {
      form.vehicle.hasTrailer = v ? 1 : 0;
    }
  });

  const rules: FormRules = {
    'driver.name': [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    'driver.phone': [
      { required: true, message: '请输入手机号', trigger: 'blur' }
    ],
    'vehicle.plateNumber': [
      { required: true, message: '请输入车牌号', trigger: 'blur' }
    ]
  };

  const approvalLabel = (s?: number) =>
    s === 0
      ? '草稿'
      : s === 1
        ? '待审核'
        : s === 2
          ? '已通过'
          : s === 3
            ? '已驳回'
            : '—';
  const approvalTagType = (s?: number): 'info' | 'primary' | 'success' | 'danger' =>
    s === 1 ? 'primary' : s === 2 ? 'success' : s === 3 ? 'danger' : 'info';

  const statusLabel = (s?: number) =>
    s === 0
      ? '未生效'
      : s === 1
        ? '正常'
        : s === 2
          ? '停用'
          : s === 3
            ? '黑名单'
            : '—';
  const statusTagType = (s?: number): 'info' | 'success' | 'warning' | 'danger' =>
    s === 1 ? 'success' : s === 2 ? 'warning' : s === 3 ? 'danger' : 'info';

  const onOpen = async () => {
    Object.assign(form, buildEmptyForm());
    activeTab.value = 'basic';
    if (props.data?.id) {
      // 取最新详情
      try {
        const fresh = await getSocialCapacity(props.data.id);
        applyDetail(fresh);
      } catch {
        applyDetail(props.data);
      }
    }
  };

  const applyDetail = (d: SocialCapacityDetail) => {
    form.id = d.id;
    form.socialCode = d.socialCode;
    form.approvalStatus = d.approvalStatus;
    form.status = d.status;
    form.source = d.source;
    form.sourceRemark = d.sourceRemark;
    form.referrerUserId = d.referrerUserId;
    form.remark = d.remark;
    if (d.vehicle) {
      Object.assign(form.vehicle, d.vehicle);
    }
    if (d.driver) {
      Object.assign(form.driver, d.driver);
    }
  };

  watch(
    () => props.visible,
    (v) => {
      if (!v) {
        formRef.value?.clearValidate();
      }
    }
  );

  const buildPayload = (): SocialCapacityForm => ({
    source: form.source,
    sourceRemark: form.sourceRemark,
    referrerUserId: form.referrerUserId,
    remark: form.remark,
    vehicle: { ...form.vehicle },
    driver: { ...form.driver }
  });

  const save = async () => {
    if (!formRef.value) return;
    try {
      await formRef.value.validate();
    } catch {
      EleMessage.warning({ message: '请完善必填字段', plain: true });
      return;
    }
    saving.value = true;
    try {
      const payload = buildPayload();
      if (form.id) {
        const detail = await updateSocialCapacity(form.id, payload);
        applyDetail(detail);
      } else {
        const detail = await addSocialCapacity(payload);
        applyDetail(detail);
      }
      EleMessage.success({ message: '保存成功', plain: true });
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '保存失败', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const submitForApproval = async () => {
    if (!form.id) return;
    try {
      await ElMessageBox.confirm('提交审核后将不可编辑（除结算账户）。确认提交？', '系统提示', {
        type: 'warning',
        draggable: true
      });
    } catch {
      return;
    }
    submitting.value = true;
    try {
      const detail = await submitSocialCapacity(form.id);
      applyDetail(detail);
      EleMessage.success({ message: '已提交审核', plain: true });
      emit('done');
      updateVisible(false);
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '提交失败', plain: true });
    } finally {
      submitting.value = false;
    }
  };

  const withdraw = async () => {
    if (!form.id) return;
    submitting.value = true;
    try {
      const detail = await withdrawSocialCapacity(form.id);
      applyDetail(detail);
      EleMessage.success({ message: '已撤回审核', plain: true });
      emit('done');
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '撤回失败', plain: true });
    } finally {
      submitting.value = false;
    }
  };
</script>

<style scoped>
  .sc-edit-badges {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
    padding: 6px 10px;
    background: var(--el-fill-color-light);
    border-radius: 4px;
    font-size: 13px;
  }
  .sc-edit-tabs :deep(.el-tabs__content) {
    max-height: 60vh;
    overflow-y: auto;
  }
</style>
