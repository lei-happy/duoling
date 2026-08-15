<template>
  <ele-page>
    <ele-card :body-style="{ paddingBottom: 0 }">
      <el-form :inline="true" @submit.prevent="">
        <el-form-item label="卡号">
          <el-input
            v-model="keyword"
            placeholder="卡号"
            clearable
            style="width: 180px"
            @keyup.enter="reload(1)"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="reload(1)">查询</el-button>
          <el-button type="primary" @click="openEdit()">新增能源卡</el-button>
        </el-form-item>
      </el-form>
    </ele-card>
    <ele-card>
      <el-table :data="list" v-loading="loading" border>
        <el-table-column prop="cardNo" label="卡号" min-width="160" />
        <el-table-column prop="accountName" label="所属账户" min-width="140" />
        <el-table-column label="能源" width="80">
          <template #default="{ row }">
            {{ labelOf(ENERGY_TYPES, row.energyType) }}
          </template>
        </el-table-column>
        <el-table-column prop="cardType" label="卡类型" width="100" />
        <el-table-column label="当前绑定" min-width="160">
          <template #default="{ row }">
            {{ bindText(row) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            {{ labelOf(CARD_STATUSES, row.status) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="openBind(row)">绑定</el-button>
            <el-button link type="primary" @click="doUnbind(row)">解绑</el-button>
            <el-button link type="danger" @click="doRemove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination
          :current-page="page"
          :page-size="limit"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="(p: number) => { page = p; fetchData(); }"
        />
      </div>
    </ele-card>

    <el-dialog
      v-model="editVisible"
      :title="form.id ? '编辑能源卡' : '新增能源卡'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px">
        <el-form-item label="所属账户" prop="accountId">
          <el-select
            v-model="form.accountId"
            filterable
            style="width: 100%"
            :disabled="!!form.id"
          >
            <el-option
              v-for="a in accounts"
              :key="a.id"
              :label="`${a.accountName}（${a.accountCode}）`"
              :value="a.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="卡号" prop="cardNo">
          <el-input v-model.trim="form.cardNo" :disabled="!!form.id" placeholder="实体卡或虚拟卡号" />
        </el-form-item>
        <el-form-item label="卡类型">
          <el-select v-model="form.cardType" clearable style="width: 100%">
            <el-option v-for="o in CARD_TYPES" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="能源类型">
          <el-select v-model="form.energyType" clearable style="width: 100%">
            <el-option v-for="o in ENERGY_TYPES" :key="o.value" :label="o.label" :value="o.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.id" label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option
              v-for="o in CARD_STATUSES"
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

    <el-dialog v-model="bindVisible" title="绑定车辆 / 司机" width="480px" :close-on-click-modal="false">
      <el-alert
        type="info"
        :closable="false"
        title="绑定会记下开始时间。以后改绑不会覆盖历史，三个月前的消费仍能还原当时绑的是谁。"
        style="margin-bottom: 16px"
      />
      <el-form :model="bindForm" label-width="80px">
        <el-form-item label="车辆">
          <el-select v-model="bindForm.vehicleId" filterable clearable style="width: 100%">
            <el-option
              v-for="v in vehicles"
              :key="v.id"
              :label="v.plateNumber"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="司机">
          <el-select v-model="bindForm.driverId" filterable clearable style="width: 100%">
            <el-option
              v-for="d in drivers"
              :key="d.id"
              :label="`${d.name || '未命名'}${d.phone ? ' · ' + d.phone : ''}`"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveBind">确认绑定</el-button>
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
    addCard,
    bindCard,
    pageCards,
    removeCard,
    unbindCard,
    updateCard
  } from '@/api/energy';
  import {
    CARD_STATUSES,
    CARD_TYPES,
    ENERGY_TYPES,
    asPage,
    labelOf
  } from '../_shared/options';
  import { useEnergyLookups } from '../_shared/use-lookups';

  defineOptions({ name: 'EnergyCard' });

  const loading = ref(false);
  const saving = ref(false);
  const list = ref<any[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(20);
  const keyword = ref('');
  const { accounts, vehicles, drivers, loadAccounts, loadVehicles, loadDrivers } =
    useEnergyLookups();

  const editVisible = ref(false);
  const bindVisible = ref(false);
  const formRef = ref<FormInstance>();
  const form = reactive<any>({});
  const bindForm = reactive<any>({ cardId: 0 });

  const rules: FormRules = {
    accountId: [{ required: true, message: '请选择所属账户', trigger: 'change' }],
    cardNo: [{ required: true, message: '请填写卡号', trigger: 'blur' }]
  };

  const bindText = (row: any) => {
    const parts = [];
    const plate = vehicles.value.find((v) => v.id === row.vehicleId)?.plateNumber;
    const driver = drivers.value.find((d) => d.id === row.driverId);
    if (row.vehicleId) parts.push(plate || `车辆 ${row.vehicleId}`);
    if (row.driverId) parts.push(driver?.name || `司机 ${row.driverId}`);
    return parts.join(' / ') || '未绑定';
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      const res = asPage(
        await pageCards({ keyword: keyword.value, page: page.value, limit: limit.value })
      );
      list.value = res.list;
      total.value = res.count;
    } catch (e: any) {
      EleMessage.error({ message: e.message || '加载能源卡失败，请重试', plain: true });
    } finally {
      loading.value = false;
    }
  };
  const reload = (p?: number) => {
    if (p) page.value = p;
    fetchData();
  };

  const openEdit = (row?: any) => {
    Object.assign(form, {
      id: row?.id,
      accountId: row?.accountId,
      cardNo: row?.cardNo || '',
      cardType: row?.cardType || '实体卡',
      energyType: row?.energyType || 'OIL',
      status: row?.status ?? 1,
      remark: row?.remark || ''
    });
    editVisible.value = true;
  };

  const save = async () => {
    await formRef.value?.validate();
    saving.value = true;
    try {
      if (form.id) await updateCard(form.id, form);
      else await addCard(form);
      EleMessage.success({ message: form.id ? '已保存能源卡' : '已新增能源卡', plain: true });
      editVisible.value = false;
      reload();
    } catch (e: any) {
      if (e?.message) EleMessage.error({ message: e.message, plain: true });
    } finally {
      saving.value = false;
    }
  };

  const openBind = async (row: any) => {
    Object.assign(bindForm, {
      cardId: row.id,
      vehicleId: row.vehicleId,
      driverId: row.driverId
    });
    await Promise.all([loadVehicles(), loadDrivers()]);
    bindVisible.value = true;
  };

  const saveBind = async () => {
    if (!bindForm.vehicleId && !bindForm.driverId) {
      EleMessage.error({ message: '请至少选择车辆或司机', plain: true });
      return;
    }
    saving.value = true;
    try {
      await bindCard(bindForm.cardId, {
        vehicleId: bindForm.vehicleId,
        driverId: bindForm.driverId
      });
      EleMessage.success({ message: '已绑定', plain: true });
      bindVisible.value = false;
      reload();
    } catch (e: any) {
      EleMessage.error({ message: e.message || '绑定失败，请重试', plain: true });
    } finally {
      saving.value = false;
    }
  };

  const doUnbind = (row: any) => {
    ElMessageBox.confirm('解绑后这张卡不再对应当前车辆/司机，历史绑定会保留。', '解绑确认', {
      type: 'warning'
    }).then(async () => {
      await unbindCard(row.id);
      EleMessage.success({ message: '已解绑', plain: true });
      reload();
    });
  };

  const doRemove = (row: any) => {
    ElMessageBox.confirm(`确定删除卡「${row.cardNo}」？`, '删除确认', {
      type: 'warning'
    }).then(async () => {
      await removeCard(row.id);
      EleMessage.success({ message: '已删除', plain: true });
      reload();
    });
  };

  onMounted(async () => {
    await Promise.all([loadAccounts(), loadVehicles(), loadDrivers()]);
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
