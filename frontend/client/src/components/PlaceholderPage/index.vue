<template>
  <ele-page>
    <ele-card>
      <el-result
        :icon="status"
        :title="title"
        :sub-title="subTitle || defaultSubTitle"
      >
        <template #extra>
          <el-space>
            <el-button type="primary" @click="goBack">返回上一页</el-button>
            <el-button @click="goHome">返回工作台</el-button>
          </el-space>
          <div v-if="featureCode || version" class="placeholder-meta">
            <el-tag
              v-if="featureCode"
              size="small"
              type="info"
              :disable-transitions="true"
            >
              feature_code: {{ featureCode }}
            </el-tag>
            <el-tag
              v-if="version"
              size="small"
              type="warning"
              :disable-transitions="true"
              style="margin-left: 8px"
            >
              所属版本：{{ version }}
            </el-tag>
          </div>
        </template>
      </el-result>
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useRouter } from 'vue-router';

  defineOptions({ name: 'PlaceholderPage' });

  const props = withDefaults(
    defineProps<{
      /** 页面标题（必填，显示在 result 标题位置） */
      title: string;
      /** 副标题，可不传，默认提示"功能开发中" */
      subTitle?: string;
      /** 功能编码，便于在 UI 上关联到 sys_menu.feature_code */
      featureCode?: string;
      /** 所属产品版本，方便排期沟通 */
      version?: string;
      /** result 状态：success | warning | info | error，默认 info */
      status?: 'success' | 'warning' | 'info' | 'error';
    }>(),
    {
      subTitle: '',
      featureCode: '',
      version: '',
      status: 'info'
    }
  );

  const router = useRouter();

  const defaultSubTitle = computed(
    () =>
      `「${props.title}」功能正在规划/开发中，` +
      '上线后将自动启用，敬请期待。'
  );

  const goBack = () => {
    if (window.history.length > 1) {
      router.back();
    } else {
      router.replace('/');
    }
  };

  const goHome = () => {
    router.push('/');
  };
</script>

<style lang="scss" scoped>
  .placeholder-meta {
    margin-top: 16px;
    text-align: center;
  }
</style>
