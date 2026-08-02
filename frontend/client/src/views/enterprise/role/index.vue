<template>
  <ele-page>
    <role-search @search="onSearch" />
    <ele-card :body-style="{ paddingTop: '8px' }">
      <div class="role-gallery-toolbar">
        <btn-items :items="[{ preset: 'add', onClick: () => openEdit() }]" />
      </div>

      <div v-loading="loading" class="role-gallery-body">
        <div v-if="list.length" class="role-card-grid">
          <role-card
            v-for="item in list"
            :key="item.roleId"
            :data="item"
            @auth="openAuth(item)"
            @edit="openEdit(item)"
            @delete="remove(item)"
            @view-users="openUsers(item)"
          />
          <button
            type="button"
            class="role-card-create"
            @click="openEdit()"
          >
            <span class="role-card-create__plus">+</span>
            <span>新建角色</span>
          </button>
        </div>
        <el-empty v-else-if="!loading" description="还没有角色，先新建一个吧">
          <btn-items
            :items="[
              { preset: 'add', title: '新建角色', onClick: () => openEdit() }
            ]"
          />
        </el-empty>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { ElMessageBox } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import RoleSearch from './components/role-search.vue';
  import RoleCard from './components/role-card.vue';
  import { listRoles, removeRole } from '@/api/system/role';
  import type { Role, RoleParam } from '@/api/system/role/model';

  defineOptions({ name: 'SystemRole' });

  const { openModal } = useModal();

  const loading = ref(false);
  const list = ref<Role[]>([]);
  const queryWhere = ref<RoleParam>({});

  const loadData = async () => {
    loading.value = true;
    try {
      list.value = await listRoles({ ...queryWhere.value });
    } catch (e: any) {
      list.value = [];
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  };

  const reload = () => {
    loadData();
  };

  const onSearch = (where?: RoleParam) => {
    queryWhere.value = { ...(where || {}) };
    loadData();
  };

  /** 打开编辑弹窗 */
  const openEdit = (row?: Role) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/role-edit.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 打开权限分配弹窗 */
  const openAuth = (row?: Role) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/role-auth.vue'),
      componentProps: { data: row, onDone: () => reload() }
    });
  };

  /** 查看角色关联人员 */
  const openUsers = (row: Role) => {
    openModal({
      custom: true,
      asyncComponent: () => import('./components/role-users.vue'),
      componentProps: { data: row }
    });
  };

  /** 删除 */
  const remove = (row: Role) => {
    ElMessageBox.confirm(`确定要删除「${row.roleName}」吗？`, '系统提示', {
      type: 'warning',
      draggable: true
    })
      .then(() => {
        const loadingMsg = EleMessage.loading({
          message: '正在删除角色，请稍候…',
          plain: true
        });
        removeRole(row.roleId)
          .then((msg) => {
            loadingMsg.close();
            EleMessage.success({ message: msg, plain: true });
            reload();
          })
          .catch((e) => {
            loadingMsg.close();
            EleMessage.error({ message: e.message, plain: true });
          });
      })
      .catch(() => {});
  };

  onMounted(() => {
    loadData();
  });
</script>

<style scoped>
  .role-gallery-toolbar {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
  }

  .role-gallery-body {
    min-height: 200px;
  }

  .role-card-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }

  @media (max-width: 1400px) {
    .role-card-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
  }

  @media (max-width: 992px) {
    .role-card-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 640px) {
    .role-card-grid {
      grid-template-columns: 1fr;
    }
  }

  .role-card-create {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 180px;
    margin: 0;
    padding: 16px;
    border: 1px dashed var(--el-border-color);
    border-radius: 8px;
    background: transparent;
    color: var(--el-text-color-secondary);
    font: inherit;
    font-size: 14px;
    cursor: pointer;
    transition:
      border-color 0.15s ease,
      color 0.15s ease,
      background-color 0.15s ease;
  }

  .role-card-create:hover {
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }

  .role-card-create__plus {
    font-size: 28px;
    line-height: 1;
    font-weight: 300;
  }
</style>
