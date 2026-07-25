<!--
  企业档案弹层：既用于查看白名单成员，也用于「先查资格、再决定要不要开免审」

  不传 tenantCode 时先让运营输入编码——授予免审是主动动作，入口不该藏在
  某条挂牌的详情里，否则想给一家老客户开免审，还得先等他发一条货源。
-->
<template>
  <ele-modal :width="640" :title="title" v-model="visible">
    <el-form v-if="!tenantCode" inline @submit.prevent="query">
      <el-form-item label="企业编码">
        <el-input
          clearable
          v-model="input"
          placeholder="例如 zt10001"
          style="width: 220px"
          @keyup.enter="query"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="query">查资格</el-button>
      </el-form-item>
    </el-form>

    <el-alert
      v-if="!tenantCode && !current"
      type="info"
      :closable="false"
      show-icon
      title="输入企业编码后，这里会列出它的历史记录与还差哪几项条件。"
    />

    <tenant-profile
      v-if="current"
      :tenant-code="current"
      @changed="onChanged"
    />

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, ref } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import TenantProfile from '@/views/ecosystem/components/tenant-profile.vue';

  const props = defineProps<{
    /** 传了就直接看这家；不传则由运营输入编码 */
    tenantCode?: string | null;
    onDone?: () => void;
  }>();

  const visible = defineModel<boolean>({ default: false });

  const input = ref('');
  const queried = ref<string | null>(null);

  const current = computed(() => props.tenantCode || queried.value);

  const title = computed(() =>
    props.tenantCode ? '企业档案与免审处置' : '授予免审白名单'
  );

  const query = () => {
    const code = input.value.trim();
    if (!code) {
      EleMessage.warning({ message: '请先输入企业编码', plain: true });
      return;
    }
    queried.value = code;
  };

  const onChanged = () => {
    props.onDone?.();
  };
</script>
