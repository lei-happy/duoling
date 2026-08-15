<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent="">
        <el-form-item label="关键字">
          <el-input
            v-model="where.keyword"
            placeholder="账户编码 / 名称"
            clearable
            style="width: 200px"
            @keyup.enter="reload(1)"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="reload(1)">查询</el-button>
          <el-button type="primary" @click="openEdit()">新增账户</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table :data="list" v-loading="loading" border row-key="id">
        <el-table-column prop="accountCode" label="账户编码" min-width="140" />
        <el-table-column prop="accountName" label="账户名称" min-width="160" />
        <el-table-column prop="supplierName" label="供应商" min-width="140" />
        <el-table-column label="能源" width="80">
          <template #default="{ row }">
            {{ labelOf(ENERGY_TYPES, row.energyType) }}
          </template>
        </el-table-column>
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            {{ labelOf(ACCOUNT_TYPES, row.accountType) }}
          </template>
        </el-table-column>
        <el-table-column prop="ledgerBalance" label="账面余额" width="120" />
        <el-table-column prop="availableBalance" label="可用余额" width="120" />
        <el-table-column prop="diffAmount" label="差异" width="100" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            {{ labelOf(ACCOUNT_STATUSES, row.status) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="openAdjust(row)">调账</el-button>
            <el-button link type="danger" @click="doRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          :current-page="page"
          :page-size="limit"
          :total="total"
          layout="total, prev, pager, next, sizes"
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
      </div>
    </ele-card>

    <el-dialog
      v-model="editVisible"
      :title="form.id ? '编辑账户' : '新增账户'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="108px">
        <el-form-item label="账户名称" prop="accountName">
          <el-input v-model.trim="form.accountName" placeholder="如 中石化预付主账户" />
        </el-form-item>
        <el-form-item label="供应商" prop="supplierId">
          <el-select
            v-model="form.supplierId"
            filterable
            style="width: 100%"
            :disabled="!!form.id"
          >
            <el-option
              v-for="s in suppliers"
              :key="s.id"
              :label="s.supplierName"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="能源类型" prop="energyType">
          <el-select v-model="form.energyType" style="width: 100%">
            <el-option
              v-for="o in ENERGY_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="账户类型" prop="accountType">
          <el-select v-model="form.accountType" style="width: 100%">
            <el-option
              v-for="o in ACCOUNT_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商账号">
          <el-input
            v-model.trim="form.externalAccountNo"
            placeholder="对方系统里的账号，可空"
          />
        </el-form-item>
        <el-form-item v-if="form.id" label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option
              v-for="o in ACCOUNT_STATUSES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="adjustVisible"
      title="调账"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-alert
        type="info"
        :closable="false"
        title="正数增加账面余额，负数减少。调账会留下流水，不能直接改余额。"
        style="margin-bottom: 16px"
      />
      <el-form ref="adjustRef" :model="adjustForm" :rules="adjustRules" label-width="96px">
        <el-form-item label="调账金额" prop="amount">
          <el-input-number
            v-model="adjustForm.amount"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="原因" prop="remark">
          <el-input
            v-model.trim="adjustForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请说明为什么调账，例如供应商手续费更正"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAdjust">确认调账</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addAccount,
    adjustAccount,
    pageAccounts,
    removeAccount,
    updateAccount
  } from '@/api/energy';
  import {
    ACCOUNT_STATUSES,
    ACCOUNT_TYPES,
    ENERGY_TYPES,
    asPage,
    labelOf
  } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyAccount' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(20);
  const where = reactive<{ keyword?: string }>({});
  const { suppliers, loadSuppliers } = useEnergyLookups();

  const editVisible = ref(false);
  const adjustVisible = ref(false);
  const formRef = ref<FormInstance>();
  const adjustRef = ref<FormInstance>();
  const form = reactive<any>({ energyType: 'OIL', accountType: 'PREPAID' });
  const adjustForm = reactive<any>({ amount: 0, remark: '', accountId: 0 });

  const rules: FormRules = {
    accountName: [{ required: true, message: '请填写账户名称', trigger: 'blur' }],
    supplierId: [{ required: true, message: '请选择供应商', trigger: 'change' }],
    energyType: [{ required: true, message: '请选择能源类型', trigger: 'change' }],
    accountType: [{ required: true, message: '请选择账户类型', trigger: 'change' }]
  };
  const adjustRules: FormRules = {
    amount: [{ required: true, message: '请填写调账金额', trigger: 'change' }],
    remark: [{ required: true, message: '请填写调账原因', trigger: 'blur' }]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      const res = asPage(
        await pageAccounts({ ...where, page: page.value, limit: limit.value })
      );
      list.value = res.list;
      total.value = res.count;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载账户失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };
  const reload = (p?: number) => {
    if (p) page.value = p;
    fetchData();
  };
  const onPageChange = (p: number) => {
    page.value = p;
    fetchData();
  };
  const onSizeChange = (s: number) => {
    limit.value = s;
    page.value = 1;
    fetchData();
  };

  const openEdit = (row?: any) => {
    Object.assign(form, {
      id: row?.id,
      accountName: row?.accountName || '',
      supplierId: row?.supplierId,
      energyType: row?.energyType || 'OIL',
      accountType: row?.accountType || 'PREPAID',
      externalAccountNo: row?.externalAccountNo || '',
      status: row?.status ?? 1,
      remark: row?.remark || ''
    });
    editVisible.value = true;
  };

  const save = async () => {
    await formRef.value?.validate();
    saving.value = true;
    try {
      if (form.id) await updateAccount(form.id, form);
      else await addAccount(form);
      EleMessage.success({ message: form.id ? '已保存账户' : '已新增账户', plain: true });
      editVisible.value = false;
      reload();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openAdjust = (row: any) => {
    Object.assign(adjustForm, { accountId: row.id, amount: 0, remark: '' });
    adjustVisible.value = true;
  };

  const saveAdjust = async () => {
    await adjustRef.value?.validate();
    if (!adjustForm.amount) {
      EleMessage.error({ message: '调账金额不能为 0', plain: true });
      return;
    }
    saving.value = true;
    try {
      await adjustAccount(adjustForm.accountId, {
        amount: adjustForm.amount,
        remark: adjustForm.remark
      });
      EleMessage.success({ message: '已完成调账', plain: true });
      adjustVisible.value = false;
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '调账失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const doRemove = (row: any) => {
    ElMessageBox.confirm(`确定删除账户「${row.accountName}」？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await removeAccount(row.id);
      EleMessage.success({ message: '已删除账户', plain: true });
      reload();
    });
  };

  onMounted(async () => {
    await loadSuppliers();
    fetchData();
  });
</script>

<style scoped>
  .pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
</style>
