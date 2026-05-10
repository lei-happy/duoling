<template>
  <el-dialog
    :title="isEdit ? '编辑驾驶员' : '新增驾驶员'"
    :model-value="visible"
    width="780px"
    draggable
    class="driver-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="basicRules"
      label-width="0"
      class="driver-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="driver-edit-tabs">
        <el-tab-pane label="基础信息" name="basic">
          <div class="driver-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item prop="name">
                  <floating-label
                    label="请输入姓名"
                    type="input"
                    v-model.trim="form.name"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="phone">
                  <floating-label
                    label="请输入手机号"
                    type="input"
                    v-model.trim="form.phone"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    v-model="form.gender"
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
                    v-model.trim="form.idCard"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入紧急联系人"
                    type="input"
                    v-model.trim="form.emergencyContact"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入紧急联系电话"
                    type="input"
                    v-model.trim="form.emergencyPhone"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <floating-label
                    label="请输入家庭住址"
                    type="input"
                    v-model.trim="form.homeAddress"
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

        <el-tab-pane label="资质信息" name="license">
          <div class="driver-tab-pane">
            <el-row :gutter="12" class="driver-license-row">
              <el-col :span="5" :xs="24" :sm="5">
                <el-form-item>
                  <floating-label
                    v-model="form.licenseType"
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
              <el-col :span="10" :xs="24" :sm="10">
                <el-form-item>
                  <floating-label
                    label="请输入驾照号码"
                    type="input"
                    v-model.trim="form.licenseNo"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="9" :xs="24" :sm="9">
                <el-form-item>
                  <floating-label
                    label="请选择驾照有效期"
                    type="date"
                    date-type="date"
                    v-model="form.licenseExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12" class="driver-license-row">
              <el-col :span="12" :xs="24" :sm="12">
                <el-form-item>
                  <floating-label
                    label="请输入从业资格证号"
                    type="input"
                    v-model.trim="form.qualificationNo"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12" :xs="24" :sm="12">
                <el-form-item>
                  <floating-label
                    label="请选择资格证有效期"
                    type="date"
                    date-type="date"
                    v-model="form.qualificationExpire"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="driver-photo-section-title">证件照片</div>
            <div class="driver-doc-gallery">
              <div
                v-for="doc in driverPhotoGallery"
                :key="doc.key"
                class="driver-doc-gallery__card"
              >
                <div class="driver-doc-gallery__title">{{ doc.title }}</div>
                <el-upload
                  class="driver-doc-gallery__upload"
                  :show-file-list="false"
                  :http-request="(opt: any) => handlePhotoUpload(opt, doc.field)"
                  accept="image/*"
                >
                  <div class="driver-doc-gallery__frame">
                    <el-image
                      v-if="(form as any)[doc.field]"
                      :src="resolveUploadUrl((form as any)[doc.field])"
                      fit="cover"
                      class="driver-doc-gallery__image"
                    />
                    <div v-else class="driver-doc-gallery__empty">
                      <el-icon :size="28"><Plus /></el-icon>
                      <span>点击上传</span>
                    </div>
                  </div>
                  <p class="driver-doc-gallery__hint">{{ doc.hint }}</p>
                </el-upload>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="运营属性" name="operation">
          <div class="driver-tab-pane">
            <el-row :gutter="12" class="driver-op-row">
              <el-col :span="8" :xs="24" :sm="8">
                <el-form-item class="driver-op-form-item">
                  <DepartmentSelect
                    v-model="form.departmentId"
                    placeholder="请选择所属部门"
                    clearable
                    class="driver-op-dept-select"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8" :xs="24" :sm="8">
                <el-form-item class="driver-op-form-item">
                  <floating-label
                    v-model="form.driverType"
                    label="请选择司机类型"
                    type="select"
                    clearable
                  >
                    <el-option label="自有" :value="1" />
                    <el-option label="外协" :value="2" />
                    <el-option label="临时" :value="3" />
                  </floating-label>
                </el-form-item>
              </el-col>
              <el-col :span="8" :xs="24" :sm="8">
                <el-form-item class="driver-op-form-item">
                  <floating-label
                    v-model="form.operationStatus"
                    label="请选择运营状态"
                    type="select"
                    clearable
                  >
                    <el-option label="可接单" :value="1" />
                    <el-option label="忙碌" :value="2" />
                    <el-option label="休假" :value="3" />
                    <el-option label="停运" :value="4" />
                  </floating-label>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="driver-photo-section-title">常跑线路</div>
            <div class="driver-section-toolbar">
              <el-button type="primary" size="small" @click="addRoute">
                添加线路
              </el-button>
              <span v-if="!isEdit" class="driver-hint">
                请先保存驾驶员后再管理线路
              </span>
            </div>
            <div class="driver-table-wrap">
            <el-table
              :data="routes"
              border
              stripe
              size="default"
              class="driver-nested-table driver-data-table"
            >
              <el-table-column label="出发地" min-width="160">
                <template #default="{ row, $index }">
                  <RegionsSelect
                    v-model="row.originValue"
                    type="provinceCity"
                    placeholder="选择出发地"
                    size="small"
                    @change="onRouteRegionChange(row, 'origin', $index)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="目的地" min-width="160">
                <template #default="{ row, $index }">
                  <RegionsSelect
                    v-model="row.destValue"
                    type="provinceCity"
                    placeholder="选择目的地"
                    size="small"
                    @change="onRouteRegionChange(row, 'dest', $index)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="70" align="center">
                <template #default="{ $index }">
                  <el-link
                    type="danger"
                    :underline="false"
                    @click="removeRoute($index)"
                  >
                    删除
                  </el-link>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="账户信息" name="account">
          <div class="driver-tab-pane">
            <div class="driver-section-toolbar">
              <el-button
                type="primary"
                size="small"
                :disabled="!isEdit"
                @click="addAccount"
              >
                新增账户
              </el-button>
              <span v-if="!isEdit" class="driver-hint">
                请先保存驾驶员基础信息后再添加账户
              </span>
            </div>
            <div class="driver-table-wrap">
            <el-table
              :data="accounts"
              border
              stripe
              size="default"
              class="driver-nested-table driver-data-table"
            >
              <el-table-column prop="accountType" label="账户类型" width="100" align="center">
                <template #default="{ row }">
                  <span v-if="row.accountType === 1">银行卡</span>
                  <span v-else-if="row.accountType === 2">油气款</span>
                  <span v-else-if="row.accountType === 3">积分</span>
                </template>
              </el-table-column>
              <el-table-column prop="accountName" label="账户名称" min-width="120" />
              <el-table-column prop="accountNo" label="账户号" min-width="160" />
              <el-table-column prop="balance" label="余额" width="100" align="right" />
              <el-table-column prop="status" label="状态" width="90" align="center">
                <template #default="{ row }">
                  <el-switch
                    :model-value="row.status === 1"
                    size="small"
                    @change="(checked: boolean) => toggleAccountStatus(row, checked)"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" align="center">
                <template #default="{ row }">
                  <el-link
                    type="primary"
                    :underline="false"
                    @click="editAccount(row)"
                  >
                    编辑
                  </el-link>
                  <el-divider direction="vertical" />
                  <el-link
                    type="danger"
                    :underline="false"
                    @click="deleteAccount(row)"
                  >
                    删除
                  </el-link>
                </template>
              </el-table-column>
            </el-table>
            </div>
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

    <!-- 账户编辑弹窗 -->
    <el-dialog
      v-model="accountDialogVisible"
      :title="editingAccount?.id ? '编辑账户' : '新增账户'"
      width="480px"
      append-to-body
      draggable
      :close-on-click-modal="false"
    >
      <el-form
        ref="accountFormRef"
        :model="accountForm"
        :rules="accountRules"
        label-width="0"
      >
        <el-form-item prop="accountType">
          <floating-label
            v-model="accountForm.accountType"
            label="请选择账户类型"
            type="select"
            clearable
          >
            <el-option label="银行卡" :value="1" />
            <el-option label="油气款" :value="2" />
            <el-option label="积分" :value="3" />
          </floating-label>
        </el-form-item>
        <el-form-item prop="accountName">
          <floating-label
            label="请输入账户名称"
            type="input"
            v-model.trim="accountForm.accountName"
            clearable
          />
        </el-form-item>
        <el-form-item prop="accountNo">
          <floating-label
            label="请输入账户号"
            type="input"
            v-model.trim="accountForm.accountNo"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <floating-label
            v-model="accountForm.status"
            label="请选择状态"
            type="select"
            clearable
          >
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </floating-label>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="accountDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="accountLoading"
          @click="handleAccountSubmit"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import DepartmentSelect from '@/components/DepartmentSelect/index.vue';
  import RegionsSelect from '@/components/RegionsSelect/index.vue';
  import { uploadFile } from '@/api/system/file';
  import { resolveUploadUrl } from '@/utils/upload-url';
  import {
    addDriver,
    updateDriver,
    listDriverAccounts,
    addDriverAccount,
    updateDriverAccount,
    removeDriverAccount,
    toggleAccountStatus as apiToggleAccountStatus,
    listDriverRoutes,
    saveDriverRoutes
  } from '@/api/capacity/self_capacity/driver';
  import type {
    Driver,
    DriverAccount,
    DriverRoute
  } from '@/api/capacity/self_capacity/driver/model';

  interface RouteRow extends DriverRoute {
    originValue?: string[];
    destValue?: string[];
  }

  const props = defineProps<{
    visible: boolean;
    data: Driver | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const activeTab = ref('basic');
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Driver>({});

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const accounts = ref<DriverAccount[]>([]);
  const accountDialogVisible = ref(false);
  const accountFormRef = ref<FormInstance>();
  const accountLoading = ref(false);
  const editingAccount = ref<DriverAccount | null>(null);
  const accountForm = reactive<Partial<DriverAccount>>({});

  const routes = ref<RouteRow[]>([]);

  /** 资质页证件画廊项（字段名与 Driver 一致） */
  const driverPhotoGallery = [
    {
      key: 'license',
      title: '驾驶证',
      field: 'licensePhoto' as const,
      hint: 'JPG / PNG'
    },
    {
      key: 'qualification',
      title: '从业资格证',
      field: 'qualificationPhoto' as const,
      hint: 'JPG / PNG'
    },
    {
      key: 'idFront',
      title: '身份证人像面',
      field: 'idCardFrontPhoto' as const,
      hint: 'JPG / PNG'
    },
    {
      key: 'idBack',
      title: '身份证国徽面',
      field: 'idCardBackPhoto' as const,
      hint: 'JPG / PNG'
    }
  ];

  const basicRules = reactive<FormRules>({
    name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
    phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }]
  });

  const accountRules = reactive<FormRules>({
    accountType: [
      { required: true, message: '请选择账户类型', trigger: 'change' }
    ],
    accountName: [
      { required: true, message: '请输入账户名称', trigger: 'blur' }
    ],
    accountNo: [
      { required: true, message: '请输入账户号', trigger: 'blur' }
    ]
  });

  const handlePhotoUpload = async (options: any, field: string) => {
    try {
      const res = await uploadFile(
        options.file,
        undefined,
        options.file.name,
        'driver_license'
      );
      (form as any)[field] = res.url;
      EleMessage.success({ message: '上传成功', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message || '上传失败', plain: true });
    }
  };

  const loadAccounts = async () => {
    if (!props.data?.id) {
      accounts.value = [];
      return;
    }
    try {
      const list = await listDriverAccounts(props.data.id);
      accounts.value = list ?? [];
    } catch {
      accounts.value = [];
    }
  };

  const loadRoutes = async () => {
    if (!props.data?.id) {
      routes.value = [];
      return;
    }
    try {
      const list = await listDriverRoutes(props.data.id);
      routes.value = (list ?? []).map((r: DriverRoute) => ({
        ...r,
        originValue: r.originCode ? r.originCode.split(',') : [],
        destValue: r.destCode ? r.destCode.split(',') : []
      }));
    } catch {
      routes.value = [];
    }
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        activeTab.value = 'basic';
        if (props.data) {
          Object.assign(form, { ...props.data });
          loadAccounts();
          loadRoutes();
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
          accounts.value = [];
          routes.value = [];
        }
        void nextTick(() => {
          formRef.value?.clearValidate();
        });
      } else {
        void nextTick(() => {
          formRef.value?.clearValidate();
        });
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) {
        activeTab.value = 'basic';
        return;
      }
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateDriver(form);
          await saveRoutes();
        } else {
          await addDriver(form);
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

  const addRoute = () => {
    routes.value.push({
      originCode: '',
      originName: '',
      destCode: '',
      destName: '',
      originValue: [],
      destValue: []
    });
  };

  const removeRoute = (index: number) => {
    routes.value.splice(index, 1);
  };

  const onRouteRegionChange = (row: RouteRow, type: 'origin' | 'dest', _index: number) => {
    const val = type === 'origin' ? row.originValue : row.destValue;
    if (val && val.length) {
      const code = val.join(',');
      const name = val[val.length - 1];
      if (type === 'origin') {
        row.originCode = code;
        row.originName = name;
      } else {
        row.destCode = code;
        row.destName = name;
      }
    } else {
      if (type === 'origin') {
        row.originCode = '';
        row.originName = '';
      } else {
        row.destCode = '';
        row.destName = '';
      }
    }
  };

  const saveRoutes = async () => {
    if (!props.data?.id) return;
    const validRoutes = routes.value.filter(
      (r) => r.originCode && r.destCode
    );
    try {
      await saveDriverRoutes(props.data.id, validRoutes);
    } catch {
      // route save failure should not block main save
    }
  };

  const toggleAccountStatus = async (row: DriverAccount, checked: boolean) => {
    const newStatus = checked ? 1 : 0;
    try {
      await apiToggleAccountStatus(row.id!, newStatus);
      row.status = newStatus;
      EleMessage.success({ message: '状态修改成功', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const addAccount = () => {
    editingAccount.value = null;
    Object.keys(accountForm).forEach((k) => {
      (accountForm as any)[k] = undefined;
    });
    accountForm.status = 1;
    accountDialogVisible.value = true;
  };

  const editAccount = (row: DriverAccount) => {
    editingAccount.value = row;
    Object.assign(accountForm, row);
    accountDialogVisible.value = true;
  };

  const handleAccountSubmit = () => {
    accountFormRef.value?.validate(async (valid) => {
      if (!valid) return;
      accountLoading.value = true;
      try {
        if (editingAccount.value?.id) {
          await updateDriverAccount({
            id: editingAccount.value.id,
            ...accountForm
          });
        } else {
          await addDriverAccount(props.data!.id!, accountForm);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        accountDialogVisible.value = false;
        loadAccounts();
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        accountLoading.value = false;
      }
    });
  };

  const deleteAccount = (row: DriverAccount) => {
    ElMessageBox.confirm('确定要删除该账户吗?', '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(async () => {
        try {
          await removeDriverAccount(row.id!);
          EleMessage.success({ message: '删除成功', plain: true });
          loadAccounts();
        } catch (e: any) {
          EleMessage.error({ message: e.message, plain: true });
        }
      })
      .catch(() => {});
  };
</script>

<style scoped>
  .driver-edit-form {
    margin: 0;
  }

  /* Tab 灰色底轨铺满整行，单项均分且文字居中 */
  .driver-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .driver-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .driver-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .driver-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .driver-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .driver-edit-tabs :deep(.el-tabs__item) {
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

  .driver-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .driver-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .driver-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .driver-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  /* 顶部留白：浮动标签上浮后不被裁切；与 Tab 条留出间距 */
  .driver-tab-pane {
    max-height: min(420px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  /* 浮动标签与输入框上边框「穿线」问题：抬高并加厚底色遮挡边框 */
  .driver-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .driver-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .driver-edit-dialog :deep(.driver-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .driver-op-row :deep(.el-form-item__content) {
    width: 100%;
  }

  .driver-op-dept-select {
    width: 100%;
  }

  .driver-op-form-item {
    width: 100%;
    margin-bottom: 12px;
  }

  .driver-photo-section-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 8px 0 10px;
    padding-left: 2px;
    border-left: 3px solid var(--el-color-primary);
    line-height: 1.2;
  }

  .driver-section-toolbar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 10px;
  }

  .driver-hint {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }

  .driver-nested-table {
    width: 100%;
    margin-bottom: 0;
  }

  .driver-table-wrap {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
    border: 1px solid var(--el-border-color-lighter);
    background: var(--el-bg-color);
  }

  .driver-data-table :deep(.el-table__inner-wrapper::before) {
    display: none;
  }

  .driver-data-table :deep(.el-table__header-wrapper th.el-table__cell) {
    background: var(--el-fill-color-light) !important;
    color: var(--el-text-color-regular);
    font-weight: 600;
    font-size: 13px;
  }

  .driver-data-table :deep(.el-table__header .cell) {
    padding: 0 10px;
  }

  .driver-data-table :deep(.el-table__body .el-table__cell) {
    vertical-align: middle;
  }

  .driver-data-table :deep(.el-table__body .cell) {
    padding: 10px 10px;
  }

  .driver-data-table :deep(.el-table__row:hover > td.el-table__cell) {
    background-color: var(--el-fill-color-lighter) !important;
  }

  .driver-data-table :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
    background: var(--el-fill-color-blank);
  }

  .driver-license-row {
    margin-bottom: 4px;
  }

  .driver-doc-gallery {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 4px;
  }

  @media (max-width: 768px) {
    .driver-doc-gallery {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 480px) {
    .driver-doc-gallery {
      grid-template-columns: 1fr;
    }
  }

  .driver-doc-gallery__card {
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 10px 10px 8px;
    background: var(--el-fill-color-blank);
    transition:
      box-shadow 0.2s,
      border-color 0.2s;
  }

  .driver-doc-gallery__card:hover {
    border-color: var(--el-color-primary-light-5);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  }

  .driver-doc-gallery__title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    text-align: center;
    margin-bottom: 8px;
  }

  .driver-doc-gallery__upload {
    display: block;
    width: 100%;
  }

  .driver-doc-gallery__upload :deep(.el-upload) {
    display: block;
    width: 100%;
    cursor: pointer;
  }

  .driver-doc-gallery__frame {
    position: relative;
    width: 100%;
    aspect-ratio: 4 / 3;
    border-radius: 8px;
    overflow: hidden;
    border: 1px dashed var(--el-border-color);
    background: var(--el-fill-color-light);
    transition: border-color 0.2s;
  }

  .driver-doc-gallery__upload:hover .driver-doc-gallery__frame {
    border-color: var(--el-color-primary);
  }

  .driver-doc-gallery__image {
    width: 100%;
    height: 100%;
    display: block;
  }

  .driver-doc-gallery__empty {
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

  .driver-doc-gallery__hint {
    margin: 8px 0 0;
    text-align: center;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    line-height: 1.3;
  }
</style>
