<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-alert
        type="info"
        :closable="false"
        title="油补是付给司机的补贴；这里的消费是付给供应商的能源费。司机垫付只作台账，不扣能源账户、不重复计成本。"
        style="margin-bottom: 12px"
      />
      <el-form :inline="true" @submit.prevent="">
        <el-form-item label="关键字">
          <el-input
            v-model="keyword"
            placeholder="单号 / 卡号 / 车牌"
            clearable
            style="width: 180px"
            @keyup.enter="fetchData"
          />
        </el-form-item>
        <el-form-item label="匹配">
          <el-select v-model="matchStatus" clearable placeholder="全部" style="width: 130px">
            <el-option
              v-for="o in MATCH_STATUSES"
              :key="o.value"
              :label="o.label"
              :value="o.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button type="primary" @click="openAdd">手工录入</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="consumptionTime" label="消费时间" min-width="160" />
        <el-table-column prop="plateNumber" label="车牌" width="110" />
        <el-table-column prop="cardNo" label="卡号" min-width="130" />
        <el-table-column prop="productName" label="商品" width="100" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="amount" label="金额" width="100" />
        <el-table-column label="匹配" width="100">
          <template #default="{ row }">
            {{ labelOf(MATCH_STATUSES, row.matchStatus) }}
          </template>
        </el-table-column>
        <el-table-column label="来源" width="130">
          <template #default="{ row }">
            {{ labelOf(SOURCE_CHANNELS, row.sourceChannel) }}
          </template>
        </el-table-column>
        <el-table-column label="入账" width="80">
          <template #default="{ row }">
            {{ row.isLedgerAffecting === 0 ? '否' : '是' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openAssign(row)">归属</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          :current-page="page"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="(p: number) => { page = p; fetchData(); }"
        />
      </div>
    </ele-card>

    <el-dialog v-model="addVisible" title="手工录入消费" width="640px" :close-on-click-modal="false">
      <el-form ref="addRef" :model="addForm" :rules="addRules" label-width="108px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="消费时间" prop="consumptionTime">
              <el-date-picker
                v-model="addForm.consumptionTime"
                type="datetime"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="金额" prop="amount">
              <el-input-number
                v-model="addForm.amount"
                :min="0.01"
                :precision="2"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数量">
              <el-input-number
                v-model="addForm.quantity"
                :min="0"
                :precision="3"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价">
              <el-input-number
                v-model="addForm.unitPrice"
                :min="0"
                :precision="4"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="能源类型" prop="energyType">
              <el-select v-model="addForm.energyType" style="width: 100%">
                <el-option
                  v-for="o in ENERGY_TYPES"
                  :key="o.value"
                  :label="o.label"
                  :value="o.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="能源商品">
              <el-select v-model="addForm.energyProductId" clearable filterable style="width: 100%">
                <el-option
                  v-for="p in products"
                  :key="p.id"
                  :label="p.productName"
                  :value="p.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="能源账户">
              <el-select v-model="addForm.accountId" clearable filterable style="width: 100%">
                <el-option
                  v-for="a in accounts"
                  :key="a.id"
                  :label="a.accountName"
                  :value="a.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="卡号">
              <el-input v-model.trim="addForm.cardNo" placeholder="有卡号更容易自动匹配" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车辆">
              <el-select
                v-model="addForm.vehicleId"
                clearable
                filterable
                style="width: 100%"
                @change="onVehicleChange"
              >
                <el-option
                  v-for="v in vehicles"
                  :key="v.id"
                  :label="v.plateNumber"
                  :value="v.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="司机">
              <el-select v-model="addForm.driverId" clearable filterable style="width: 100%">
                <el-option
                  v-for="d in drivers"
                  :key="d.id"
                  :label="d.name"
                  :value="d.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="站点名称">
              <el-input v-model.trim="addForm.stationName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="本次里程">
              <el-input-number
                v-model="addForm.mileage"
                :min="0"
                :precision="1"
                controls-position="right"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源">
              <el-select v-model="addForm.sourceChannel" style="width: 100%">
                <el-option
                  v-for="o in SOURCE_CHANNELS.filter((x) => [3, 4, 5].includes(x.value))"
                  :key="o.value"
                  :label="o.label"
                  :value="o.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="扣账户余额">
              <el-switch
                v-model="addForm.isLedgerAffecting"
                :active-value="1"
                :inactive-value="0"
                :disabled="addForm.sourceChannel === 4"
              />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注">
              <el-input v-model.trim="addForm.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAdd">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignVisible" title="人工归属" width="480px" :close-on-click-modal="false">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="车辆">
          <el-select v-model="assignForm.vehicleId" clearable filterable style="width: 100%">
            <el-option
              v-for="v in vehicles"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="司机">
          <el-select v-model="assignForm.driverId" clearable filterable style="width: 100%">
            <el-option v-for="d in drivers" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="能源账户">
          <el-select v-model="assignForm.accountId" clearable filterable style="width: 100%">
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="a.accountName"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveAssign">确认归属</el-button>
      </template>
    </el-dialog>
  </ele-page>
</template>

<script lang="ts" setup>
  import { onMounted, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { addConsumption, assignConsumption, pageConsumptions } from '@/api/energy';
  import {
    ENERGY_TYPES,
    MATCH_STATUSES,
    SOURCE_CHANNELS,
    asPage,
    labelOf
  } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyConsumption' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const total = ref(0);
  const page = ref(1);
  const keyword = ref('');
  const matchStatus = ref<string>();
  const {
    accounts,
    products,
    vehicles,
    drivers,
    loadAccounts,
    loadProducts,
    loadVehicles,
    loadDrivers
  } = useEnergyLookups();

  const addVisible = ref(false);
  const assignVisible = ref(false);
  const addRef = ref<FormInstance>();
  const addForm = reactive<any>({
    energyType: 'OIL',
    sourceChannel: 3,
    isLedgerAffecting: 1
  });
  const assignForm = reactive<any>({ id: 0 });

  const addRules: FormRules = {
    consumptionTime: [{ required: true, message: '请选择消费时间', trigger: 'change' }],
    amount: [{ required: true, message: '请填写金额', trigger: 'change' }],
    energyType: [{ required: true, message: '请选择能源类型', trigger: 'change' }]
  };

  watch(
    () => addForm.sourceChannel,
    (v) => {
      if (v === 4) addForm.isLedgerAffecting = 0;
    }
  );

  const fetchData = async () => {
    loading.value = true;
    try {
      const res = asPage(
        await pageConsumptions({
          keyword: keyword.value,
          matchStatus: matchStatus.value,
          page: page.value,
          limit: 20
        })
      );
      list.value = res.list;
      total.value = res.count;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载消费流水失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };

  const onVehicleChange = (id?: number) => {
    const v = vehicles.value.find((x) => x.id === id);
    if (v) addForm.plateNumber = v.plateNumber;
  };

  const openAdd = async () => {
    await Promise.all([loadAccounts(), loadProducts(), loadVehicles(), loadDrivers()]);
    Object.assign(addForm, {
      consumptionTime: '',
      amount: undefined,
      quantity: undefined,
      unitPrice: undefined,
      energyType: 'OIL',
      energyProductId: undefined,
      accountId: undefined,
      cardNo: '',
      vehicleId: undefined,
      plateNumber: '',
      driverId: undefined,
      stationName: '',
      mileage: undefined,
      sourceChannel: 3,
      isLedgerAffecting: 1,
      remark: ''
    });
    addVisible.value = true;
  };

  const saveAdd = async () => {
    await addRef.value?.validate();
    const product = products.value.find((p) => p.id === addForm.energyProductId);
    saving.value = true;
    try {
      await addConsumption({
        ...addForm,
        productName: product?.productName,
        unit: product?.standardUnit
      });
      EleMessage.success({ message: '已录入消费', plain: true });
      addVisible.value = false;
      fetchData();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openAssign = async (row: any) => {
    await Promise.all([loadVehicles(), loadDrivers(), loadAccounts()]);
    Object.assign(assignForm, {
      id: row.id,
      vehicleId: undefined,
      driverId: undefined,
      accountId: row.accountId
    });
    assignVisible.value = true;
  };

  const saveAssign = async () => {
    saving.value = true;
    try {
      await assignConsumption(assignForm.id, assignForm);
      EleMessage.success({ message: '已归属', plain: true });
      assignVisible.value = false;
      fetchData();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '归属失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  onMounted(fetchData);
</script>
<style scoped>
  .pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
</style>
