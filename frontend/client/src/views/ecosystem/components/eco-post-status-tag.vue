<!--
  挂牌状态标签

  「展示中但已过期」是个容易被忽略的组合：状态还是展示中，同行却已经搜不到了。
  用户要靠这个提示去点「延长展示」，所以过期在这里单独打一个标，而不是混在
  「展示中」里。
-->
<template>
  <span class="eco-status">
    <el-tag size="small" :type="meta.type" :disable-transitions="true">
      {{ meta.label }}
    </el-tag>
    <el-tag
      v-if="expired"
      size="small"
      type="warning"
      effect="plain"
      :disable-transitions="true"
    >
      已过期
    </el-tag>
  </span>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { PostStatus, postStatusMeta } from '@/config/ecosystem/enums';

  const props = defineProps<{
    status?: number | null;
    validUntil?: string | null;
  }>();

  const meta = computed(() => postStatusMeta(props.status));

  const expired = computed(() => {
    if (props.status !== PostStatus.LISTED || !props.validUntil) {
      return false;
    }
    const until = new Date(props.validUntil.replace(/-/g, '/')).getTime();
    return Number.isFinite(until) && until < Date.now();
  });
</script>

<style lang="scss" scoped>
  .eco-status {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
</style>
