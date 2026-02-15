<!-- 全局页脚 -->
<template>
  <ele-text type="placeholder" class="ele-footer">
    <el-space :size="24">
      <el-link underline="never" href="https://eleadmin.com" target="_blank">
        {{ t('layout.footer.website') }}
      </el-link>
      <el-link
        underline="never"
        href="https://eleadmin.com/doc/eleadminplus/"
        target="_blank"
      >
        {{ t('layout.footer.document') }}
      </el-link>
      <el-link
        underline="never"
        href="https://eleadmin.com/goods/11"
        target="_blank"
      >
        {{ t('layout.footer.authorization') }}
      </el-link>
    </el-space>
    <div>{{ t('layout.footer.copyright') }}</div>
  </ele-text>
</template>

<script lang="ts" setup>
  import { useI18n } from 'vue-i18n';

  const { t } = useI18n();
</script>
