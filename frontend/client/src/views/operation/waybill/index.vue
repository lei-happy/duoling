<!--
  运单工作台（重构后）
  ====================

  布局：
    1. 顶部 7 张状态卡（待确认 / 待调度 / 调度中 / 运输中 / 待签收 / 已签收 / 已关闭）
       置于「页面背景」之上，与下方"白色卡片"区隔，避免视觉拥挤
    2. 中部 按 pool 配置的筛选栏（仅渲染对应字段）
    3. 下部 按 pool 配置的列表 + 行内动作 + 工具栏（新增 / 批量确认 / 批量导入）

  本组件负责"壳"：
    - KPI 拉取（getWaybillWorkbenchStats）
    - 当前 poolKey 状态
    - 弹层托管：编辑 / 详情 / 商品车明细 / 计算明细

  详细列表交互在 waybill-pool.vue 中维护；筛选条件配置在 waybill-pool-registry.ts。
-->
<template>
  <ele-page>
    <!--
      卡片放在 ele-card 之外（页面背景色上），与下方筛选 + 列表的"白色卡片"
      形成空间区隔，避免视觉上"一坨白"。
    -->
    <waybill-stats-cards
      class="waybill-page__cards"
      :stats="stats"
      :active-card-key="activeKey"
      :pending-confirm-hidden="pendingConfirmHidden"
      @select-card="onSelectCard"
    />

    <waybill-pool
      :key="activeKey"
      :pool-key="activeKey"
      :reload-token="reloadToken"
      :list-show-freight-amount="listShowFreightAmount"
      @sync-stats="loadStats"
      @open-edit="openEdit"
      @open-detail="openDetail"
      @open-cargo-detail="openCargoDetail"
      @open-freight-detail="openFreightDetail"
      @open-import="goImportPage"
    />

    <waybill-edit
      v-model:visible="editVisible"
      :data="editData"
      @done="onEditDone"
    />
    <waybill-cargoes-detail
      v-model:visible="cargoDetailVisible"
      :waybill="cargoDetailWaybill"
    />
    <waybill-freight-detail
      v-model:visible="freightDetailVisible"
      :waybill-id="freightDetailWaybillId"
      @sync-list="reloadAfterMutation"
    />
    <waybill-detail
      v-model:visible="detailVisible"
      :waybill-id="detailWaybillId"
    />
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed, onActivated, onMounted, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { useRouter } from 'vue-router';
  import WaybillStatsCards from './components/waybill-stats-cards.vue';
  import WaybillPool from './components/waybill-pool.vue';
  import WaybillEdit from './components/waybill-edit.vue';
  import WaybillCargoesDetail from './components/waybill-cargoes-detail.vue';
  import WaybillFreightDetail from './components/waybill-freight-detail.vue';
  import WaybillDetail from './components/waybill-detail.vue';
  import { listConfigsByGroup } from '@/api/system/config';
  import { getWaybillWorkbenchStats } from '@/api/waybill';
  import type { Waybill, WaybillWorkbenchStats } from '@/api/waybill/model';
  import { WAYBILL_POOLS } from './waybill-pool-registry';

  defineOptions({ name: 'Waybill' });

  const router = useRouter();

  /** 默认进入注册表第一项（当前为「待确认」=新单流入口） */
  const activeKey = ref<string>(WAYBILL_POOLS[0]!.key);
  const reloadToken = ref(0);

  // ============================================
  // KPI 卡片统计
  // ============================================
  const stats = ref<WaybillWorkbenchStats | null>(null);

  const loadStats = async () => {
    try {
      stats.value = (await getWaybillWorkbenchStats()) ?? null;
    } catch (e: unknown) {
      const msg = (e as { message?: string }).message;
      if (msg) EleMessage.error({ message: msg, plain: true });
    }
  };

  const onSelectCard = (cardKey: string) => {
    if (cardKey === activeKey.value) return;
    activeKey.value = cardKey;
  };

  // ============================================
  // 系统配置（运单分组）—— 列表运费列、新建自动确认
  // ============================================
  const listShowFreightAmount = ref(false);
  const autoConfirmOnCreate = ref(false);

  /** 开关打开 + 当前待确认运单数为 0 时，隐藏「待确认」状态卡 */
  const pendingConfirmHidden = computed(
    () =>
      autoConfirmOnCreate.value && (stats.value?.totals?.pendingConfirm ?? 0) === 0
  );

  /** 隐藏后若当前激活的是 pending-confirm，自动切到下一张卡（待调度） */
  watch(pendingConfirmHidden, (hidden) => {
    if (hidden && activeKey.value === 'pending-confirm') {
      activeKey.value = 'pending-dispatch';
    }
  });

  const syncWaybillSettings = () => {
    listConfigsByGroup('waybill')
      .then((list) => {
        const showFreight = list?.find(
          (i) => i.configKey === 'waybill.list_show_freight_amount'
        );
        listShowFreightAmount.value = showFreight?.configValue === 'true';
        const autoConfirm = list?.find(
          (i) => i.configKey === 'waybill.auto_confirm_on_create'
        );
        autoConfirmOnCreate.value = autoConfirm?.configValue === 'true';
      })
      .catch(() => {});
  };

  // ============================================
  // 弹层托管
  // ============================================
  const editVisible = ref(false);
  const editData = ref<Waybill | null>(null);
  const cargoDetailVisible = ref(false);
  const cargoDetailWaybill = ref<Waybill | null>(null);
  const freightDetailVisible = ref(false);
  const freightDetailWaybillId = ref<number | null>(null);
  const detailVisible = ref(false);
  const detailWaybillId = ref<number | null>(null);

  const openEdit = (row?: Waybill) => {
    editData.value = row ?? null;
    editVisible.value = true;
  };

  const openDetail = (row: Waybill) => {
    detailWaybillId.value = row.id ?? null;
    detailVisible.value = true;
  };

  const openCargoDetail = (row: Waybill) => {
    cargoDetailWaybill.value = row;
    cargoDetailVisible.value = true;
  };

  const openFreightDetail = (row: Waybill) => {
    if (!row.id) return;
    freightDetailWaybillId.value = row.id;
    freightDetailVisible.value = true;
  };

  const goImportPage = () => {
    router.push('/operation/waybill/import');
  };

  /** 弹层（编辑 / 计算明细）成功后 → 列表 + 卡片同步刷新 */
  const reloadAfterMutation = () => {
    reloadToken.value += 1;
    loadStats();
  };

  const onEditDone = () => {
    reloadAfterMutation();
  };

  // ============================================
  // 初始化
  // ============================================
  const initAll = () => {
    syncWaybillSettings();
    loadStats();
  };

  onMounted(initAll);
  onActivated(initAll);
</script>

<style scoped>
  .waybill-page__cards {
    margin-bottom: 12px;
  }
</style>
