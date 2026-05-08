<!-- 承运商邀请历史抽屉 -->
<template>
  <el-drawer
    :title="`邀请历史 - ${data?.carrierName ?? ''}`"
    :model-value="visible"
    direction="rtl"
    size="640px"
    @update:model-value="updateVisible"
  >
    <el-table
      :data="rows"
      border
      stripe
      size="small"
      v-loading="loading"
      empty-text="暂无邀请记录"
    >
      <el-table-column type="index" label="#" width="50" align="center" />
      <el-table-column prop="invitePhone" label="被邀手机号" width="120" />
      <el-table-column label="渠道" width="80" align="center">
        <template #default="{ row }">
          {{ row.inviteChannel === 'sms' ? '短信' : row.inviteChannel }}
        </template>
      </el-table-column>
      <el-table-column label="路径" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.invitePath }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag
            size="small"
            :type="statusTagType(row.status)"
            :disable-transitions="true"
          >
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发起时间" width="160" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.invitedAt) }}
        </template>
      </el-table-column>
      <el-table-column label="过期时间" width="160" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.expiresAt) }}
        </template>
      </el-table-column>
    </el-table>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { listCarrierInvitations } from '@/api/partner/carrier';
  import type {
    CarrierInvitation,
    Carrier,
    CarrierListItem
  } from '@/api/partner/carrier/model';
  import { formatDateTime } from '@/utils/date-util';

  const props = defineProps<{
    visible: boolean;
    data: Carrier | CarrierListItem | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
  }>();

  const rows = ref<CarrierInvitation[]>([]);
  const loading = ref(false);

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  watch(
    () => props.visible,
    async (val) => {
      if (!val || !props.data?.id) {
        rows.value = [];
        return;
      }
      loading.value = true;
      try {
        rows.value = await listCarrierInvitations(props.data.id);
      } finally {
        loading.value = false;
      }
    }
  );

  function statusText(s: number) {
    const map: Record<number, string> = {
      0: '待发送',
      1: '已发送',
      2: '已点击',
      3: '已激活',
      4: '已过期',
      5: 'A 已撤回',
      6: 'B 已拒绝',
      7: '代转交中',
      8: 'A 端预审拒绝'
    };
    return map[s] ?? `未知(${s})`;
  }

  function statusTagType(s: number): any {
    if (s === 3) return 'success';
    if (s === 1 || s === 2) return 'warning';
    if (s === 4 || s === 5 || s === 6 || s === 8) return 'info';
    return 'danger';
  }
</script>
