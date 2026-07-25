<template>
  <el-drawer
    :title="`成员管理 · ${group?.groupName ?? ''}`"
    :model-value="visible"
    size="720px"
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
  >
    <div class="member-toolbar">
      <floating-label
        class="member-search"
        label="搜索司机姓名/手机号/车牌"
        type="input"
        v-model.trim="keyword"
        clearable
        @keyup.enter="reloadMembers"
      />
      <div class="member-toolbar__btns">
        <el-button @click="reloadMembers">查询</el-button>
        <el-button
          type="danger"
          plain
          :disabled="!selection.length"
          @click="batchRemove"
        >
          批量移出
        </el-button>
        <el-button type="primary" @click="openPicker">添加成员</el-button>
      </div>
    </div>

    <el-table
      ref="tableRef"
      :data="members"
      row-key="id"
      height="calc(100vh - 220px)"
      v-loading="loading"
      @selection-change="onSelectionChange"
    >
      <el-table-column type="selection" width="46" />
      <el-table-column label="司机" min-width="120">
        <template #default="{ row }">
          <div class="member-driver">
            <span>{{ row.driverName }}</span>
            <span class="member-driver__phone">{{
              row.driverPhone || '—'
            }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="当前车牌" min-width="130" align="center">
        <template #default="{ row }">
          <plate-number-tag v-if="row.plateNumber" :text="row.plateNumber" />
          <span v-else style="color: #999">未在运力中</span>
        </template>
      </el-table-column>
      <el-table-column label="在运力" width="90" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.bound ? 'success' : 'info'"
            size="small"
            :disable-transitions="true"
          >
            {{ row.bound ? '绑定中' : '已下车' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center">
        <template #default="{ row }">
          <el-button link type="danger" @click="removeOne(row)">移出</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="member-pager">
      <el-pagination
        layout="total, prev, pager, next"
        :total="total"
        :current-page="page"
        :page-size="limit"
        @current-change="onPageChange"
      />
    </div>

    <!-- 添加成员：从绑定中的运力多选 -->
    <el-dialog
      title="从运力添加成员"
      v-model="pickerVisible"
      width="640px"
      append-to-body
      :close-on-click-modal="false"
    >
      <div class="picker-toolbar">
        <floating-label
          label="搜索司机姓名/手机号/车牌"
          type="input"
          v-model.trim="pickerKeyword"
          clearable
          @keyup.enter="reloadPicker"
        />
        <el-button @click="reloadPicker">查询</el-button>
      </div>
      <el-table
        :data="capacities"
        row-key="id"
        height="380px"
        v-loading="pickerLoading"
        @selection-change="onPickerSelectionChange"
      >
        <el-table-column type="selection" width="46" />
        <el-table-column label="司机" min-width="120">
          <template #default="{ row }">
            <div class="member-driver">
              <span>{{ row.driverName }}</span>
              <span class="member-driver__phone">{{ row.driverPhone }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="车牌" min-width="130" align="center">
          <template #default="{ row }">
            <plate-number-tag :text="row.plateNumber" />
          </template>
        </el-table-column>
      </el-table>
      <div class="member-pager">
        <el-pagination
          layout="total, prev, pager, next"
          :total="pickerTotal"
          :current-page="pickerPage"
          :page-size="pickerLimit"
          @current-change="onPickerPageChange"
        />
      </div>
      <template #footer>
        <el-button @click="pickerVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="adding"
          :disabled="!pickerSelection.length"
          @click="confirmAdd"
        >
          添加 {{ pickerSelection.length ? `(${pickerSelection.length})` : '' }}
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import PlateNumberTag from '@/components/PlateNumberTag/index.vue';
  import {
    pageGroupMembers,
    addGroupMembers,
    removeGroupMembers
  } from '@/api/capacity/self-capacity/group';
  import type {
    CapacityGroup,
    CapacityGroupMember
  } from '@/api/capacity/self-capacity/group/model';
  import { pageCapacities } from '@/api/capacity/self-capacity/list';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';

  const props = defineProps<{
    visible: boolean;
    group: CapacityGroup | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'changed'): void;
  }>();

  const loading = ref(false);
  const members = ref<CapacityGroupMember[]>([]);
  const total = ref(0);
  const page = ref(1);
  const limit = ref(10);
  const keyword = ref('');
  const selection = ref<CapacityGroupMember[]>([]);

  const loadMembers = async () => {
    if (!props.group?.id) return;
    loading.value = true;
    try {
      const res = await pageGroupMembers(props.group.id, {
        keyword: keyword.value,
        page: page.value,
        limit: limit.value
      });
      const raw = res as {
        list?: CapacityGroupMember[];
        count?: number;
        total?: number;
      };
      members.value = raw?.list ?? [];
      total.value = raw?.count ?? raw?.total ?? 0;
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const reloadMembers = () => {
    page.value = 1;
    loadMembers();
  };

  const onPageChange = (p: number) => {
    page.value = p;
    loadMembers();
  };

  const onSelectionChange = (rows: CapacityGroupMember[]) => {
    selection.value = rows;
  };

  const removeOne = (row: CapacityGroupMember) => {
    ElMessageBox.confirm(
      `确定把司机「${row.driverName}」移出该分组吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => doRemove({ memberIds: [row.id] }))
      .catch(() => {});
  };

  const batchRemove = () => {
    if (!selection.value.length) return;
    ElMessageBox.confirm(
      `确定把选中的 ${selection.value.length} 位成员移出该分组吗？`,
      '系统提示',
      { type: 'warning', draggable: true }
    )
      .then(() => doRemove({ memberIds: selection.value.map((m) => m.id) }))
      .catch(() => {});
  };

  const doRemove = async (payload: {
    memberIds?: number[];
    driverIds?: number[];
  }) => {
    if (!props.group?.id) return;
    try {
      const msg = await removeGroupMembers(props.group.id, payload);
      EleMessage.success({ message: msg, plain: true });
      selection.value = [];
      reloadMembers();
      emit('changed');
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    }
  };

  // ---------- 添加成员 picker ----------
  const pickerVisible = ref(false);
  const pickerLoading = ref(false);
  const capacities = ref<Capacity[]>([]);
  const pickerTotal = ref(0);
  const pickerPage = ref(1);
  const pickerLimit = ref(10);
  const pickerKeyword = ref('');
  const pickerSelection = ref<Capacity[]>([]);
  const adding = ref(false);

  const openPicker = () => {
    pickerKeyword.value = '';
    pickerSelection.value = [];
    pickerPage.value = 1;
    pickerVisible.value = true;
    loadPicker();
  };

  const loadPicker = async () => {
    pickerLoading.value = true;
    try {
      const res = await pageCapacities({
        keyword: pickerKeyword.value,
        page: pickerPage.value,
        limit: pickerLimit.value
      });
      const raw = res as { list?: Capacity[]; count?: number; total?: number };
      capacities.value = raw?.list ?? [];
      pickerTotal.value = raw?.count ?? raw?.total ?? 0;
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      pickerLoading.value = false;
    }
  };

  const reloadPicker = () => {
    pickerPage.value = 1;
    loadPicker();
  };

  const onPickerPageChange = (p: number) => {
    pickerPage.value = p;
    loadPicker();
  };

  const onPickerSelectionChange = (rows: Capacity[]) => {
    pickerSelection.value = rows;
  };

  const confirmAdd = async () => {
    if (!props.group?.id || !pickerSelection.value.length) return;
    adding.value = true;
    try {
      const ids = pickerSelection.value
        .map((c) => c.id)
        .filter((id): id is number => id != null);
      const msg = await addGroupMembers(props.group.id, ids);
      EleMessage.success({ message: msg, plain: true });
      pickerVisible.value = false;
      reloadMembers();
      emit('changed');
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      adding.value = false;
    }
  };

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        keyword.value = '';
        selection.value = [];
        page.value = 1;
        loadMembers();
      }
    }
  );
</script>

<style scoped>
  .member-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }
  .member-search {
    flex: 1;
    min-width: 0;
  }
  .member-toolbar__btns {
    display: flex;
    gap: 8px;
    flex-shrink: 0;
  }
  .member-driver {
    display: flex;
    flex-direction: column;
    line-height: 1.35;
  }
  .member-driver__phone {
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
  .member-pager {
    display: flex;
    justify-content: flex-end;
    margin-top: 12px;
  }
  .picker-toolbar {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }
  .picker-toolbar .floating-label-wrapper {
    flex: 1;
  }
</style>
