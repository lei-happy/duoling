<template>
  <el-dialog
    :title="isEdit ? '编辑社会运力' : '新增社会运力'"
    :model-value="visible"
    width="860px"
    draggable
    class="sc-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
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

    <el-alert
      v-if="form.approvalStatus === 2"
      type="info"
      :closable="false"
      show-icon
      class="sc-edit-reapproval-hint"
      title="修改运力信息后请先保存，再提交审核；审批通过后变更生效。仅修改备注不需重新审核。"
    />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      :disabled="isApproving"
      label-width="0"
      class="sc-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="sc-edit-tabs">
        <!-- ==== 基础信息 ==== -->
        <el-tab-pane label="基础信息" name="basic">
          <div class="sc-tab-pane">
            <el-row :gutter="16">
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
                    label="请输入备注"
                    type="input"
                    input-type="textarea"
                    v-model.trim="form.remark"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- ==== 车辆信息 ==== -->
        <el-tab-pane label="车辆信息" name="vehicle">
          <div class="sc-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item prop="vehicle.plateNumber">
                  <floating-label
                    label="请输入车牌号"
                    type="input"
                    v-model.trim="form.vehicle.plateNumber"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    v-model="form.vehicle.plateCategory"
                    label="请选择车牌类型"
                    type="select"
                  >
                    <el-option label="蓝牌" value="BLUE" />
                    <el-option label="黄牌" value="YELLOW" />
                    <el-option label="新能源" value="NEW_ENERGY" />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <dict-select-hint-wrap dict-name="车辆类型">
                    <floating-label
                      v-model="form.vehicle.vehicleType"
                      label="请选择车辆类型"
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
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入品牌"
                    type="input"
                    v-model.trim="form.vehicle.brand"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入型号"
                    type="input"
                    v-model.trim="form.vehicle.model"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入颜色"
                    type="input"
                    v-model.trim="form.vehicle.color"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入车架号"
                    type="input"
                    v-model.trim="form.vehicle.vin"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入发动机号"
                    type="input"
                    v-model.trim="form.vehicle.engineNo"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入载重(吨)"
                    type="input"
                    input-type="number"
                    v-model="vehicleLoadCapacityStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入容积(m³)"
                    type="input"
                    input-type="number"
                    v-model="vehicleVolumeCapacityStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入车长(m)"
                    type="input"
                    input-type="number"
                    v-model="vehicleLengthStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入轴数"
                    type="input"
                    input-type="number"
                    v-model="vehicleAxleCountStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    type="date"
                    date-type="date"
                    label="请选择注册日期"
                    v-model="form.vehicle.registrationDate"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    type="date"
                    date-type="date"
                    label="请选择年检到期日"
                    v-model="form.vehicle.inspectionExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    type="date"
                    date-type="date"
                    label="请选择保险到期日"
                    v-model="form.vehicle.insuranceExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入道路运输证号"
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
                    label="请选择道路运输证有效期"
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
                <el-col :span="12">
                  <el-form-item>
                    <floating-label
                      label="请输入挂车车牌号"
                      type="input"
                      v-model.trim="form.vehicle.trailerPlate"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item>
                    <dict-select-hint-wrap dict-name="挂车类型">
                      <floating-label
                        v-model="form.vehicle.trailerType"
                        label="请选择挂车类型"
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
                <el-col :span="12">
                  <el-form-item>
                    <floating-label
                      label="请输入挂车载重(吨)"
                      type="input"
                      input-type="number"
                      v-model="trailerLoadCapacityStr"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </template>
            </el-row>
            <div class="sc-photo-section-title">证件照片</div>
            <div class="sc-doc-gallery">
              <div
                v-for="doc in vehiclePhotoGallery"
                :key="doc.key"
                class="sc-doc-gallery__card"
              >
                <div class="sc-doc-gallery__title">{{ doc.title }}</div>
                <el-upload
                  class="sc-doc-gallery__upload"
                  :show-file-list="false"
                  :http-request="
                    (opt: any) => handleVehiclePhotoUpload(opt, doc.field)
                  "
                  accept="image/*"
                >
                  <div class="sc-doc-gallery__frame">
                    <el-image
                      v-if="form.vehicle[doc.field]"
                      :src="resolveUploadUrl(form.vehicle[doc.field])"
                      fit="cover"
                      class="sc-doc-gallery__image"
                    />
                    <div v-else class="sc-doc-gallery__empty">
                      <el-icon :size="28"><Plus /></el-icon>
                      <span>点击上传</span>
                    </div>
                  </div>
                  <p class="sc-doc-gallery__hint">{{ doc.hint }}</p>
                </el-upload>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- ==== 驾驶员信息 ==== -->
        <el-tab-pane label="驾驶员信息" name="driver">
          <div class="sc-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item prop="driver.name">
                  <floating-label
                    label="请输入姓名"
                    type="input"
                    v-model.trim="form.driver.name"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="driver.phone">
                  <floating-label
                    label="请输入手机号"
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
                    label="请选择性别"
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
                    label="请输入身份证号"
                    type="input"
                    v-model.trim="form.driver.idCard"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    v-model="form.driver.licenseType"
                    label="请选择驾照类型"
                    type="select"
                    clearable
                  >
                    <el-option label="A1" value="A1" />
                    <el-option label="A2" value="A2" />
                    <el-option label="A3" value="A3" />
                    <el-option label="B1" value="B1" />
                    <el-option label="B2" value="B2" />
                    <el-option label="C1" value="C1" />
                    <el-option label="C2" value="C2" />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入驾照号码"
                    type="input"
                    v-model.trim="form.driver.licenseNo"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    type="date"
                    date-type="date"
                    label="请选择驾照有效期"
                    v-model="form.driver.licenseExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入从业资格证号"
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
                    label="请选择资格证有效期"
                    v-model="form.driver.qualificationExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入紧急联系人"
                    type="input"
                    v-model.trim="form.driver.emergencyContact"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入紧急联系电话"
                    type="input"
                    v-model.trim="form.driver.emergencyPhone"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <floating-label
                    label="请输入居住地址"
                    type="input"
                    v-model.trim="form.driver.homeAddress"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="sc-photo-section-title">证件照片</div>
            <div class="sc-doc-gallery">
              <div
                v-for="doc in driverPhotoGallery"
                :key="doc.key"
                class="sc-doc-gallery__card"
              >
                <div class="sc-doc-gallery__title">{{ doc.title }}</div>
                <el-upload
                  class="sc-doc-gallery__upload"
                  :show-file-list="false"
                  :http-request="
                    (opt: any) => handleDriverPhotoUpload(opt, doc.field)
                  "
                  accept="image/*"
                >
                  <div class="sc-doc-gallery__frame">
                    <el-image
                      v-if="form.driver[doc.field]"
                      :src="resolveUploadUrl(form.driver[doc.field])"
                      fit="cover"
                      class="sc-doc-gallery__image"
                    />
                    <div v-else class="sc-doc-gallery__empty">
                      <el-icon :size="28"><Plus /></el-icon>
                      <span>点击上传</span>
                    </div>
                  </div>
                  <p class="sc-doc-gallery__hint">{{ doc.hint }}</p>
                </el-upload>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- ==== 结算账户 ==== -->
        <el-tab-pane
          label="结算账户"
          name="account"
          :disabled="!isEdit"
        >
          <div class="sc-tab-pane">
            <social-capacity-account
              v-if="isEdit && form.id"
              :social-capacity-id="form.id"
              :read-only="false"
            />
            <el-empty
              v-else
              description="请先保存基础 / 车辆 / 驾驶员信息后再维护结算账户"
              :image-size="80"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
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
  import { Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import DictSelectHintWrap from '@/components/DictSelectHintWrap/index.vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { useDictData } from '@/utils/use-dict-data';
  import { uploadFile } from '@/api/system/file';
  import { resolveUploadUrl } from '@/utils/upload-url';
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

  type VehiclePhotoField = keyof Pick<
    SocialCapacityVehicleInfo,
    | 'vehicleLicensePhoto'
    | 'vehicleLicenseBackPhoto'
    | 'transportLicensePhoto'
    | 'vehiclePhoto'
  >;

  type DriverPhotoField = keyof Pick<
    SocialCapacityDriverInfo,
    | 'licensePhoto'
    | 'qualificationPhoto'
    | 'idCardFrontPhoto'
    | 'idCardBackPhoto'
  >;

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

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

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

  const vehiclePhotoGallery: Array<{
    key: string;
    title: string;
    field: VehiclePhotoField;
    hint: string;
  }> = [
    {
      key: 'vehicleLicense',
      title: '行驶证主页',
      field: 'vehicleLicensePhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'vehicleLicenseBack',
      title: '行驶证副页',
      field: 'vehicleLicenseBackPhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'transportLicense',
      title: '道路运输证',
      field: 'transportLicensePhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'vehicle',
      title: '车辆外观照',
      field: 'vehiclePhoto',
      hint: 'JPG / PNG'
    }
  ];

  const driverPhotoGallery: Array<{
    key: string;
    title: string;
    field: DriverPhotoField;
    hint: string;
  }> = [
    {
      key: 'license',
      title: '驾驶证',
      field: 'licensePhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'qualification',
      title: '从业资格证',
      field: 'qualificationPhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'idFront',
      title: '身份证人像面',
      field: 'idCardFrontPhoto',
      hint: 'JPG / PNG'
    },
    {
      key: 'idBack',
      title: '身份证国徽面',
      field: 'idCardBackPhoto',
      hint: 'JPG / PNG'
    }
  ];

  const numToStr = (n: number | undefined | null) =>
    n != null && !Number.isNaN(Number(n)) ? String(n) : '';

  const makeNumField = (
    getter: () => number | undefined,
    setter: (v: number | undefined) => void
  ) =>
    computed({
      get: () => numToStr(getter()),
      set: (v: string) => {
        const t = v?.trim();
        if (t === '' || t == null) {
          setter(undefined);
          return;
        }
        const n = Number(t);
        setter(Number.isFinite(n) ? Math.round(n * 100) / 100 : undefined);
      }
    });

  const vehicleLoadCapacityStr = makeNumField(
    () => form.vehicle.loadCapacity,
    (v) => {
      form.vehicle.loadCapacity = v;
    }
  );
  const vehicleVolumeCapacityStr = makeNumField(
    () => form.vehicle.volumeCapacity,
    (v) => {
      form.vehicle.volumeCapacity = v;
    }
  );
  const vehicleLengthStr = makeNumField(
    () => form.vehicle.length,
    (v) => {
      form.vehicle.length = v;
    }
  );
  const vehicleAxleCountStr = computed({
    get: () => numToStr(form.vehicle.axleCount),
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.vehicle.axleCount = undefined;
        return;
      }
      const n = Number(t);
      form.vehicle.axleCount = Number.isFinite(n) ? Math.round(n) : undefined;
    }
  });
  const trailerLoadCapacityStr = makeNumField(
    () => form.vehicle.trailerLoadCapacity,
    (v) => {
      form.vehicle.trailerLoadCapacity = v;
    }
  );

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

  const handleVehiclePhotoUpload = async (
    options: any,
    field: VehiclePhotoField
  ) => {
    try {
      const res = await uploadFile(
        options.file,
        undefined,
        options.file.name,
        'vehicle'
      );
      form.vehicle[field] = res.url;
      EleMessage.success({ message: '上传成功', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message || '上传失败', plain: true });
    }
  };

  const handleDriverPhotoUpload = async (
    options: any,
    field: DriverPhotoField
  ) => {
    try {
      const res = await uploadFile(
        options.file,
        undefined,
        options.file.name,
        'driver_license'
      );
      form.driver[field] = res.url;
      EleMessage.success({ message: '上传成功', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message || '上传失败', plain: true });
    }
  };

  const onOpen = async () => {
    Object.assign(form, buildEmptyForm());
    activeTab.value = 'basic';
    if (props.data?.id) {
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
    const prevApprovalStatus = form.approvalStatus;
    try {
      const payload = buildPayload();
      if (form.id) {
        const detail = await updateSocialCapacity(form.id, payload);
        applyDetail(detail);
        if (prevApprovalStatus === 2 && detail.approvalStatus === 0) {
          EleMessage.success({
            message: '已保存，变更已进入草稿，请提交审核通过后生效',
            plain: true
          });
        } else {
          EleMessage.success({ message: '保存成功', plain: true });
        }
      } else {
        const detail = await addSocialCapacity(payload);
        applyDetail(detail);
        EleMessage.success({ message: '保存成功', plain: true });
      }
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
      await ElMessageBox.confirm(
        '提交审核后将进入待审核状态，审核期间不可编辑。确认提交？',
        '系统提示',
        {
          type: 'warning',
          draggable: true
        }
      );
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
  .sc-edit-form {
    margin: 0;
  }

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

  .sc-edit-reapproval-hint {
    margin-bottom: 10px;
  }

  .sc-edit-reapproval-hint :deep(.el-alert__title) {
    font-size: 13px;
    line-height: 1.5;
  }

  .sc-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .sc-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .sc-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .sc-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .sc-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .sc-edit-tabs :deep(.el-tabs__item) {
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

  .sc-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .sc-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .sc-edit-tabs :deep(.el-tabs__item.is-disabled) {
    cursor: not-allowed;
    opacity: 0.55;
  }

  .sc-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .sc-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .sc-tab-pane {
    max-height: min(420px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .sc-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .sc-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .sc-edit-dialog
    :deep(.sc-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .sc-photo-section-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 8px 0 10px;
    padding-left: 2px;
    border-left: 3px solid var(--el-color-primary);
    line-height: 1.2;
  }

  .sc-doc-gallery {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 4px;
  }

  @media (max-width: 768px) {
    .sc-doc-gallery {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 480px) {
    .sc-doc-gallery {
      grid-template-columns: 1fr;
    }
  }

  .sc-doc-gallery__card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 10px 10px 8px;
    background: var(--el-fill-color-blank);
    transition:
      box-shadow 0.2s,
      border-color 0.2s;
  }

  .sc-doc-gallery__card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  }

  .sc-doc-gallery__title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    text-align: center;
    margin-bottom: 8px;
  }

  .sc-doc-gallery__upload {
    display: block;
    width: 100%;
  }

  .sc-doc-gallery__upload :deep(.el-upload) {
    display: block;
    width: 100%;
    cursor: pointer;
  }

  .sc-doc-gallery__frame {
    position: relative;
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 8px;
    overflow: hidden;
    border: 1px dashed var(--el-border-color);
    background: var(--el-fill-color-light);
    transition: border-color 0.2s;
  }

  .sc-doc-gallery__upload:hover .sc-doc-gallery__frame {
    border-color: var(--el-color-primary);
  }

  .sc-doc-gallery__image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .sc-doc-gallery__empty {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .sc-doc-gallery__hint {
    margin: 8px 0 0;
    text-align: center;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    line-height: 1.3;
  }
</style>
