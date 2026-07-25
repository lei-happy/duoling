<!--
  延长展示天数

  单独做一个弹层是因为要让用户选天数，而不是替他决定。延长只对「展示中」的挂牌
  有效，也不触发重审——所以这是一个低风险、可以随手点的动作，界面要够轻。

  后端从原始起展日算总时长并有上限（单次合作 30 天、长期 90 天），
  所以这里说的是「再展示几天」而不是「延长到某天」，避免用户以为可以无限续。
-->
<template>
  <ele-modal
    :width="420"
    title="延长展示"
    :model-value="visible"
    @update:model-value="updateVisible"
  >
    <div class="eco-extend">
      <p class="eco-extend__tip">
        {{ currentTip }}
      </p>
      <el-radio-group v-model="days">
        <el-radio-button v-for="item in dayOptions" :key="item" :value="item">
          {{ item }} 天
        </el-radio-button>
      </el-radio-group>
      <p class="eco-extend__hint">
        平台对总展示时长有上限，超出时会自动按上限截取。
      </p>
    </div>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="save">
        确定延长
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed, ref, watch } from 'vue';
  import { EleMessage } from 'ele-admin-plus';
  import { extendPost } from '@/api/ecosystem/post';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import {
    DEFAULT_VALID_DAYS,
    VALID_DAYS_FALLBACK
  } from '@/config/ecosystem/enums';

  const props = defineProps<{
    visible: boolean;
    post?: EcoPost | null;
    /** 由 /filters 或 /publish/options 下发，缺省时用兜底值 */
    dayOptions?: number[];
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', visible: boolean): void;
    (e: 'done'): void;
  }>();

  const days = ref(DEFAULT_VALID_DAYS);
  const loading = ref(false);

  const dayOptions = computed(() =>
    props.dayOptions?.length ? props.dayOptions : VALID_DAYS_FALLBACK
  );

  const currentTip = computed(() => {
    const until = props.post?.validUntil;
    if (!until) {
      return '选择还要展示多少天。';
    }
    return `当前展示到 ${until}，选择在此基础上再展示多少天。`;
  });

  watch(
    () => props.visible,
    (open) => {
      if (open) {
        days.value = DEFAULT_VALID_DAYS;
      }
    }
  );

  const updateVisible = (value: boolean) => {
    emit('update:visible', value);
  };

  const save = async () => {
    const post = props.post;
    if (!post) {
      return;
    }
    loading.value = true;
    try {
      const { data, message } = await extendPost(post.id, days.value);
      EleMessage.success({
        message: data.validUntil
          ? `已延长，展示到 ${data.validUntil}`
          : message || '已延长展示时间',
        plain: true
      });
      updateVisible(false);
      emit('done');
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能延长，请稍后再试',
        plain: true
      });
    } finally {
      loading.value = false;
    }
  };
</script>

<style lang="scss" scoped>
  .eco-extend__tip {
    margin: 0 0 12px;
    line-height: 1.7;
    color: var(--el-text-color-regular);
  }

  .eco-extend__hint {
    margin: 12px 0 0;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }
</style>
