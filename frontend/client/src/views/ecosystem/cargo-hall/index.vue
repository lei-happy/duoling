<!--
  货源大厅

  页面本身只负责把 postType 和货源的发布弹层接上，浏览、筛选、我发布的都在
  `eco-hall-view` 里，与运力大厅共用一份。

  路由上还支持 `?taskId=`：从任务单点「发布到货源大厅」进来时直接打开弹层并带出
  源单，用户不用再从一堆任务里把刚看的那一单找回来。
-->
<template>
  <eco-hall-view
    ref="hallRef"
    :post-type="PostType.CARGO"
    @publish="openPublish"
    @edit="openEdit"
  />

  <cargo-publish
    v-model:visible="publishVisible"
    :source-task-id="sourceTaskId"
    :post="editing"
    @done="onDone"
  />
</template>

<script lang="ts" setup>
  import { onMounted, ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import { PostType } from '@/config/ecosystem/enums';
  import EcoHallView from '@/views/ecosystem/components/eco-hall-view.vue';
  import CargoPublish from './components/cargo-publish.vue';

  defineOptions({ name: 'EcosystemCargoHall' });

  const route = useRoute();
  const router = useRouter();

  const hallRef = ref<InstanceType<typeof EcoHallView> | null>(null);
  const publishVisible = ref(false);
  const sourceTaskId = ref<number | null>(null);
  const editing = ref<EcoPost | null>(null);

  const openPublish = () => {
    editing.value = null;
    sourceTaskId.value = null;
    publishVisible.value = true;
  };

  const openEdit = (post: EcoPost) => {
    sourceTaskId.value = null;
    editing.value = post;
    publishVisible.value = true;
  };

  const onDone = () => {
    hallRef.value?.reload?.();
    // 发完直接切到「我发布的」：用户接下来要确认的是这条现在什么状态
    hallRef.value?.switchToMine?.();
  };

  onMounted(() => {
    const taskId = Number(route.query.taskId);
    if (taskId > 0) {
      sourceTaskId.value = taskId;
      publishVisible.value = true;
      // 清掉 query，否则刷新或返回时又弹一次
      router.replace({ query: {} });
    }
  });
</script>
