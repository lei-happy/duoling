<template>
  <el-dialog
    :title="isEdit ? '编辑驾驶员' : '新增驾驶员'"
    :model-value="visible"
    @update:model-value="updateVisible"
    width="750px"
    draggable
  >
    <el-tabs v-model="activeTab">
      <!-- Tab 1: 基础信息 -->
      <el-tab-pane label="基础信息" name="basic">
        <el-form
          ref="basicFormRef"
          :model="form"
          :rules="basicRules"
          label-width="100px"
          @submit.prevent=""
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="form.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="手机号" prop="phone">
                <el-input v-model="form.phone" placeholder="请输入手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="性别">
                <el-select
                  v-model="form.gender"
                  placeholder="请选择性别"
                  style="width: 100%"
                >
                  <el-option label="男" :value="1" />
                  <el-option label="女" :value="2" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证号">
                <el-input
                  v-model="form.idCard"
                  placeholder="请输入身份证号"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="紧急联系人">
                <el-input
                  v-model="form.emergencyContact"
                  placeholder="请输入紧急联系人"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="紧急电话">
                <el-input
                  v-model="form.emergencyPhone"
                  placeholder="请输入紧急联系电话"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="家庭住址">
                <el-input
                  v-model="form.homeAddress"
                  placeholder="请输入家庭住址"
                />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item label="备注">
                <el-input
                  v-model="form.remark"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入备注"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-tab-pane>

      <!-- Tab 2: 资质信息 -->
      <el-tab-pane label="资质信息" name="license">
        <el-form :model="form" label-width="110px" @submit.prevent="">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="驾照类型">
                <el-select
                  v-model="form.licenseType"
                  placeholder="请选择驾照类型"
                  style="width: 100%"
                >
                  <el-option label="A1" value="A1" />
                  <el-option label="A2" value="A2" />
                  <el-option label="A3" value="A3" />
                  <el-option label="B1" value="B1" />
                  <el-option label="B2" value="B2" />
                  <el-option label="C1" value="C1" />
                  <el-option label="C2" value="C2" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="驾照号码">
                <el-input
                  v-model="form.licenseNo"
                  placeholder="请输入驾照号码"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="驾照有效期">
                <el-date-picker
                  v-model="form.licenseExpire"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="资格证号">
                <el-input
                  v-model="form.qualificationNo"
                  placeholder="请输入从业资格证号"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="资格证有效期">
                <el-date-picker
                  v-model="form.qualificationExpire"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider content-position="left">证件附件</el-divider>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="驾驶证">
                <el-upload
                  class="driver-photo-upload"
                  :show-file-list="false"
                  :http-request="(opt: any) => handlePhotoUpload(opt, 'licensePhoto')"
                  accept="image/*"
                >
                  <el-image
                    v-if="form.licensePhoto"
                    :src="resolveUploadUrl(form.licensePhoto)"
                    fit="cover"
                    style="width: 120px; height: 80px"
                  />
                  <div v-else class="driver-photo-placeholder">
                    <el-icon :size="24"><Plus /></el-icon>
                    <span>上传驾驶证</span>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="资格证">
                <el-upload
                  class="driver-photo-upload"
                  :show-file-list="false"
                  :http-request="(opt: any) => handlePhotoUpload(opt, 'qualificationPhoto')"
                  accept="image/*"
                >
                  <el-image
                    v-if="form.qualificationPhoto"
                    :src="resolveUploadUrl(form.qualificationPhoto)"
                    fit="cover"
                    style="width: 120px; height: 80px"
                  />
                  <div v-else class="driver-photo-placeholder">
                    <el-icon :size="24"><Plus /></el-icon>
                    <span>上传资格证</span>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证正面">
                <el-upload
                  class="driver-photo-upload"
                  :show-file-list="false"
                  :http-request="(opt: any) => handlePhotoUpload(opt, 'idCardFrontPhoto')"
                  accept="image/*"
                >
                  <el-image
                    v-if="form.idCardFrontPhoto"
                    :src="resolveUploadUrl(form.idCardFrontPhoto)"
                    fit="cover"
                    style="width: 120px; height: 80px"
                  />
                  <div v-else class="driver-photo-placeholder">
                    <el-icon :size="24"><Plus /></el-icon>
                    <span>上传正面</span>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证反面">
                <el-upload
                  class="driver-photo-upload"
                  :show-file-list="false"
                  :http-request="(opt: any) => handlePhotoUpload(opt, 'idCardBackPhoto')"
                  accept="image/*"
                >
                  <el-image
                    v-if="form.idCardBackPhoto"
                    :src="resolveUploadUrl(form.idCardBackPhoto)"
                    fit="cover"
                    style="width: 120px; height: 80px"
                  />
                  <div v-else class="driver-photo-placeholder">
                    <el-icon :size="24"><Plus /></el-icon>
                    <span>上传反面</span>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </el-tab-pane>

      <!-- Tab 3: 运营属性 -->
      <el-tab-pane label="运营属性" name="operation">
        <el-form :model="form" label-width="100px" @submit.prevent="">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="所属部门">
                <DepartmentSelect
                  v-model="form.departmentId"
                  placeholder="请选择所属部门"
                  clearable
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="司机类型">
                <el-select
                  v-model="form.driverType"
                  placeholder="请选择司机类型"
                  style="width: 100%"
                  clearable
                >
                  <el-option label="自有" :value="1" />
                  <el-option label="外协" :value="2" />
                  <el-option label="临时" :value="3" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="运营状态">
                <el-select
                  v-model="form.operationStatus"
                  placeholder="请选择运营状态"
                  style="width: 100%"
                  clearable
                >
                  <el-option label="可接单" :value="1" />
                  <el-option label="忙碌" :value="2" />
                  <el-option label="休假" :value="3" />
                  <el-option label="停运" :value="4" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-divider content-position="left">常跑线路</el-divider>
          <div style="margin-bottom: 12px">
            <el-button type="primary" size="small" @click="addRoute">
              添加线路
            </el-button>
            <span v-if="!isEdit" style="color: #999; margin-left: 8px; font-size: 12px">
              请先保存驾驶员后再管理线路
            </span>
          </div>
          <el-table :data="routes" border size="small" style="width: 100%">
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
        </el-form>
      </el-tab-pane>

      <!-- Tab 4: 账户信息 -->
      <el-tab-pane label="账户信息" name="account">
        <div style="margin-bottom: 12px">
          <el-button
            type="primary"
            size="small"
            :disabled="!isEdit"
            @click="addAccount"
          >
            新增账户
          </el-button>
          <span v-if="!isEdit" style="color: #999; margin-left: 8px; font-size: 12px">
            请先保存驾驶员基础信息后再添加账户
          </span>
        </div>
        <el-table :data="accounts" border size="small" style="width: 100%">
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
      </el-tab-pane>
    </el-tabs>
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
    >
      <el-form
        ref="accountFormRef"
        :model="accountForm"
        :rules="accountRules"
        label-width="90px"
      >
        <el-form-item label="账户类型" prop="accountType">
          <el-select
            v-model="accountForm.accountType"
            placeholder="请选择"
            style="width: 100%"
          >
            <el-option label="银行卡" :value="1" />
            <el-option label="油气款" :value="2" />
            <el-option label="积分" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户名称" prop="accountName">
          <el-input
            v-model="accountForm.accountName"
            placeholder="请输入账户名称"
          />
        </el-form-item>
        <el-form-item label="账户号" prop="accountNo">
          <el-input
            v-model="accountForm.accountNo"
            placeholder="请输入账户号"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="accountForm.status" style="width: 100%">
            <el-option label="正常" :value="1" />
            <el-option label="停用" :value="0" />
          </el-select>
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
  import { ref, reactive, watch, computed } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { Plus } from '@element-plus/icons-vue';
  import { EleMessage } from 'ele-admin-plus';
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
  const basicFormRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Driver>({});

  const accounts = ref<DriverAccount[]>([]);
  const accountDialogVisible = ref(false);
  const accountFormRef = ref<FormInstance>();
  const accountLoading = ref(false);
  const editingAccount = ref<DriverAccount | null>(null);
  const accountForm = reactive<Partial<DriverAccount>>({});

  const routes = ref<RouteRow[]>([]);

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
          Object.assign(form, props.data);
          loadAccounts();
          loadRoutes();
        } else {
          Object.keys(form).forEach((k) => {
            (form as any)[k] = undefined;
          });
          accounts.value = [];
          routes.value = [];
        }
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    basicFormRef.value?.validate(async (valid) => {
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
  .driver-photo-upload :deep(.el-upload) {
    border: 1px dashed var(--el-border-color);
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .driver-photo-upload :deep(.el-upload:hover) {
    border-color: var(--el-color-primary);
  }

  .driver-photo-placeholder {
    width: 120px;
    height: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 12px;
    gap: 4px;
  }
</style>
