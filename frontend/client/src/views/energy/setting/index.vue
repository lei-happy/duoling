<template>
  <ele-page>
    <el-tabs v-model="tab">
      <el-tab-pane label="能源商品" name="product">
        <ele-card>
          <el-button type="primary" style="margin-bottom: 12px" @click="openProduct()">
            新增商品
          </el-button>
          <el-table :data="products" border>
            <el-table-column prop="productCode" label="编码" width="140" />
            <el-table-column prop="productName" label="名称" min-width="140" />
            <el-table-column label="类型" width="90">
              <template #default="{ row }">
                {{ labelOf(ENERGY_TYPES, row.energyType) }}
              </template>
            </el-table-column>
            <el-table-column prop="standardUnit" label="单位" width="80" />
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="openProduct(row)">编辑</el-button>
                <el-button link type="danger" @click="doRemoveProduct(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </ele-card>
      </el-tab-pane>
      <el-tab-pane label="车辆能源档案" name="profile">
        <ele-card>
          <el-button type="primary" style="margin-bottom: 12px" @click="openProfile()">
            维护档案
          </el-button>
          <el-table :data="profiles" border>
            <el-table-column label="车辆" min-width="140">
              <template #default="{ row }">
                {{ plateOf(row.vehicleId) }}
              </template>
            </el-table-column>
            <el-table-column label="能源" width="90">
              <template #default="{ row }">
                {{ labelOf(ENERGY_TYPES, row.energyType) }}
              </template>
            </el-table-column>
            <el-table-column prop="tankCapacity" label="油箱容量" width="110" />
            <el-table-column prop="batteryCapacity" label="电池容量" width="110" />
            <el-table-column prop="standardConsumptionPer100km" label="标准百公里" width="120" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button link type="primary" @click="openProfile(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </ele-card>
      </el-tab-pane>
      <el-tab-pane label="风控阈值" name="rule">
        <ele-card>
          <el-table :data="rules" border>
            <el-table-column prop="ruleName" label="规则" min-width="160" />
            <el-table-column prop="thresholdValue" label="阈值" width="120" />
            <el-table-column label="等级" width="90">
              <template #default="{ row }">
                {{ labelOf(RISK_LEVELS, row.riskLevel) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="primary" @click="openRule(row)">调整</el-button>
              </template>
            </el-table-column>
          </el-table>
        </ele-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="productVisible"
      :title="productForm.id ? '编辑商品' : '新增商品'"
      width="480px"
      :close-on-click-modal="false"
    >
      <el-form ref="productRef" :model="productForm" :rules="productRules" label-width="96px">
        <el-form-item label="商品编码" prop="productCode">
          <el-input
            v-model.trim="productForm.productCode"
            :disabled="!!productForm.id"
            placeholder="如 DIESEL_0"
          />
        </el-form-item>
        <el-form-item label="商品名称" prop="productName">
          <el-input v-model.trim="productForm.productName" placeholder="如 0#柴油" />
        </el-form-item>
        <el-form-item label="能源类型" prop="energyType">
          <el-select v-model="productForm.energyType" style="width: 100%" @change="onEnergyType">
            <el-option
              v-for="o in ENERGY_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标准单位" prop="standardUnit">
          <el-input v-model.trim="productForm.standardUnit" placeholder="L / kg / kWh" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model.trim="productForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="productVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="profileVisible"
      title="车辆能源档案"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="profileRef" :model="profileForm" :rules="profileRules" label-width="120px">
        <el-form-item label="车辆" prop="vehicleId">
          <el-select
            v-model="profileForm.vehicleId"
            filterable
            style="width: 100%"
            :disabled="!!profileForm.id"
          >
            <el-option
              v-for="v in vehicles"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="能源类型" prop="energyType">
          <el-select v-model="profileForm.energyType" style="width: 100%">
            <el-option
              v-for="o in ENERGY_TYPES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="默认商品">
          <el-select v-model="profileForm.defaultProductId" clearable filterable style="width: 100%">
            <el-option
              v-for="p in productList"
              :key="p.id"
              :label="p.productName"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="油箱/气瓶容量">
          <el-input-number
            v-model="profileForm.tankCapacity"
            :min="0"
            :precision="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="电池容量">
          <el-input-number
            v-model="profileForm.batteryCapacity"
            :min="0"
            :precision="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="标准百公里">
          <el-input-number
            v-model="profileForm.standardConsumptionPer100km"
            :min="0"
            :precision="2"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ruleVisible" title="调整风控阈值" width="480px" :close-on-click-modal="false">
      <el-form ref="ruleRef" :model="ruleForm" :rules="ruleRules" label-width="80px">
        <el-form-item label="阈值" prop="thresholdValue">
          <el-input-number
            v-model="ruleForm.thresholdValue"
            :precision="3"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="ruleForm.riskLevel" style="width: 100%">
            <el-option v-for="o in RISK_LEVELS" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveRule">保存</el-button>
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
    addProduct,
    listProducts,
    listRules,
    pageProfiles,
    removeProduct,
    updateProduct,
    updateRule,
    upsertProfile
  } from '@/api/energy';
  import { ENERGY_TYPES, RISK_LEVELS, asPage, labelOf } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergySetting' });

  const tab = ref('product');
  const saving = ref(false);
  const products = ref<any[]>([]);
  const productList = ref<any[]>([]);
  const profiles = ref<any[]>([]);
  const rules = ref<any[]>([]);
  const { vehicles, loadVehicles } = useEnergyLookups();

  const productVisible = ref(false);
  const profileVisible = ref(false);
  const ruleVisible = ref(false);
  const productRef = ref<FormInstance>();
  const profileRef = ref<FormInstance>();
  const ruleRef = ref<FormInstance>();
  const productForm = reactive<any>({ energyType: 'OIL', standardUnit: 'L' });
  const profileForm = reactive<any>({ energyType: 'OIL' });
  const ruleForm = reactive<any>({});

  const productRules: FormRules = {
    productCode: [{ required: true, message: '请填写商品编码', trigger: 'blur' }],
    productName: [{ required: true, message: '请填写商品名称', trigger: 'blur' }],
    energyType: [{ required: true, message: '请选择能源类型', trigger: 'change' }]
  };
  const profileRules: FormRules = {
    vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
    energyType: [{ required: true, message: '请选择能源类型', trigger: 'change' }]
  };
  const ruleRules: FormRules = {
    thresholdValue: [{ required: true, message: '请填写阈值', trigger: 'change' }]
  };

  const plateOf = (id?: number) =>
    vehicles.value.find((v) => v.id === id)?.plateNumber || (id ? `车辆 ${id}` : '-');

  const load = async () => {
    await loadVehicles();
    products.value = (await listProducts()) || [];
    productList.value = products.value;
    profiles.value = asPage(await pageProfiles({ page: 1, limit: 50 })).list;
    rules.value = (await listRules()) || [];
  };

  const onEnergyType = (v: string) => {
    const unit = ENERGY_TYPES.find((o) => o.value === v)?.unit;
    if (unit) productForm.standardUnit = unit;
  };

  const openProduct = (row?: any) => {
    Object.assign(productForm, {
      id: row?.id,
      productCode: row?.productCode || '',
      productName: row?.productName || '',
      energyType: row?.energyType || 'OIL',
      standardUnit: row?.standardUnit || 'L',
      remark: row?.remark || ''
    });
    productVisible.value = true;
  };

  const saveProduct = async () => {
    await productRef.value?.validate();
    saving.value = true;
    try {
      if (productForm.id) await updateProduct(productForm.id, productForm);
      else await addProduct(productForm);
      EleMessage.success({ message: productForm.id ? '已保存商品' : '已新增商品', plain: true });
      productVisible.value = false;
      load();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const doRemoveProduct = (row: any) => {
    ElMessageBox.confirm(`确定删除商品「${row.productName}」？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await removeProduct(row.id);
      EleMessage.success({ message: '已删除商品', plain: true });
      load();
    });
  };

  const openProfile = async (row?: any) => {
    await loadVehicles();
    Object.assign(profileForm, {
      id: row?.id,
      vehicleId: row?.vehicleId,
      energyType: row?.energyType || 'OIL',
      defaultProductId: row?.defaultProductId,
      tankCapacity: row?.tankCapacity,
      batteryCapacity: row?.batteryCapacity,
      standardConsumptionPer100km: row?.standardConsumptionPer100km
    });
    profileVisible.value = true;
  };

  const saveProfile = async () => {
    await profileRef.value?.validate();
    saving.value = true;
    try {
      await upsertProfile(profileForm);
      EleMessage.success({ message: '已保存车辆档案', plain: true });
      profileVisible.value = false;
      load();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openRule = (row: any) => {
    Object.assign(ruleForm, {
      id: row.id,
      thresholdValue: row.thresholdValue,
      riskLevel: row.riskLevel || 'MEDIUM'
    });
    ruleVisible.value = true;
  };

  const saveRule = async () => {
    await ruleRef.value?.validate();
    saving.value = true;
    try {
      await updateRule(ruleForm.id, {
        thresholdValue: ruleForm.thresholdValue,
        riskLevel: ruleForm.riskLevel
      });
      EleMessage.success({ message: '已更新阈值', plain: true });
      ruleVisible.value = false;
      load();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '保存失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  onMounted(load);
</script>
