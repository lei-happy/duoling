<template>
  <div class="mock-rows">
    <div
      v-for="(row, i) in rows"
      :key="i"
      class="mock-row"
      :class="{ 'is-head': row.head, 'is-full': row.full }"
    >
      <span
        v-for="(cell, j) in row.cells"
        :key="j"
        :class="{ num: row.nums?.includes(j) }"
      >
        {{ cell }}
      </span>
      <span v-if="row.tag" class="tag" :class="row.tag.kind && `tag-${row.tag.kind}`">
        {{ row.tag.text }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MockRow } from './mock';

defineProps<{ rows: MockRow[] }>();
</script>

<style scoped lang="scss">
.mock-row.is-full {
  grid-template-columns: 1fr;
}
</style>
