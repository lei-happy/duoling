<template>
  <ele-modal
    :width="720"
    v-model="visible"
    title="管理快捷操作"
    @closed="handleClosed"
  >
    <div class="picker-tip">
      仅展示您有权限的操作，最多添加 {{ quickActionMax }} 项。
    </div>
    <div v-if="selected.length" class="picker-selected">
      <div class="picker-group-title">已添加（{{ selected.length }}）</div>
      <div class="picker-selected-list">
        <el-tag
          v-for="item in selected"
          :key="item.key"
          closable
          class="picker-selected-tag"
          @close="emit('remove', item.key)"
        >
          {{ item.title }}
        </el-tag>
      </div>
    </div>
    <div v-if="groupedAvailable.length" class="picker-available">
      <div class="picker-group-title">可添加</div>
      <div
        v-for="group in groupedAvailable"
        :key="group.name"
        class="picker-group"
      >
        <div class="picker-group-title">{{ group.name }}</div>
        <el-row :gutter="12">
          <el-col
            v-for="item in group.items"
            :key="item.key"
            :md="8"
            :sm="12"
            :xs="24"
          >
            <ele-card
              bordered
              :body-style="{ padding: '12px' }"
              class="picker-item"
            >
              <div class="picker-item-main">
                <img
                  v-if="item.image"
                  :src="item.image"
                  :alt="item.title"
                  class="picker-item-img"
                />
                <el-icon v-else :style="{ color: item.color || '#69c0ff' }">
                  <AppstoreOutlined />
                </el-icon>
                <span>{{ item.title }}</span>
              </div>
              <el-button
                plain
                round
                size="small"
                type="primary"
                @click="emit('add', item.key)"
              >
                添加
              </el-button>
            </ele-card>
          </el-col>
        </el-row>
      </div>
    </div>
    <el-empty
      v-else-if="!selected.length"
      description="暂无可添加的快捷操作"
      :image-size="80"
    />
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import { AppstoreOutlined } from '@/components/icons';
  import { groupQuickActions } from '../quick-action/quick-action-registry';
  import type { QuickActionConfig } from '../quick-action/types';

  defineOptions({
    components: {
      AppstoreOutlined
    }
  });

  const props = defineProps<{
    modelValue: boolean;
    available: QuickActionConfig[];
    selected: QuickActionConfig[];
    quickActionMax: number;
  }>();

  const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void;
    (e: 'add', key: string): void;
    (e: 'remove', key: string): void;
  }>();

  const visible = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value)
  });

  const groupedAvailable = computed(() => {
    const grouped = groupQuickActions(props.available);
    return Object.keys(grouped).map((name) => ({
      name,
      items: grouped[name]
    }));
  });

  const handleClosed = () => {
    emit('update:modelValue', false);
  };
</script>

<style lang="scss" scoped>
  .picker-tip {
    margin: -8px 0 16px;
    color: var(--el-text-color-secondary);
    font-size: 13px;
  }

  .picker-group + .picker-group {
    margin-top: 16px;
  }

  .picker-group-title {
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 600;
  }

  .picker-selected {
    margin-bottom: 16px;
  }

  .picker-selected-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .picker-selected-tag {
    margin: 0;
  }

  .picker-available {
    margin-top: 4px;
  }

  .picker-item {
    margin-bottom: 12px;

    :deep(.ele-card-body) {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
  }

  .picker-item-main {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;

    .el-icon {
      font-size: 20px;
      flex-shrink: 0;
    }

    .picker-item-img {
      width: 20px;
      height: 20px;
      object-fit: cover;
      border-radius: 4px;
      flex-shrink: 0;
    }

    span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
</style>
