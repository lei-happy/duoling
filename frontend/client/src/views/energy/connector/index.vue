<template>
  <ele-page>
    <ele-card>
      <div class="toolbar">
        <el-button type="primary" @click="openAdd">新增接入</el-button>
      </div>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="connectorName" label="名称" min-width="160" />
        <el-table-column label="类型" width="140">
          <template #default="{ row }">
            {{ labelOf(CONNECTOR_CODES, row.connectorCode) }}
          </template>
        </el-table-column>
        <el-table-column prop="syncMode" label="同步方式" width="110" />
        <el-table-column prop="lastSyncTime" label="最近同步" min-width="160" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-upload
              v-if="row.connectorCode === 'excel'"
              :show-file-list="false"
              :http-request="(opt: any) => doImport(row, opt.file)"
            >
              <el-button link type="primary">导入 Excel</el-button>
            </el-upload>
            <el-button link type="primary" @click="doPull(row)">立即同步</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <el-dialog v-model="visible" title="新增数据接入" width="520px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="108px">
        <el-form-item label="接入名称" prop="connectorName">
          <el-input v-model.trim="form.connectorName" placeholder="如 中石化月账单导入" />
        </el-form-item>
        <el-form-item label="接入类型" prop="connectorCode">
          <el-select v-model="form.connectorCode" style="width: 100%">
            <el-option
              v-for="o in CONNECTOR_CODES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="supplierId">
          <el-select v-model="form.supplierId" filterable style="width: 100%">
            <el-option
              v-for="s in suppliers"
              :key="s.id"
              :label="s.supplierName"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="默认账户">
          <el-select v-model="form.accountId" clearable filterable style="width: 100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="a.accountName"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="同步方式">
          <el-select v-model="form.syncMode" style="width: 100%">
            <el-option label="手工" value="manual" />
            <el-option label="定时" value="cron" />
            <el-option label="间隔拉取" value="interval" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.syncMode === 'cron'" label="Cron">
          <el-input v-model.trim="form.cron" placeholder="如 0 2 * * *" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addConnector,
    importConnector,
    pageConnectors,
    pullConnector
  } from '@/api/energy';
  import { CONNECTOR_CODES, asPage, labelOf } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyConnector' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const visible = ref(false);
  const formRef = ref<FormInstance>();
  const form = reactive<any>({ connectorCode: 'excel', syncMode: 'manual' });
  const { suppliers, accounts, loadSuppliers, loadAccounts } = useEnergyLookups();

  const rules: FormRules = {
    connectorName: [{ required: true, message: '请填写接入名称', trigger: 'blur' }],
    connectorCode: [{ required: true, message: '请选择接入类型', trigger: 'change' }],
    supplierId: [{ required: true, message: '请选择供应商', trigger: 'change' }]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      list.value = asPage(await pageConnectors({ page: 1, limit: 50 })).list;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载接入配置失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const openAdd = async () => {
    await Promise.all([loadSuppliers(), loadAccounts()]);
    Object.assign(form, {
      connectorName: '',
      connectorCode: 'excel',
      supplierId: undefined,
      accountId: undefined,
      syncMode: 'manual',
      cron: '',
      remark: ''
    });
    visible.value = true;
  };

  const save = async () => {
    await formRef.value?.validate();
    saving.value = true;
    try {
      await addConnector(form);
      EleMessage.success({ message: '已新增接入配置', plain: true });
      visible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const doImport = async (row: any, file: File) => {
    try {
      const res: any = await importConnector(row.id, file);
      EleMessage.success({
        message: `已导入 ${res.imported ?? 0} 笔，重复 ${res.duplicated ?? 0} 笔`,
        plain: true
      });
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '导入失败，请检查文件后重试', plain: true });
    }
  };

  const doPull = async (row: any) => {
    try {
      await pullConnector(row.id);
      EleMessage.success({ message: '已发起同步', plain: true });
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '同步失败，请稍后重试', plain: true });
    }
  };

  onMounted(fetchData);
</script>
<style scoped>
  .toolbar {
    margin-bottom: 12px;
  }
</style>
