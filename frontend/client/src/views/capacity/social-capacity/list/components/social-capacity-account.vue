<template>
  <div class="sc-account">
    <div class="sc-account__toolbar">
      <el-button type="primary" :disabled="readOnly" @click="openCreate">
        新增结算账户
      </el-button>
      <span v-if="!readOnly" class="sc-account__hint">
        新增首条账户将自动设为默认；最多 1 条默认账户
      </span>
    </div>
    <el-table
      v-loading="loading"
      :data="accounts"
      class="sc-account__table"
      border
      stripe
    >
      <el-table-column label="默认" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isDefault === 1" type="success" size="small">默认</el-tag>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column label="账户类型" width="100">
        <template #default="{ row }">{{ accountTypeLabel(row.accountType) }}</template>
      </el-table-column>
      <el-table-column prop="accountLabel" label="标签" width="120" />
      <el-table-column prop="accountName" label="户名" min-width="120" />
      <el-table-column prop="accountNo" label="账号" min-width="160" />
      <el-table-column prop="bankName" label="开户行" min-width="120" />
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.status === 1" type="success" size="small">启用</el-tag>
          <el-tag v-else type="info" size="small">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            :disabled="readOnly || row.isDefault === 1 || row.status !== 1"
            @click="setDefault(row)"
          >
            设为默认
          </el-button>
          <el-button
            link
            type="primary"
            :disabled="readOnly"
            @click="openEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            link
            type="danger"
            :disabled="readOnly"
            @click="removeRow(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="formVisible"
      :title="formData.id ? '编辑结算账户' : '新增结算账户'"
      width="560px"
      append-to-body
      align-center
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        @submit.prevent=""
      >
        <el-form-item label="账户类型" prop="accountType">
          <el-select v-model="formData.accountType" placeholder="请选择" style="width: 100%">
            <el-option label="银行卡" :value="1" />
            <el-option label="支付宝" :value="2" />
            <el-option label="微信" :value="3" />
            <el-option label="其他" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="账户标签">
          <el-input v-model.trim="formData.accountLabel" placeholder="如：主账户 / 油卡" />
        </el-form-item>
        <el-form-item label="户名" prop="accountName">
          <el-input v-model.trim="formData.accountName" placeholder="请输入户名" />
        </el-form-item>
        <el-form-item label="账号" prop="accountNo">
          <el-input v-model.trim="formData.accountNo" placeholder="账号 / 手机号" />
        </el-form-item>
        <template v-if="formData.accountType === 1">
          <el-form-item label="开户行">
            <el-input v-model.trim="formData.bankName" placeholder="请输入开户行" />
          </el-form-item>
          <el-form-item label="开户支行">
            <el-input v-model.trim="formData.bankBranch" placeholder="请输入开户支行" />
          </el-form-item>
        </template>
        <el-form-item label="持卡人身份证">
          <el-input
            v-model.trim="formData.holderIdCard"
            placeholder="配偶卡 / 第三方代收时填写"
          />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch
            :model-value="formData.isDefault === 1"
            @update:model-value="(v: any) => (formData.isDefault = v ? 1 : 0)"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="formData.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
  import { ref, watch, reactive } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    listAccounts,
    addAccount,
    updateAccount,
    removeAccount,
    setDefaultAccount
  } from '@/api/capacity/social-capacity/list';
  import type {
    SocialCapacityAccount,
    SocialCapacityAccountForm
  } from '@/api/capacity/social-capacity/list/model';

  const props = defineProps<{
    socialCapacityId: number;
    readOnly?: boolean;
  }>();

  const accounts = ref<SocialCapacityAccount[]>([]);
  const loading = ref(false);

  const reload = async () => {
    if (!props.socialCapacityId) return;
    loading.value = true;
    try {
      accounts.value = (await listAccounts(props.socialCapacityId)) || [];
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '加载结算账户失败', plain: true });
    } finally {
      loading.value = false;
    }
  };

  watch(
    () => props.socialCapacityId,
    (id) => {
      if (id) reload();
      else accounts.value = [];
    },
    { immediate: true }
  );

  // ----- 弹窗表单 -----
  const formVisible = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const saving = ref(false);
  const formData = reactive<SocialCapacityAccountForm & { id?: number }>({
    accountType: 1,
    accountLabel: '',
    accountName: '',
    accountNo: '',
    bankName: '',
    bankBranch: '',
    holderIdCard: '',
    isDefault: 0,
    status: 1,
    remark: ''
  });

  const rules: FormRules = {
    accountType: [{ required: true, message: '请选择账户类型', trigger: 'change' }],
    accountName: [{ required: true, message: '请输入户名', trigger: 'blur' }],
    accountNo: [{ required: true, message: '请输入账号', trigger: 'blur' }]
  };

  const accountTypeLabel = (t?: number) =>
    t === 1
      ? '银行卡'
      : t === 2
        ? '支付宝'
        : t === 3
          ? '微信'
          : t === 4
            ? '其他'
            : '—';

  const resetForm = () => {
    Object.assign(formData, {
      id: undefined,
      accountType: 1,
      accountLabel: '',
      accountName: '',
      accountNo: '',
      bankName: '',
      bankBranch: '',
      holderIdCard: '',
      isDefault: 0,
      status: 1,
      remark: ''
    });
  };

  const openCreate = () => {
    resetForm();
    formVisible.value = true;
  };

  const openEdit = (row: SocialCapacityAccount) => {
    resetForm();
    Object.assign(formData, row);
    formVisible.value = true;
  };

  const save = async () => {
    if (!formRef.value) return;
    try {
      await formRef.value.validate();
    } catch {
      return;
    }
    saving.value = true;
    try {
      const { id, ...payload } = formData;
      if (id) {
        await updateAccount(props.socialCapacityId, id, payload);
      } else {
        await addAccount(props.socialCapacityId, payload);
      }
      EleMessage.success({ message: '保存成功', plain: true });
      formVisible.value = false;
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '保存失败', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const removeRow = async (row: SocialCapacityAccount) => {
    try {
      await ElMessageBox.confirm(`确定要删除此结算账户吗？`, '系统提示', {
        type: 'warning',
        draggable: true
      });
    } catch {
      return;
    }
    try {
      await removeAccount(props.socialCapacityId, row.id!);
      EleMessage.success({ message: '删除成功', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '删除失败', plain: true });
    }
  };

  const setDefault = async (row: SocialCapacityAccount) => {
    try {
      await setDefaultAccount(props.socialCapacityId, row.id!);
      EleMessage.success({ message: '已设为默认账户', plain: true });
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e?.message ?? '设置失败', plain: true });
    }
  };

  defineExpose({ reload });
</script>

<style scoped>
  .sc-account__toolbar {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .sc-account__hint {
    color: var(--el-color-info);
    font-size: 12px;
  }
  .sc-account__table {
    width: 100%;
  }
</style>
