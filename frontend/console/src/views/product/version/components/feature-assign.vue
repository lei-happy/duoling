<template>
  <ele-modal
    :width="520"
    :title="`配置功能 - ${versionName}`"
    v-bind="modalProps"
  >
    <el-skeleton :loading="loading" :rows="8" animated>
      <template #default>
        <div
          v-for="group in featureGroups"
          :key="group.module"
          style="margin-bottom: 16px"
        >
          <div
            style="
              font-weight: bold;
              margin-bottom: 8px;
              color: var(--el-text-color-primary);
            "
          >
            {{ group.label }}
          </div>
          <el-checkbox-group v-model="selectedIds">
            <el-checkbox
              v-for="f in group.features"
              :key="f.id"
              :value="f.id!"
              :label="f.featureName"
              style="margin-bottom: 4px; display: block"
            />
          </el-checkbox-group>
        </div>
        <el-empty v-if="!featureGroups.length" description="暂无功能数据" />
      </template>
    </el-skeleton>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', loading: saving, onClick: () => handleSave() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, onMounted, computed } from 'vue';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import {
    listFeatures,
    getVersionFeatures,
    assignVersionFeatures
  } from '@/api/product';
  import type { ProductFeature } from '@/api/product/model';

  const MODULE_LABELS: Record<string, string> = {
    base: '基础模块',
    resource: '资源管理',
    biz: '业务模块',
    finance: '财务模块',
    bi: '数据分析'
  };

  const props = defineProps<{
    data: { id: number; versionName?: string };
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const versionName = computed(() => props.data?.versionName || '');

  const loading = ref(true);
  const saving = ref(false);
  const allFeatures = ref<ProductFeature[]>([]);
  const selectedIds = ref<number[]>([]);

  interface FeatureGroup {
    module: string;
    label: string;
    features: ProductFeature[];
  }

  const featureGroups = computed<FeatureGroup[]>(() => {
    const map = new Map<string, ProductFeature[]>();
    for (const f of allFeatures.value) {
      const mod = f.module || 'other';
      if (!map.has(mod)) map.set(mod, []);
      map.get(mod)!.push(f);
    }
    const order = Object.keys(MODULE_LABELS);
    const result: FeatureGroup[] = [];
    for (const mod of order) {
      const features = map.get(mod);
      if (features?.length) {
        result.push({
          module: mod,
          label: MODULE_LABELS[mod] || mod,
          features
        });
      }
    }
    for (const [mod, features] of map) {
      if (!order.includes(mod)) {
        result.push({
          module: mod,
          label: MODULE_LABELS[mod] || mod,
          features
        });
      }
    }
    return result;
  });

  const handleCancel = () => {
    closeModal();
  };

  const handleSave = () => {
    saving.value = true;
    assignVersionFeatures(props.data.id, selectedIds.value)
      .then((msg) => {
        saving.value = false;
        EleMessage.success({ message: msg, plain: true });
        emit('done');
        handleCancel();
      })
      .catch((e) => {
        saving.value = false;
        EleMessage.error({ message: e.message, plain: true });
      });
  };

  onMounted(async () => {
    try {
      const [features, assigned] = await Promise.all([
        listFeatures({ status: 1 }),
        getVersionFeatures(props.data.id)
      ]);
      allFeatures.value = features;
      selectedIds.value = assigned
        .filter((a) => a.featureId != null)
        .map((a) => a.featureId!);
    } catch (e: any) {
      EleMessage.error({ message: e.message, plain: true });
    } finally {
      loading.value = false;
    }
  });
</script>
