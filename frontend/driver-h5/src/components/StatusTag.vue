<template>
  <span class="status-tag" :class="`status-tag--${level}`">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  label: string;
  level?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

const props = withDefaults(defineProps<Props>(), {
  level: 'default'
});

const level = computed(() => props.level);
</script>

<style lang="scss" scoped>
.status-tag {
  display: inline-block;
  padding: 2px 8px;
  font-size: $font-size-xs;
  line-height: 1.6;
  border-radius: $border-radius-sm;
  background: rgba(100, 116, 139, 0.12);
  color: $text-secondary;
  white-space: nowrap;
}
.status-tag--primary {
  background: rgba(29, 78, 216, 0.12);
  color: $brand-primary;
}
.status-tag--success {
  background: rgba(22, 163, 74, 0.12);
  color: $brand-success;
}
.status-tag--warning {
  background: rgba(245, 158, 11, 0.12);
  color: $brand-warning;
}
.status-tag--danger {
  background: rgba(220, 38, 38, 0.12);
  color: $brand-danger;
}
.status-tag--info {
  background: rgba(14, 165, 233, 0.12);
  color: $brand-info;
}
</style>
