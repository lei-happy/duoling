<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent="">
        <el-form-item label="关键字">
          <el-input
            v-model="keyword"
            placeholder="供应商名称 / 编码"
            clearable
            style="width: 200px"
            @keyup.enter="fetchData"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button type="primary" @click="openSupplier()">新增供应商</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table
        :data="list"
        v-loading="loading"
        border
        highlight-current-row
        @current-change="onSelect"
      >
        <el-table-column prop="supplierCode" label="编码" width="140" />
        <el-table-column prop="supplierName" label="名称" min-width="160" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            {{ labelOf(SUPPLIER_TYPES, row.supplierType) }}
          </template>
        </el-table-column>
        <el-table-column prop="contactName" label="联系人" width="110" />
        <el-table-column prop="contactPhone" label="电话" width="140" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openSupplier(row)">编辑</el-button>
            <el-button link type="danger" @click="doRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <ele-card v-if="current">
      <div class="toolbar">
        <span class="sub-title">{{ current.supplierName }} 的站点</span>
        <el-button type="primary" @click="openStation()">新增站点</el-button>
      </div>
      <el-table :data="stations" border>
        <el-table-column prop="stationCode" label="站点编码" width="140" />
        <el-table-column prop="stationName" label="站点名称" min-width="160" />
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="openStation(row)">编辑</el-button>
            <el-button link type="danger" @click="doRemoveStation(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ele-card>

    <el-dialog
      v-model="supplierVisible"
      :title="supplierForm.id ? '编辑供应商' : '新增供应商'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="supplierFormRef"
        :model="supplierForm"
        :rules="supplierRules"
        label-width="96px"
      >
        <el-form-item label="供应商名称" prop="supplierName">
          <el-input v-model.trim="supplierForm.supplierName" placeholder="如 中石化、万金油" />
        </el-form-item>
        <el-form-item label="类型" prop="supplierType">
          <el-select v-model="supplierForm.supplierType" style="width: 100%">
            <el-option
              v-for="o in SUPPLIER_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="编码">
          <el-input
            v-model.trim="supplierForm.supplierCode"
            placeholder="可空，系统自动生成"
          />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model.trim="supplierForm.contactName" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model.trim="supplierForm.contactPhone" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="supplierForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="supplierVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveSupplier">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="stationVisible"
      :title="stationForm.id ? '编辑站点' : '新增站点'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="stationFormRef"
        :model="stationForm"
        :rules="stationRules"
        label-width="96px"
      >
        <el-form-item label="站点名称" prop="stationName">
          <el-input v-model.trim="stationForm.stationName" />
        </el-form-item>
        <el-form-item label="站点编码" prop="stationCode">
          <el-input
            v-model.trim="stationForm.stationCode"
            :disabled="!!stationForm.id"
            placeholder="供应商内唯一"
          />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model.trim="stationForm.address" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="stationForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stationVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveStation">保存</el-button>
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
    addStation,
    addSupplier,
    pageStations,
    pageSuppliers,
    removeStation,
    removeSupplier,
    updateStation,
    updateSupplier
  } from '@/api/energy';
  import { SUPPLIER_TYPES, asPage, labelOf } from '../_shared/options';

  defineOptions({ name: 'EnergySupplier' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const stations = ref<any[]>([]);
  const keyword = ref('');
  const current = ref<any>(null);

  const supplierVisible = ref(false);
  const stationVisible = ref(false);
  const supplierFormRef = ref<FormInstance>();
  const stationFormRef = ref<FormInstance>();
  const supplierForm = reactive<any>({ supplierType: 9 });
  const stationForm = reactive<any>({});

  const supplierRules: FormRules = {
    supplierName: [{ required: true, message: '请填写供应商名称', trigger: 'blur' }],
    supplierType: [{ required: true, message: '请选择类型', trigger: 'change' }]
  };
  const stationRules: FormRules = {
    stationName: [{ required: true, message: '请填写站点名称', trigger: 'blur' }],
    stationCode: [{ required: true, message: '请填写站点编码', trigger: 'blur' }]
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      list.value = asPage(await pageSuppliers({ keyword: keyword.value, page: 1, limit: 100 })).list;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载供应商失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const loadStations = async () => {
    if (!current.value) {
      stations.value = [];
      return;
    }
    stations.value = asPage(
      await pageStations({ supplierId: current.value.id, page: 1, limit: 100 })
    ).list;
  };

  const onSelect = (row: any) => {
    current.value = row;
    loadStations();
  };

  const openSupplier = (row?: any) => {
    Object.assign(supplierForm, {
      id: row?.id,
      supplierName: row?.supplierName || '',
      supplierType: row?.supplierType ?? 9,
      supplierCode: row?.supplierCode || '',
      contactName: row?.contactName || '',
      contactPhone: row?.contactPhone || '',
      remark: row?.remark || ''
    });
    supplierVisible.value = true;
  };

  const saveSupplier = async () => {
    await supplierFormRef.value?.validate();
    saving.value = true;
    try {
      if (supplierForm.id) {
        await updateSupplier(supplierForm.id, supplierForm);
        EleMessage.success({ message: '已保存供应商', plain: true });
      } else {
        await addSupplier(supplierForm);
        EleMessage.success({ message: '已新增供应商', plain: true });
      }
      supplierVisible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openStation = (row?: any) => {
    if (!current.value) return;
    Object.assign(stationForm, {
      id: row?.id,
      stationName: row?.stationName || '',
      stationCode: row?.stationCode || '',
      address: row?.address || '',
      remark: row?.remark || ''
    });
    stationVisible.value = true;
  };

  const saveStation = async () => {
    await stationFormRef.value?.validate();
    saving.value = true;
    try {
      if (stationForm.id) {
        await updateStation(stationForm.id, stationForm);
        EleMessage.success({ message: '已保存站点', plain: true });
      } else {
        await addStation({ ...stationForm, supplierId: current.value.id });
        EleMessage.success({ message: '已新增站点', plain: true });
      }
      stationVisible.value = false;
      loadStations();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const doRemove = (row: any) => {
    ElMessageBox.confirm(`确定删除供应商「${row.supplierName}」？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await removeSupplier(row.id);
      EleMessage.success({ message: '已删除供应商', plain: true });
      if (current.value?.id === row.id) current.value = null;
      fetchData();
    });
  };

  const doRemoveStation = (row: any) => {
    ElMessageBox.confirm(`确定删除站点「${row.stationName}」？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await removeStation(row.id);
      EleMessage.success({ message: '已删除站点', plain: true });
      loadStations();
    });
  };

  onMounted(fetchData);
</script>

<style scoped>
  .toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  .sub-title {
    font-weight: 600;
  }
</style>
