<template>
  <ele-page>
    <ele-card>
      <div>
        从“男用户”页面和“女用户”页面点击进入的详情页面是共用的同一个页面,
        会选中各自对应的“男用户”或“女用户”菜单, 并且会各自KeepAlive.
      </div>
      <div style="display: flex; align-items: center; margin-top: 16px">
        <div style="padding-right: 16px">路由参数</div>
        <div style="padding-right: 16px">sex: {{ form.sex }}</div>
        <div>userId: {{ form.userId }}</div>
      </div>
      <div style="display: flex; align-items: center; margin-top: 8px">
        <div style="padding-right: 16px">测试KeepAlive</div>
        <div style="flex: 1; max-width: 220px">
          <el-input v-model="text" placeholder="请输入" />
        </div>
      </div>
    </ele-card>
    <ele-card>
      <el-descriptions :border="true" :column="1" class="detail-table">
        <el-descriptions-item label="用户名">
          <div>{{ form.nickname }}</div>
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
        <el-descriptions-item label="创建时间">
          <div>{{ form.createTime }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import { useRoute } from 'vue-router';
  import { usePageTab } from '@/utils/use-page-tab';
  import { getUser } from '@/api/system/user';
  import type { User } from '@/api/system/user/model';

  defineOptions({ name: 'ListUsersDetails' });

  const { setPageTabTitle } = usePageTab();

  const route = useRoute();
  const paths = route.path.split('/');

  /** 用户信息 */
  const form = reactive<User>({
    userId: Number(route.params.id),
    sex: paths[paths.length - 2],
    username: '',
    nickname: '',
    sexName: '',
    phone: '',
    createTime: ''
  });

  /** 查询详情 */
  const query = () => {
    if (!form.userId || isNaN(form.userId)) {
      return;
    }
    getUser(form.userId)
      .then((data) => {
        Object.assign(form, data);
        const sex = form.sex == '1' ? '男' : '女';
        setPageTabTitle(`${sex}用户详情[${form.nickname}]`);
      })
      .catch((e) => {
        console.error(e.message);
      });
  };

  query();

  /** 输入框 */
  const text = ref('');
</script>

<style lang="scss" scoped>
  .detail-table :deep(td.el-descriptions__label.el-descriptions__cell) {
    width: 108px;
    text-align: right;
    font-weight: normal;
  }
</style>
