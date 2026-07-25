<!--
  升级引导

  两种用户心理完全不同，不能用同一段文案应付（05.前端交互与UX设计.md §7.2）：

  - 已经能发布的租户（standard）：他知道大厅有价值，缺的是「主动出击」的能力
  - 还没体会过价值的租户（lite / ylb）：先要证明这个市场是活的

  文案里刻意不写「大厅现有 138 条货源」这类数字：灰度期数据量小，
  编出来的繁荣一眼就被看穿，反而损害信任。等有了真实统计接口再补。
-->
<template>
  <ele-modal
    :width="520"
    :title="config.title"
    :model-value="visible"
    @update:model-value="updateVisible"
  >
    <div class="eco-upgrade">
      <p class="eco-upgrade__lead">{{ config.lead }}</p>
      <ul class="eco-upgrade__list">
        <li v-for="(item, index) in config.items" :key="index">
          <el-icon class="eco-upgrade__icon"><CircleCheckFilled /></el-icon>
          <span>{{ item }}</span>
        </li>
      </ul>
      <p class="eco-upgrade__foot">{{ config.foot }}</p>
    </div>
    <template #footer>
      <el-button @click="updateVisible(false)">以后再说</el-button>
      <el-button type="primary" @click="goUpgrade">
        {{ config.confirm }}
      </el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { useRouter } from 'vue-router';
  import { CircleCheckFilled } from '@element-plus/icons-vue';

  const props = defineProps<{
    visible: boolean;
    /** intent-想主动联系同行；publish-想发布自己的货或车 */
    scene: 'intent' | 'publish';
    /** 货源 / 运力，用于把文案说到具体业务上 */
    postType?: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', visible: boolean): void;
  }>();

  const router = useRouter();

  const subject = computed(() => (props.postType === 2 ? '运力' : '货源'));

  const config = computed(() => {
    if (props.scene === 'intent') {
      return {
        title: '专业版可以主动联系同行',
        lead: `你已经可以把${subject.value}发布到大厅，让同行找上门。升级专业版后还能主动出击：`,
        items: [
          '主动向同行发起合作意向',
          '对方响应后互相看到联系方式，直接沟通',
          '订阅常跑线路，有新信息第一时间提醒你'
        ],
        foot: '现在这条信息的发布方还看不到你，升级后你可以先开口。',
        confirm: '了解专业版'
      };
    }
    return {
      title: `发布${subject.value}需要标准版及以上`,
      lead: '同行之间互通有无，靠的就是把手上的货和车挂出来：',
      items: [
        `把吃不下的${subject.value}交给同行，不用再打一圈电话`,
        '信息由平台审核后展示，避免无效询问',
        '谁看过、谁想合作，都能在「我发布的」里跟进'
      ],
      foot: '浏览大厅一直是免费的，你可以先看看有没有合适的机会。',
      confirm: '查看版本对比'
    };
  });

  const updateVisible = (value: boolean) => {
    emit('update:visible', value);
  };

  const goUpgrade = () => {
    updateVisible(false);
    router.push('/upgrade-plans').catch(() => {});
  };
</script>

<style lang="scss" scoped>
  .eco-upgrade__lead {
    margin: 0 0 12px;
    line-height: 1.7;
    color: var(--el-text-color-primary);
  }

  .eco-upgrade__list {
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      padding: 5px 0;
      line-height: 1.6;
      color: var(--el-text-color-regular);
    }
  }

  .eco-upgrade__icon {
    margin-top: 3px;
    color: var(--el-color-success);
  }

  .eco-upgrade__foot {
    margin: 12px 0 0;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color-lighter);
    line-height: 1.7;
    color: var(--el-text-color-secondary);
  }
</style>
