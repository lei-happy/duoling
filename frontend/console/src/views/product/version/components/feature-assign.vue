<template>
  <ele-modal
    :width="520"
    :title="`配置功能 - ${versionName}`"
    v-bind="modalProps"
  >
    <el-alert
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 12px"
      title="勾选功能即表示『允许该版本下的菜单展示』"
      description="保存后系统会：1) 自动联动菜单 visible（避免远期预留菜单永远不显示）；2) 递增所有持有此版本的租户 menu_version，触发其客户端在下次切换路由/标签页激活时强制重新拉取菜单。如客户端仍未刷新，请引导用户 F5。"
    />
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
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_PRODUCT_MODULE } from '@/api/product/model';
  import type { ProductFeature } from '@/api/product/model';

  const [moduleDicts] = useDictData([DICT_CODE_PRODUCT_MODULE]);

  const moduleLabels = computed<Record<string, string>>(() => {
    const map: Record<string, string> = {};
    for (const d of moduleDicts.value) {
      map[d.dictDataCode] = d.dictDataName;
    }
    return map;
  });

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
    const labels = moduleLabels.value;
    const order = moduleDicts.value.map((d) => d.dictDataCode);
    const result: FeatureGroup[] = [];
    for (const mod of order) {
      const features = map.get(mod);
      if (features?.length) {
        result.push({
          module: mod,
          label: labels[mod] || mod,
          features
        });
      }
    }
    for (const [mod, features] of map) {
      if (!order.includes(mod)) {
        result.push({
          module: mod,
          label: labels[mod] || mod,
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
