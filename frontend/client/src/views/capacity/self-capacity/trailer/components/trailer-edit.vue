<template>
  <el-dialog
    :title="isEdit ? '编辑挂车' : '新增挂车'"
    :model-value="visible"
    width="780px"
    draggable
    class="trailer-edit-dialog"
    :close-on-click-modal="false"
    :body-style="dialogBodyStyle"
    @update:model-value="updateVisible"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="0"
      class="trailer-edit-form"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-tabs v-model="activeTab" class="trailer-edit-tabs">
        <el-tab-pane label="基础信息" name="basic">
          <div class="trailer-tab-pane">
            <el-row :gutter="16" align="middle">
              <el-col :span="12">
                <el-form-item prop="plateCategory" class="trailer-plate-category-item">
                  <el-radio-group
                    v-model="form.plateCategory"
                    size="small"
                    class="trailer-plate-category-radios"
                  >
                    <el-radio
                      v-for="opt in PLATE_CATEGORY_OPTIONS"
                      :key="opt.value"
                      :value="opt.value"
                      :label="opt.label"
                    />
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item prop="plateNumber">
                  <floating-label
                    :label="trailerPlateLabel"
                    type="input"
                    v-model.trim="form.plateNumber"
                    :maxlength="trailerPlateMaxLen"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col v-if="isEdit" :span="12">
                <el-form-item>
                  <floating-label
                    v-model="form.status"
                    label="请选择状态"
                    type="select"
                    clearable
                  >
                    <el-option label="正常" :value="1" />
                    <el-option label="停用" :value="0" />
                  </floating-label>
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="规格参数" name="spec">
          <div class="trailer-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item>
                  <dict-select-hint-wrap dict-name="挂车类型">
                    <floating-label
                      v-model="form.trailerType"
                      label="请选择挂车类型"
                      type="select"
                      :filterable="true"
                      clearable
                    >
                      <el-option
                        v-for="item in trailerTypeDict"
                        :key="item.dictDataCode"
                        :label="item.dictDataName"
                        :value="item.dictDataCode"
                      />
                    </floating-label>
                  </dict-select-hint-wrap>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入轴数"
                    type="input"
                    input-type="number"
                    v-model="axleCountStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入载重(吨)"
                    type="input"
                    input-type="number"
                    v-model="loadCapacityStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入容积(m³)"
                    type="input"
                    input-type="number"
                    v-model="volumeCapacityStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <floating-label
                    label="请输入车厢长(m)"
                    type="input"
                    input-type="number"
                    v-model="lengthStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <floating-label
                    label="请输入车厢宽(m)"
                    type="input"
                    input-type="number"
                    v-model="widthStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item>
                  <floating-label
                    label="请输入车厢高(m)"
                    type="input"
                    input-type="number"
                    v-model="heightStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请输入车位数"
                    type="input"
                    input-type="number"
                    v-model="parkingSpotsStr"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <el-tab-pane label="档案信息" name="archive">
          <div class="trailer-tab-pane">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item>
                  <floating-label
                    label="请选择购买日期"
                    type="date"
                    date-type="date"
                    v-model="form.purchaseDate"
                    value-format="YYYY-MM-DD"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item>
                  <floating-label
                    label="请输入备注"
                    type="input"
                    input-type="textarea"
                    v-model.trim="form.remark"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
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
  import { ref, reactive, watch, computed, nextTick } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import DictSelectHintWrap from '@/components/DictSelectHintWrap/index.vue';
  import FloatingLabel from '@shared/FloatingLabel/index.vue';
  import { addTrailer, updateTrailer } from '@/api/capacity/self-capacity/trailer';
  import type { Trailer } from '@/api/capacity/self-capacity/trailer/model';
  import {
    DEFAULT_PLATE_CATEGORY,
    PLATE_CATEGORY_OPTIONS,
    trailerPlateInputMaxLen
  } from '@/constants/plate-category';
  import type { PlateCategory } from '@/constants/plate-category';
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_TRAILER_TYPE } from '@/constants/dict-codes';

  const props = defineProps<{
    visible: boolean;
    data: Trailer | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.data?.id);
  const activeTab = ref('basic');
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const form = reactive<Trailer>({});

  const dialogBodyStyle = {
    padding: '0 12px 8px'
  };

  const [trailerTypeDict] = useDictData([DICT_CODE_TRAILER_TYPE]);

  const round2 = (n: number) => Math.round(n * 100) / 100;

  const decStr = (
    key: 'loadCapacity' | 'volumeCapacity' | 'length' | 'width' | 'height'
  ) =>
    computed({
      get: () => {
        const n = form[key];
        return n != null && !Number.isNaN(Number(n)) ? String(n) : '';
      },
      set: (v: string) => {
        const t = v?.trim();
        if (t === '' || t == null) {
          form[key] = void 0;
          return;
        }
        const n = Number(t);
        form[key] = Number.isFinite(n) ? round2(n) : void 0;
      }
    });

  const loadCapacityStr = decStr('loadCapacity');
  const volumeCapacityStr = decStr('volumeCapacity');
  const lengthStr = decStr('length');
  const widthStr = decStr('width');
  const heightStr = decStr('height');

  const axleCountStr = computed({
    get: () =>
      form.axleCount != null && !Number.isNaN(Number(form.axleCount))
        ? String(form.axleCount)
        : '',
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.axleCount = void 0;
        return;
      }
      const n = parseInt(t, 10);
      if (!Number.isFinite(n)) {
        form.axleCount = void 0;
        return;
      }
      form.axleCount = Math.min(10, Math.max(1, n));
    }
  });

  const parkingSpotsStr = computed({
    get: () =>
      form.parkingSpots != null && !Number.isNaN(Number(form.parkingSpots))
        ? String(form.parkingSpots)
        : '',
    set: (v: string) => {
      const t = v?.trim();
      if (t === '' || t == null) {
        form.parkingSpots = void 0;
        return;
      }
      const n = parseInt(t, 10);
      form.parkingSpots = Number.isFinite(n) && n >= 0 ? n : void 0;
    }
  });

  const trailerPlateMaxLen = computed(() =>
    trailerPlateInputMaxLen(
      (form.plateCategory as PlateCategory) ?? DEFAULT_PLATE_CATEGORY
    )
  );

  const trailerPlateLabel = computed(() => {
    const c =
      (form.plateCategory as PlateCategory) ?? DEFAULT_PLATE_CATEGORY;
    if (c === 'NEW_ENERGY') return '请输入挂车号牌（新能源 8 位）';
    return '请输入挂车号牌（如 京A1234挂）';
  });

  const rules = reactive<FormRules>({
    plateCategory: [
      { required: true, message: '请选择号牌类型', trigger: 'change' }
    ],
    plateNumber: [
      { required: true, message: '请输入挂车号牌', trigger: 'blur' }
    ]
  });

  watch(
    () => form.plateCategory,
    (cat) => {
      const ml = trailerPlateInputMaxLen(
        (cat as PlateCategory) ?? DEFAULT_PLATE_CATEGORY
      );
      const pn = form.plateNumber?.trim();
      if (pn && pn.length > ml) form.plateNumber = pn.slice(0, ml);
    }
  );

  watch(
    () => props.visible,
    (val) => {
      if (val) {
        activeTab.value = 'basic';
        if (props.data) {
          Object.assign(form, props.data);
          if (!form.plateCategory) {
            form.plateCategory = DEFAULT_PLATE_CATEGORY;
          }
        } else {
          Object.keys(form).forEach((k) => {
            (form as Record<string, unknown>)[k] = undefined;
          });
          form.plateCategory = DEFAULT_PLATE_CATEGORY;
        }
        void nextTick(() => {
          formRef.value?.clearValidate();
        });
      } else {
        void nextTick(() => {
          formRef.value?.clearValidate();
        });
      }
    }
  );

  const updateVisible = (val: boolean) => {
    emit('update:visible', val);
  };

  const handleSubmit = () => {
    formRef.value?.validate(async (valid) => {
      if (!valid) {
        activeTab.value = 'basic';
        return;
      }
      loading.value = true;
      try {
        if (isEdit.value) {
          await updateTrailer(form);
        } else {
          await addTrailer(form);
        }
        EleMessage.success({ message: '操作成功', plain: true });
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({ message: e.message, plain: true });
      } finally {
        loading.value = false;
      }
    });
  };
</script>

<style scoped>
  .trailer-edit-form {
    margin: 0;
  }

  .trailer-edit-tabs :deep(.el-tabs__header) {
    margin: 0 0 10px;
    border-bottom: none;
  }

  .trailer-edit-tabs :deep(.el-tabs__nav-wrap) {
    width: 100%;
  }

  .trailer-edit-tabs :deep(.el-tabs__nav-wrap)::after {
    display: none;
  }

  .trailer-edit-tabs :deep(.el-tabs__nav-scroll) {
    width: 100%;
    overflow: hidden;
  }

  .trailer-edit-tabs :deep(.el-tabs__nav) {
    display: flex;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    background: var(--el-fill-color-light);
  }

  .trailer-edit-tabs :deep(.el-tabs__item) {
    flex: 1;
    min-width: 0;
    margin: 0;
    padding: 0 6px;
    height: 36px;
    line-height: 36px;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    color: var(--el-text-color-regular);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition:
      color 0.2s,
      background 0.2s,
      box-shadow 0.2s;
  }

  .trailer-edit-tabs :deep(.el-tabs__item:hover) {
    color: var(--el-color-primary);
  }

  .trailer-edit-tabs :deep(.el-tabs__item.is-active) {
    color: var(--el-color-primary);
    font-weight: 600;
    background: var(--el-bg-color);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .trailer-edit-tabs :deep(.el-tabs__active-bar) {
    display: none;
  }

  .trailer-edit-tabs :deep(.el-tabs__content) {
    overflow: visible;
  }

  .trailer-tab-pane {
    max-height: min(420px, calc(100vh - 300px));
    overflow-y: auto;
    overflow-x: hidden;
    padding: 14px 6px 12px 4px;
    scrollbar-gutter: stable;
  }

  .trailer-edit-dialog :deep(.floating-label-wrapper.is-focused .floating-label),
  .trailer-edit-dialog :deep(.floating-label-wrapper.has-value .floating-label) {
    transform: translateY(-62%);
    padding: 2px 6px;
    z-index: 4;
    background-color: var(--el-bg-color) !important;
    box-shadow: 0 0 0 2px var(--el-bg-color);
  }

  .trailer-edit-dialog :deep(.trailer-tab-pane > .el-row > .el-col > .el-form-item) {
    margin-bottom: 14px;
  }

  .trailer-tab-pane > .el-row .trailer-plate-category-item :deep(.el-form-item__content) {
    display: flex;
    align-items: center;
    line-height: 1;
  }

  .trailer-plate-category-radios {
    display: inline-flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
  }

  .trailer-plate-category-radios :deep(.el-radio) {
    margin-right: 0;
  }
</style>
