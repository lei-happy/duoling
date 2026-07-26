<!--
  运力大厅

  与货源大厅对称：浏览与「我发布的」共用 `eco-hall-view`，这里只接运力的发布弹层。
  支持 `?capacityId=` 从运力列表直接发布。
-->
<template>
  <!-- 单根节点：配合 RouterLayout 的 transition mode="out-in"，避免 SPA 切换白屏 -->
  <div class="eco-hall-page">
    <eco-hall-view
      :key="PostType.CAPACITY"
      ref="hallRef"
      :post-type="PostType.CAPACITY"
      @publish="openPublish"
      @edit="openEdit"
    />

    <capacity-publish
      v-model:visible="publishVisible"
      :source-capacity-id="sourceCapacityId"
      :post="editing"
      @done="onDone"
    />
  </div>
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import { PostType } from '@/config/ecosystem/enums';
  import EcoHallView from '@/views/ecosystem/components/eco-hall-view.vue';
  import CapacityPublish from './components/capacity-publish.vue';

  defineOptions({ name: 'EcosystemCapacityHall' });

  const route = useRoute();
  const router = useRouter();

  const hallRef = ref<InstanceType<typeof EcoHallView> | null>(null);
  const publishVisible = ref(false);
  const sourceCapacityId = ref<number | null>(null);
  const editing = ref<EcoPost | null>(null);

  const openPublish = () => {
    editing.value = null;
    sourceCapacityId.value = null;
    publishVisible.value = true;
  };

  const openEdit = (post: EcoPost) => {
    sourceCapacityId.value = null;
    editing.value = post;
    publishVisible.value = true;
  };

  const onDone = () => {
    hallRef.value?.reload?.();
    hallRef.value?.switchToMine?.();
  };

  onMounted(() => {
    const capacityId = Number(route.query.capacityId);
    if (capacityId > 0) {
      sourceCapacityId.value = capacityId;
      publishVisible.value = true;
      router.replace({ query: {} });
    }
  });
</script>

<style lang="scss" scoped>
  .eco-hall-page {
    height: 100%;
  }
</style>
