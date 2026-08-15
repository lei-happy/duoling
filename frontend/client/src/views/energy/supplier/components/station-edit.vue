<template>
  <el-dialog
    :title="isEdit ? '编辑站点' : '新增站点'"
    :model-value="visible"
    width="760px"
    draggable
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="energy-edit-form"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item prop="supplierId">
            <floating-label
              v-model="form.supplierId"
              label="请选择所属供应商"
              type="select"
              filterable
              :clearable="false"
              :disabled="isEdit"
            >
              <el-option
                v-for="s in suppliers"
                :key="s.id"
                :label="s.supplierName"
                :value="s.id"
              />
            </floating-label>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="stationName">
            <floating-label
              label="请输入站点名称"
              type="input"
              v-model.trim="form.stationName"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item prop="stationCode">
            <floating-label
              label="请输入站点编码"
              type="input"
              v-model.trim="form.stationCode"
              :disabled="isEdit"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
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
              label="请输入经度"
              type="input"
              v-model.trim="form.longitude"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item>
            <floating-label
              label="请输入纬度"
              type="input"
              v-model.trim="form.latitude"
              clearable
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-divider content-position="left">结算价</el-divider>
          <div class="product-head">
            <p class="form-tip">
              这里填供应商给我们的结算单价，不是对外零售价。至少保留一条有效价格。
            </p>
            <el-button link type="primary" @click="addProductRow()">
              添加商品
            </el-button>
          </div>
          <el-table :data="form.products" border size="small" class="product-table">
            <el-table-column label="能源" width="120">
              <template #default="{ row }">
                <el-select
                  v-model="row.energyType"
                  style="width: 100%"
                  @change="onProductEnergy(row)"
                >
                  <el-option
                    v-for="o in ENERGY_TYPES"
                    :key="o.value"
                    :label="o.label"
                    :value="o.value"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="商品" min-width="140">
              <template #default="{ row }">
                <el-select
                  v-model="row.productId"
                  clearable
                  filterable
                  placeholder="可空"
                  style="width: 100%"
                  @change="onProductPicked(row)"
                >
                  <el-option
                    v-for="p in productsOf(row.energyType)"
                    :key="p.id"
                    :label="p.productName"
                    :value="p.id"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="结算价" width="130">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.settlementPrice"
                  :min="0"
                  :precision="4"
                  :controls="false"
                  style="width: 100%"
                />
              </template>
            </el-table-column>
            <el-table-column label="单位" width="80">
              <template #default="{ row }">
                {{ row.unit || unitOf(row.energyType) }}
              </template>
            </el-table-column>
            <el-table-column label="" width="56" align="center">
              <template #default="{ $index }">
                <el-button
                  link
                  type="danger"
                  @click="form.products.splice($index, 1)"
                >
                  删
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
        <el-col :span="24">
          <el-form-item>
            <floating-label
              label="请输入备注"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
      </el-row>
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
  import { computed, nextTick, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addStation, updateStation } from '@/api/energy';
  import { ENERGY_TYPES } from '../../_shared/options';

  const props = defineProps<{
    visible: boolean;
    data: Record<string, any> | null;
    suppliers: Array<{ id: number; supplierName: string }>;
    products: Array<Record<string, any>>;
    defaultSupplierId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Record<string, any>>({ products: [] });

  const rules = reactive<FormRules>({
    supplierId: [
      { required: true, message: '请选择所属供应商', trigger: 'change' }
    ],
    stationName: [
      { required: true, message: '请输入站点名称', trigger: 'blur' }
    ],
    stationCode: [
      { required: true, message: '请输入站点编码', trigger: 'blur' }
    ]
  });

  const unitOf = (energyType?: string) =>
    ENERGY_TYPES.find((o) => o.value === energyType)?.unit || 'L';

  const productsOf = (energyType?: string) =>
    (props.products || []).filter((p) => !energyType || p.energyType === energyType);

  const addProductRow = (energyType = 'OIL') => {
    form.products.push({
      energyType,
      productId: undefined,
      settlementPrice: undefined,
      unit: unitOf(energyType)
    });
  };

  const onProductEnergy = (row: any) => {
    row.unit = unitOf(row.energyType);
    row.productId = undefined;
  };

  const onProductPicked = (row: any) => {
    const p = props.products.find((x) => x.id === row.productId);
    if (!p) return;
    row.energyType = p.energyType;
    row.productName = p.productName;
    row.unit = p.standardUnit || unitOf(p.energyType);
  };

  const resetForm = () => {
    Object.assign(form, {
      id: undefined,
      supplierId: props.defaultSupplierId,
      stationName: '',
      stationCode: '',
      address: '',
      longitude: '',
      latitude: '',
      remark: '',
      products: []
    });
    addProductRow();
  };

  watch(
    () => props.visible,
    (val) => {
      if (!val) return;
      if (props.data?.id) {
        Object.assign(form, {
          id: props.data.id,
          supplierId: props.data.supplierId,
          stationName: props.data.stationName || '',
          stationCode: props.data.stationCode || '',
          address: props.data.address || '',
          longitude: props.data.longitude ?? '',
          latitude: props.data.latitude ?? '',
          remark: props.data.remark || '',
          products: (props.data.products || []).map((p: any) => ({
            energyType: p.energyType,
            productId: p.productId || undefined,
            productName: p.productName,
            settlementPrice: Number(p.settlementPrice),
            unit: p.unit
          }))
        });
        if (!form.products.length) addProductRow();
      } else {
        resetForm();
      }
      nextTick(() => formRef.value?.clearValidate());
    }
  );

  const updateVisible = (val: boolean) => emit('update:visible', val);

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      const productsPayload = (form.products || [])
        .filter((p: any) => p.settlementPrice != null && Number(p.settlementPrice) > 0)
        .map((p: any) => ({
          energyType: p.energyType,
          productId: p.productId || undefined,
          productName: p.productName || undefined,
          settlementPrice: p.settlementPrice,
          unit: p.unit || unitOf(p.energyType)
        }));
      loading.value = true;
      try {
        const payload = {
          supplierId: form.supplierId,
          stationName: form.stationName,
          stationCode: form.stationCode,
          address: form.address || undefined,
          longitude: form.longitude === '' ? undefined : form.longitude,
          latitude: form.latitude === '' ? undefined : form.latitude,
          remark: form.remark || undefined,
          products: productsPayload
        };
        if (isEdit.value) await updateStation(form.id, payload);
        else await addStation(payload);
        EleMessage.success({
          message: isEdit.value ? '已保存站点' : '已新增站点',
          plain: true
        });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        if (e?.message) EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .energy-edit-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  .energy-edit-form :deep(.el-divider) {
    margin: 0 0 12px;
  }

  .product-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 10px;
  }

  .form-tip {
    margin: 0;
    color: var(--el-text-color-secondary);
    font-size: 12px;
    line-height: 1.7;
  }

  .product-table {
    width: 100%;
    margin-bottom: 18px;
  }
</style>
