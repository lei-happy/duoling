<!-- 结算账户子表 -->
<template>
  <div>
    <div class="settlement-table-header">
      <span class="title">结算账户</span>
      <el-button type="primary" size="small" @click="openAdd">
        新增结算账户
      </el-button>
    </div>
    <el-table
      :data="rows"
      border
      stripe
      size="small"
      style="width: 100%"
      :empty-text="canPersist ? '暂无结算账户' : '保存承运商基础信息后再添加结算账户'"
    >
      <el-table-column type="index" label="#" width="50" align="center" />
      <el-table-column prop="accountLabel" label="账户标签" min-width="160" />
      <el-table-column label="结算方式" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small" :disable-transitions="true">
            {{ SETTLEMENT_TYPE_TEXT[row.settlementType] || row.settlementType }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="bankAccountName" label="户名" min-width="120" />
      <el-table-column prop="bankAccount" label="银行账号" min-width="160" />
      <el-table-column prop="bankName" label="开户行" min-width="160" />
      <el-table-column label="默认" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isDefault === 1" type="warning" size="small">
            默认
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.status === 1 ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.status === 1 ? '正常' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row, $index }">
          <el-button
            v-if="canPersist && row.id && row.isDefault !== 1"
            link
            type="primary"
            size="small"
            @click="setDefault(row)"
          >
            设为默认
          </el-button>
          <el-button
            link
            type="primary"
            size="small"
            @click="openEdit(row, $index)"
          >
            编辑
          </el-button>
          <el-popconfirm
            title="确认删除该结算账户？"
            @confirm="remove(row, $index)"
          >
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <carrier-settlement-edit
      v-model:visible="editVisible"
      :data="editData"
      @submit="onEditSubmit"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import {
    addSettlement,
    updateSettlement,
    setDefaultSettlement,
    removeSettlement
  } from '@/api/partner/carrier';
  import {
    SETTLEMENT_TYPE_TEXT,
    type CarrierSettlement
  } from '@/api/partner/carrier/model';
  import CarrierSettlementEdit from './carrier-settlement-edit.vue';

  const props = defineProps<{
    carrierId?: number | null;
    modelValue: CarrierSettlement[];
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value: CarrierSettlement[]): void;
  }>();

  const rows = computed({
    get: () => props.modelValue,
    set: (v) => emit('update:modelValue', v)
  });

  const canPersist = computed(() => !!props.carrierId);

  const editVisible = ref(false);
  const editData = ref<CarrierSettlement | null>(null);
  const editIndex = ref<number>(-1);

  const openAdd = () => {
    editData.value = null;
    editIndex.value = -1;
    editVisible.value = true;
  };

  const openEdit = (row: CarrierSettlement, idx: number) => {
    editData.value = { ...row };
    editIndex.value = idx;
    editVisible.value = true;
  };

  const onEditSubmit = async (payload: CarrierSettlement) => {
    if (!canPersist.value) {
      // 草稿态：仅在前端 list 中维护
      const newList = [...rows.value];
      // 默认互斥
      if (payload.isDefault === 1) {
        newList.forEach((r) => (r.isDefault = 0));
      }
      if (editIndex.value >= 0) {
        newList.splice(editIndex.value, 1, { ...newList[editIndex.value], ...payload });
      } else {
        newList.push(payload);
      }
      rows.value = newList;
      return;
    }

    try {
      let saved: CarrierSettlement | undefined;
      if (payload.id) {
        saved = (await updateSettlement(props.carrierId!, payload)) ?? undefined;
      } else {
        saved = (await addSettlement(props.carrierId!, payload)) ?? undefined;
      }
      if (saved) {
        const newList = [...rows.value];
        // 默认互斥同步
        if (saved.isDefault === 1) {
          newList.forEach((r) => (r.isDefault = 0));
        }
        if (editIndex.value >= 0) {
          newList.splice(editIndex.value, 1, saved);
        } else {
          newList.push(saved);
        }
        rows.value = newList;
      }
      EleMessage.success({ message: '保存成功', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const setDefault = async (row: CarrierSettlement) => {
    if (!canPersist.value || !row.id) return;
    try {
      const updated = await setDefaultSettlement(props.carrierId!, row.id);
      const newList = rows.value.map((r) => ({ ...r, isDefault: 0 }));
      const idx = newList.findIndex((r) => r.id === row.id);
      if (idx >= 0 && updated) {
        newList.splice(idx, 1, updated);
      }
      rows.value = newList;
      EleMessage.success({ message: '已设为默认', plain: true });
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  const remove = async (row: CarrierSettlement, idx: number) => {
    if (canPersist.value && row.id) {
      try {
        await removeSettlement(props.carrierId!, row.id);
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
        return;
      }
    }
    const newList = [...rows.value];
    newList.splice(idx, 1);
    rows.value = newList;
    EleMessage.success({ message: '删除成功', plain: true });
  };
</script>

<style scoped>
  .settlement-table-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .settlement-table-header .title {
    font-size: 14px;
    font-weight: 600;
  }
</style>
