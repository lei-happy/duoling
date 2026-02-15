<template>
  <ele-page :multi-card="false">
    <ele-card>
      <div style="margin-bottom: 16px">
        <el-button
          :icon="ArrowLeftOutlined"
          type="primary"
          class="ele-btn-icon"
          @click="handleBack"
        >
          返回列表
        </el-button>
      </div>
      <el-descriptions
        :border="true"
        :column="mobile ? 1 : 2"
        class="detail-table"
      >
        <el-descriptions-item label="用户名">
          <div>{{ form.nickname }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="头像">
          <div style="display: flex">
            <el-avatar v-if="form.avatar" :src="form.avatar" :size="32" />
            <el-avatar
              v-else
              style="background: var(--el-color-primary)"
              :size="32"
            >
              {{
                form.nickname && form.nickname.length > 2
                  ? form.nickname.substring(form.nickname.length - 2)
                  : form.nickname
              }}
            </el-avatar>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="用户账号">
          <div>{{ form.username }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="性别">
          <div>{{ form.sexName }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="手机号">
          <div>{{ form.phone }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag
            v-for="item in form.roles"
            :key="item.roleId"
            size="small"
            :disable-transitions="true"
          >
            {{ item.roleName }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <ele-dot v-if="form.status === 0" text="正常" size="9px" />
          <ele-dot
            v-else-if="form.status === 1"
            text="冻结"
            type="danger"
            :ripple="false"
            size="9px"
          />
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          <div>{{ form.createTime }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { EleMessage } from 'ele-admin-plus';
  import { ArrowLeftOutlined } from '@/components/icons';
  import { useMobile } from '@/utils/use-mobile';
  import { usePageTab } from '@/utils/use-page-tab';
  import { getUser } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  defineOptions({ name: 'SystemUserDetails' });

  const route = useRoute();
  const { push } = useRouter();
  const { routeTabKey, removePageTab, setPageTabTitle } = usePageTab();
  const { mobile } = useMobile();

  /** 用户信息 */
  const form = reactive<User>({
    userId: Number(route.params.id),
    avatar: void 0,
    username: '',
    nickname: '',
    sexName: '',
    phone: '',
    roles: [],
    createTime: void 0,
    status: void 0
  });

  /** 请求状态 */
  const loading = ref(true);

  /** 返回 */
  const handleBack = () => {
    removePageTab({ key: routeTabKey });
    push('/system/user');
  };

  /** 查询详情 */
  const query = () => {
    if (!form.userId || isNaN(form.userId)) {
      return;
    }
    loading.value = true;
    getUser(form.userId)
      .then((data) => {
        loading.value = false;
        Object.assign(form, data);
        // 修改页签标题
        setPageTabTitle(`用户详情[${form.nickname}]`);
      })
      .catch((e) => {
        loading.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  query();
</script>

<style lang="scss" scoped>
  .detail-table :deep(.el-descriptions__table) {
    table-layout: fixed;

    td.el-descriptions__label.el-descriptions__cell {
      width: 108px;
      text-align: right;
      font-weight: normal;
    }
  }
</style>
