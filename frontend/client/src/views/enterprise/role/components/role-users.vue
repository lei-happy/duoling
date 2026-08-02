<!-- 角色关联人员弹窗 -->
<template>
  <ele-modal
    :width="640"
    :title="modalTitle"
    position="center"
    :body-style="{ paddingTop: '8px', minHeight: '160px' }"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-table
      v-if="users.length"
      :data="users"
      row-key="userId"
      size="small"
      max-height="420"
      stripe
    >
      <el-table-column prop="nickname" label="姓名" min-width="100">
        <template #default="{ row }">
          {{ row.nickname || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" min-width="120" />
      <el-table-column
        prop="organizationName"
        label="所属机构"
        min-width="140"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          {{ row.organizationName || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag
            size="small"
            :type="row.status === 0 ? 'success' : 'info'"
            :disable-transitions="true"
          >
            {{ row.status === 0 ? '正常' : '冻结' }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
    <el-empty
      v-else-if="!loading"
      description="暂无人员使用该角色"
      :image-size="72"
    />
    <template #footer>
      <btn-items
        :items="[{ preset: 'cancel', title: '关闭', onClick: () => closeModal() }]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, computed } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { listRoleUsers } from '@/api/system/role';
  import type { Role } from '@/api/system/role/model';
  import type { User } from '@/api/system/user/model';

  const props = defineProps<{
    data?: Role | null;
  }>();

  const { modalProps, closeModal } = useModal();

  const loading = ref(false);
  const users = ref<User[]>([]);

  const modalTitle = computed(() => {
    const name = props.data?.roleName?.trim();
    return name ? `「${name}」的人员` : '角色人员';
  });

  const load = () => {
    if (!props.data?.roleId) {
      return;
    }
    loading.value = true;
    listRoleUsers(props.data.roleId)
      .then((list) => {
        users.value = list || [];
      })
      .catch((e) => {
        users.value = [];
        EleMessage.error({ message: e.message, plain: true });
      })
      .finally(() => {
        loading.value = false;
      });
  };

  load();
</script>
