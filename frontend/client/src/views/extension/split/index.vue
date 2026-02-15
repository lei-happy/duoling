<template>
  <ele-page
    hide-footer
    :flex-table="active === 'table'"
    :multi-card="active !== 'table'"
    :style="active !== 'table' ? void 0 : { minHeight: '420px' }"
  >
    <demo-basic v-if="active !== 'table'" @change="handleChange" />
    <demo-table v-else @change="handleChange" />
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import DemoBasic from './components/demo-basic.vue';
  import DemoTable from './components/demo-table.vue';
  const pagePath = '/extension/split';

  defineOptions({ name: 'ExtensionSplit' });

  const route = useRoute();
  const { push } = useRouter();

  const active = ref<string>();

  const handleChange = (value?: string) => {
    active.value = value;
    if (value) {
      push(`${pagePath}?type=${value}`);
      return;
    }
    push(pagePath);
  };

  watch(
    () => route.query.type,
    (type) => {
      if (route.path === pagePath) {
        active.value = [type].flat()[0] || '';
      }
    },
    { immediate: true }
  );
</script>
