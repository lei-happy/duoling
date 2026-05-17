<template>
  <el-dialog
    :title="isEdit ? '编辑线路' : '新增线路'"
    :model-value="visible"
    width="720px"
    draggable
    class="route-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    append-to-body
    destroy-on-close
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="route-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-row :gutter="10">
        <template v-if="isEdit">
          <el-col :xs="24" :sm="12">
            <el-form-item prop="routeCode">
              <floating-label
                label="线路编码"
                type="input"
                v-model="form.routeCode"
                disabled
                :clearable="false"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item prop="routeName">
              <floating-label
                label="线路名称"
                type="input"
                v-model.trim="form.routeName"
                clearable
              />
            </el-form-item>
          </el-col>
        </template>
        <el-col :xs="24" :sm="12">
          <el-form-item prop="originCode">
            <floating-label
              label="请选择出发地"
              type="cascader"
              v-model="originCodes"
              :cascader-options="regionTree"
              :cascader-option-props="regionCascaderProps"
              :cascader-filterable="true"
              @change="onOriginChange"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item prop="destinationCode">
            <floating-label
              label="请选择目的地"
              type="cascader"
              v-model="destCodes"
              :cascader-options="regionTree"
              :cascader-option-props="regionCascaderProps"
              :cascader-filterable="true"
              @change="onDestChange"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item prop="distance">
            <floating-label
              label="里程(km)"
              type="input-number"
              v-model="form.distance"
              :input-number-min="0"
              :input-number-precision="1"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
        <el-col :xs="24" :sm="12">
          <el-form-item prop="estimatedHours">
            <floating-label
              label="预计时长(h)"
              type="input-number"
              v-model="form.estimatedHours"
              :input-number-min="0"
              :input-number-precision="1"
              :clearable="false"
            />
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item prop="remark">
            <floating-label
              label="备注"
              type="input"
              input-type="textarea"
              v-model="form.remark"
              clearable
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch, computed } from 'vue';
  import type { CascaderProps, FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addRoute, updateRoute } from '@/api/resource/route';
  import type { Route } from '@/api/resource/route/model';
  import { getRegionNavTree, getRegion } from '@/api/basic-data/region';
  import type { RegionNavNode } from '@/api/basic-data/region/model';
  import {
    findLeafRegionByCodePath,
    findRegionCodePath
  } from '@/utils/region-nav-tree';

  const props = defineProps<{
    visible: boolean;
    data: Route | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Route>({});
  const regionTree = ref<RegionNavNode[]>([]);
  const originCodes = ref<string[]>([]);
  const destCodes = ref<string[]>([]);

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const regionCascaderProps: CascaderProps = {
    value: 'code',
    label: 'name',
    children: 'children',
    emitPath: true,
    checkStrictly: true
  };

  const rules = computed<FormRules>(() => {
    const r: FormRules = {
      originCode: [
        { required: true, message: '请选择出发地', trigger: 'change' }
      ],
      destinationCode: [
        { required: true, message: '请选择目的地', trigger: 'change' }
      ]
    };
    if (isEdit.value) {
      r.routeName = [
        { required: true, message: '请输入线路名称', trigger: 'blur' }
      ];
    }
    return r;
  });

  const findRegionName = (codes: string[]): string => {
    if (!codes.length) return '';
    const names: string[] = [];
    let nodes = regionTree.value;
    for (const code of codes) {
      const node = nodes.find((n) => n.code === code);
      if (node) {
        names.push(node.name);
        nodes = node.children ?? [];
      }
    }
    return names.join('/');
  };

  const onOriginChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.originCode = val[val.length - 1];
      form.origin = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.originRegionId = leaf?.regionId ?? undefined;
    } else {
      form.originCode = undefined;
      form.origin = undefined;
      form.originRegionId = undefined;
    }
  };

  const onDestChange = (val: string[] | undefined) => {
    if (val && val.length) {
      form.destinationCode = val[val.length - 1];
      form.destination = findRegionName(val);
      const leaf = findLeafRegionByCodePath(regionTree.value, val);
      form.destinationRegionId = leaf?.regionId ?? undefined;
    } else {
      form.destinationCode = undefined;
      form.destination = undefined;
      form.destinationRegionId = undefined;
    }
  };

  async function hydrateRegionCodesFromIds() {
    const oId = form.originRegionId;
    if (oId && !form.originCode) {
      const r = await getRegion(oId).catch(() => null);
      if (r?.code) form.originCode = r.code;
    }
    const dId = form.destinationRegionId;
    if (dId && !form.destinationCode) {
      const r = await getRegion(dId).catch(() => null);
      if (r?.code) form.destinationCode = r.code;
    }
  }

  watch(
    () => props.visible,
    async (val) => {
      if (!val) return;
      try {
        regionTree.value = (await getRegionNavTree()) ?? [];
      } catch {
        regionTree.value = [];
      }
      originCodes.value = [];
      destCodes.value = [];

      if (props.data?.id) {
        Object.assign(form, props.data);
        await hydrateRegionCodesFromIds();
        if (form.originCode) {
          const op = findRegionCodePath(regionTree.value, form.originCode);
          originCodes.value = op ?? [form.originCode];
        }
        if (form.destinationCode) {
          const dp = findRegionCodePath(regionTree.value, form.destinationCode);
          destCodes.value = dp ?? [form.destinationCode];
        }
        const oLeaf = findLeafRegionByCodePath(
          regionTree.value,
          originCodes.value
        );
        const dLeaf = findLeafRegionByCodePath(
          regionTree.value,
          destCodes.value
        );
        if (oLeaf) form.originRegionId = oLeaf.regionId;
        if (dLeaf) form.destinationRegionId = dLeaf.regionId;
      } else {
        Object.keys(form).forEach((k) => {
          (form as Record<string, unknown>)[k] = undefined;
        });
      }
      formRef.value?.clearValidate();
    }
  );

  const updateVisible = (v: boolean) => {
    emit('update:visible', v);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) return;
      if (!form.originRegionId || !form.destinationRegionId) {
        EleMessage.warning({ message: '请选择出发地与目的地', plain: true });
        return;
      }
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateRoute({
            id: form.id,
            routeName: form.routeName?.trim(),
            originRegionId: form.originRegionId,
            destinationRegionId: form.destinationRegionId,
            distance: form.distance,
            estimatedHours: form.estimatedHours,
            remark: form.remark
          });
        } else {
          await addRoute({
            originRegionId: form.originRegionId,
            destinationRegionId: form.destinationRegionId,
            distance: form.distance,
            estimatedHours: form.estimatedHours,
            remark: form.remark
          });
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: unknown) {
        const msg = e instanceof Error ? e.message : '操作失败';
        EleMessage.error({ message: msg, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .route-edit-form :deep(.el-form-item) {
    margin-bottom: 14px;
  }
</style>
