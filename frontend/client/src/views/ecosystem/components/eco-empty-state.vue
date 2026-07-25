<!--
  大厅空态

  空态是引导位而不是报错位：大厅冷启动时本来就没多少信息，
  用户此刻需要的是「换个条件试试」或者「先把自己的发上来」，
  而不是一句「暂无数据」。
-->
<template>
  <div class="eco-empty">
    <el-empty :image-size="90" :description="description">
      <template v-if="$slots.default" #default>
        <div class="eco-empty__actions">
          <slot></slot>
        </div>
      </template>
    </el-empty>
  </div>
</template>

<script lang="ts" setup>
  defineProps<{ description: string }>();
</script>

<style lang="scss" scoped>
  .eco-empty {
    padding: 24px 0 8px;
  }

  .eco-empty__actions {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  :deep(.el-empty__description) {
    max-width: 420px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.7;
  }
</style>
