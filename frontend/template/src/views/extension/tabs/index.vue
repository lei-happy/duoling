<template>
  <ele-page>
    <ele-card header="基础用法">
      <option-item label="尺寸">
        <el-radio-group v-model="size" size="large" @change="handleChange">
          <el-radio value="small" label="小型" />
          <el-radio value="default" label="默认" />
          <el-radio value="large" label="大型" />
        </el-radio-group>
      </option-item>
      <option-item label="风格" style="margin: 0">
        <div style="max-width: 220px">
          <el-select v-model="type" class="ele-fluid">
            <el-option label="默认风格" value="default" />
            <el-option label="卡片风格" value="card" />
            <el-option label="边框卡片风格" value="border-card" />
            <el-option label="简约风格" value="simple" />
            <el-option label="指示器风格" value="indicator" />
            <el-option label="按钮风格" value="button" />
            <el-option label="标签风格" value="tag" />
          </el-select>
        </div>
      </option-item>
      <ele-tabs
        ref="tabRef"
        :items="items"
        v-model="active"
        :size="size"
        :type="type"
        :mousewheel="true"
        style="margin-top: 24px"
        :class="{ 'demo-card-button': type === 'button' }"
      >
        <template #user>
          <div style="padding: 20px 0">User</div>
        </template>
        <template #role>
          <div style="padding: 20px 0">Role</div>
        </template>
        <template #organization>
          <div style="padding: 20px 0">Organization</div>
        </template>
        <template #menu>
          <div style="padding: 20px 0">Menu</div>
        </template>
      </ele-tabs>
    </ele-card>
    <ele-card header="右键菜单和拖动排序">
      <ele-tabs
        :items="items"
        v-model="active"
        type="border-card"
        :context-menu="true"
        :context-menus="[
          { title: '关闭当前', command: 'close' },
          { title: '关闭左侧', command: 'left' },
          { title: '关闭右侧', command: 'right' },
          { title: '关闭其他', command: 'other' }
        ]"
        :sortable="true"
      >
        <template #user>
          <div style="padding: 20px 0">User</div>
        </template>
        <template #role>
          <div style="padding: 20px 0">Role</div>
        </template>
        <template #organization>
          <div style="padding: 20px 0">Organization</div>
        </template>
        <template #menu>
          <div style="padding: 20px 0">Menu</div>
        </template>
      </ele-tabs>
    </ele-card>
    <ele-card header="组合使用">
      <ele-card
        bordered
        :header-style="{ padding: '0 16px' }"
        style="max-width: 600px"
      >
        <template #header>
          <ele-tabs
            :items="[
              { name: 'new', label: '最新' },
              { name: 'hot', label: '热门' }
            ]"
            v-model="active2"
            type="plain"
            size="large"
          />
        </template>
        <template #extra>
          <el-link type="primary" underline="never">查看全部</el-link>
        </template>
        <div v-if="active2 === 'new'">New</div>
        <div v-if="active2 === 'hot'">Hot</div>
      </ele-card>
    </ele-card>
    <ele-card header="自定义风格" :body-style="{ paddingTop: '6px' }">
      <div style="max-width: 480px; min-height: 224px">
        <ele-tabs
          :items="[
            { name: 'new', label: '最新动态' },
            { name: 'hot', label: '热门时讯' },
            { name: 'subject', label: '专题推荐' }
          ]"
          v-model="active3"
          type="simple"
          class="demo-tabs"
        >
          <template #new>
            <demo-list :type="0" />
          </template>
          <template #hot>
            <demo-list :type="1" />
          </template>
          <template #subject>
            <demo-list :type="2" />
          </template>
        </ele-tabs>
      </div>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type { EleTabs } from 'ele-admin-plus';
  import type { TabSize, TabType } from 'ele-admin-plus/es/ele-tabs/types';
  import OptionItem from '@/views/extension/avatar/components/option-item.vue';
  import DemoList from './components/demo-list.vue';

  defineOptions({ name: 'ExtensionTabs' });

  /** 组件实例 */
  const tabRef = ref<InstanceType<typeof EleTabs> | null>(null);

  /** 选中 */
  const active = ref('user');

  /** 标签页数据 */
  const items = ref([
    {
      name: 'user',
      label: '用户管理'
    },
    {
      name: 'role',
      label: '角色管理'
    },
    {
      name: 'organization',
      label: '机构管理',
      closable: true
    },
    {
      name: 'menu',
      label: '菜单管理',
      closable: true
    }
  ]);

  /** 尺寸 */
  const size = ref<TabSize>('default');

  /** 风格 */
  const type = ref<TabType>('default');

  /** 选中 */
  const active2 = ref('new');

  /** 选中 */
  const active3 = ref('new');

  const handleChange = () => {
    tabRef.value?.updateActiveBar?.();
  };
</script>

<style lang="scss" scoped>
  /* 按钮风格增加灰色背景 */
  .demo-card-button :deep(.el-tabs__header) {
    background: hsla(216deg, 8%, 50%, 0.08);
    box-shadow: -8px 0 0 0 hsla(216deg, 8%, 50%, 0.08);
  }

  /* 自定义样式 */
  div.demo-tabs.ele-tabs :deep(.el-tabs__header) {
    --ele-tab-padding: 0;
    --ele-tab-height: 46px;
    --ele-tab-font-size: 16px;
    --ele-tab-simple-hover-color: var(--el-color-primary);
    --ele-tab-simple-hover-bg: none;
    --ele-tab-simple-active-bg: none;
    --ele-tab-simple-active-weight: normal;

    .el-tabs__item {
      & + .el-tabs__item {
        margin-left: 40px;
      }

      &.is-active::after {
        height: 3px;
        width: 20px !important;
        left: 50%;
        transform: translateX(-50%);
        display: block;
      }

      .ele-tab-corner-left,
      .ele-tab-corner-right {
        display: none;
      }
    }
  }
</style>
