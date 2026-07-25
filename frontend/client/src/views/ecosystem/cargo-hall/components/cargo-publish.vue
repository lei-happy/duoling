<!--
  发布 / 编辑货源挂牌

  线路、时间、台数、货物明细一律来自任务单，弹层里只读展示、不给改：这些是运营
  比对源单的依据，能改就等于能挂一条与任务单无关的信息。所以左边是「这一单长什么
  样」，右边才是要填的东西。

  编辑时不显示展示天数：有效期只有「延长展示」一条修改路径，编辑改不了它，
  摆在表单里只会让用户以为自己改了。
-->
<template>
  <el-dialog
    :title="isEdit ? '编辑货源' : '发布货源到大厅'"
    :model-value="visible"
    width="1000px"
    draggable
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <!-- 大厅能力被关掉时不给填，省得填完才被拦 -->
    <el-alert
      v-if="options && !options.hallEnabled"
      type="warning"
      :closable="false"
      show-icon
      :title="options.disabledReason || '当前还不能发布到大厅，请联系管理员'"
    />

    <template v-else>
      <div v-if="!isEdit && !taskId" class="eco-publish__step">
        <p class="eco-publish__step-tip">
          先选一单还没派车的任务，线路、时间、台数会自动带过来。
        </p>
        <task-picker @pick="onPickTask" />
      </div>

      <el-row v-else :gutter="16">
        <el-col :md="9" :xs="24">
          <div class="eco-publish__source" v-loading="previewLoading">
            <div class="eco-publish__source-head">
              <span class="eco-publish__source-title">这一单</span>
              <el-button
                v-if="!isEdit"
                link
                type="primary"
                size="small"
                @click="resetTask"
              >
                换一单
              </el-button>
            </div>

            <div class="eco-publish__headline">{{ headline }}</div>

            <eco-route-arrow
              :from-province="recap.fromProvince"
              :from-city="recap.fromCity"
              :from-detail="recap.fromName"
              :to-province="recap.toProvince"
              :to-city="recap.toCity"
              :to-detail="recap.toName"
            />

            <ul class="eco-publish__facts">
              <li>
                <span>装车时间</span>
                <b>{{ recap.windowStart || '—' }}</b>
              </li>
              <li>
                <span>台数</span>
                <b
                  >{{ recap.totalQuantity ?? '—' }}
                  {{ recap.quantityUnit || '台' }}</b
                >
              </li>
            </ul>

            <el-alert
              v-if="blocked"
              type="error"
              :closable="false"
              show-icon
              :title="blockMessage"
            />
            <el-alert
              v-else-if="needsReview"
              type="info"
              :closable="false"
              show-icon
              title="这条信息会先由平台看一眼再上架，通常一两个小时内有结果。"
            />
            <p class="eco-publish__privacy">
              客户名称、内部成本、车架号不会发到大厅，同行只能看到线路、台数和车型。
            </p>
          </div>
        </el-col>

        <el-col :md="15" :xs="24">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="86px"
            @submit.prevent=""
          >
            <eco-publish-fields
              :form="form"
              :options="options ?? {}"
              :show-valid-days="!isEdit"
              @patch="(p) => Object.assign(form, p)"
            />

            <el-divider content-position="left">找什么样的车</el-divider>
            <el-row :gutter="12">
              <el-col :md="12" :xs="24">
                <el-form-item label="车型要求">
                  <el-select
                    v-model="truckTypes"
                    class="ele-fluid"
                    multiple
                    collapse-tags
                    clearable
                    placeholder="不限车型"
                  >
                    <el-option
                      v-for="name in truckTypeOptions"
                      :key="name"
                      :value="name"
                      :label="name"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :md="12" :xs="24">
                <el-form-item label="板位要求">
                  <div class="eco-publish__range">
                    <el-input-number
                      v-model="form.requireSlotMin"
                      :min="1"
                      :max="30"
                      :controls="false"
                      placeholder="不限"
                    />
                    <span class="eco-publish__range-sep">至</span>
                    <el-input-number
                      v-model="form.requireSlotMax"
                      :min="1"
                      :max="30"
                      :controls="false"
                      placeholder="不限"
                    />
                  </div>
                </el-form-item>
              </el-col>
              <el-col :md="12" :xs="24">
                <el-form-item label="结算方式">
                  <el-select
                    v-model="form.settleType"
                    class="ele-fluid"
                    clearable
                    placeholder="可以后面谈"
                  >
                    <el-option
                      v-for="item in options?.settleTypes || []"
                      :key="item.value"
                      :value="item.value"
                      :label="item.label"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col v-if="isPrepay" :md="12" :xs="24">
                <el-form-item label="预付比例">
                  <el-input-number
                    v-model="form.prepayRatio"
                    class="ele-fluid"
                    :min="0"
                    :max="100"
                    :controls="false"
                    placeholder="如 30"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="其他">
                  <el-checkbox v-model="allowSplit" label="可以分几台装" />
                  <el-checkbox
                    v-model="requireInsurance"
                    label="要求有货物保险"
                  />
                  <el-checkbox
                    v-model="timeNegotiable"
                    label="装车时间可以商量"
                  />
                </el-form-item>
              </el-col>
              <el-col v-if="isLongTerm" :span="24">
                <el-form-item label="发运频次">
                  <el-input
                    v-model="form.freqDesc"
                    :maxlength="100"
                    placeholder="如：每周 2 车，长期稳定"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="补充说明">
                  <el-input
                    v-model="form.otherRequirements"
                    type="textarea"
                    :rows="2"
                    :maxlength="500"
                    show-word-limit
                    placeholder="装卸要求、随车文件等。这里不要写电话或微信，会被拦下来"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="标题">
                  <el-input
                    v-model="form.title"
                    :maxlength="100"
                    :placeholder="headline || '留空就用系统生成的标题'"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-col>
      </el-row>
    </template>

    <template #footer>
      <el-button @click="updateVisible(false)">取消</el-button>
      <el-button
        v-if="showSubmit"
        type="primary"
        :loading="loading"
        :disabled="blocked"
        @click="save"
      >
        {{ isEdit ? '保存修改' : '发布到大厅' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
  import { computed, reactive, ref, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, phoneReg } from 'ele-admin-plus';
  import {
    editCargoPost,
    getPublishOptions,
    previewCargo,
    publishCargo
  } from '@/api/ecosystem/post';
  import type {
    EcoCargoForm,
    EcoPublishOptions,
    EcoPublishPreview
  } from '@/api/ecosystem/post/model';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import { useDictData } from '@/utils/use-dict-data';
  import { DICT_CODE_VEHICLE_TYPE } from '@/constants/dict-codes';
  import {
    CooperationType,
    DEFAULT_VALID_DAYS,
    PriceType,
    SettleType,
    VisibilityLevel
  } from '@/config/ecosystem/enums';
  import EcoRouteArrow from '@/views/ecosystem/components/eco-route-arrow.vue';
  import EcoPublishFields from '@/views/ecosystem/components/eco-publish-fields.vue';
  import TaskPicker from './task-picker.vue';
  import type { Task } from '@/api/operation/task/model';

  const props = defineProps<{
    visible: boolean;
    /** 传了就跳过选任务单，用于从任务单页直接发布 */
    sourceTaskId?: number | null;
    /** 编辑时传已发布的挂牌 */
    post?: EcoPost | null;
  }>();

  const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
    (e: 'done'): void;
  }>();

  const isEdit = computed(() => !!props.post?.id);

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const previewLoading = ref(false);
  const options = ref<EcoPublishOptions | null>(null);
  const preview = ref<EcoPublishPreview | null>(null);
  const taskId = ref<number | null>(null);
  const pickedTask = ref<Task | null>(null);

  /**
   * 车型要求用中文名而不是字典编码
   *
   * 字典项在各租户自己的库里，编码（`heavy_truck`）发到大厅，别家界面上就是一串
   * 英文，因为它查不到这个编码对应的中文名。
   */
  const [vehicleTypeDict] = useDictData([DICT_CODE_VEHICLE_TYPE]);
  const truckTypeOptions = computed(() =>
    (vehicleTypeDict.value ?? [])
      .map((d) => d.dictDataName)
      .filter((n): n is string => !!n)
  );

  const form = reactive<EcoCargoForm>(emptyForm());

  function emptyForm(): EcoCargoForm {
    return {
      contactName: '',
      contactPhone: '',
      contactBackup: null,
      validDays: DEFAULT_VALID_DAYS,
      cooperationType: CooperationType.ONCE,
      priceType: PriceType.NEGOTIABLE,
      priceAmount: null,
      priceIncludeTax: 0,
      priceNegotiable: 1,
      visibilityLevel: VisibilityLevel.CERTIFIED,
      contactVisibility: VisibilityLevel.NEGOTIATING,
      applyBlockRule: 1,
      extraBlockTenants: null,
      title: null,
      settleType: null,
      prepayRatio: null,
      requireTruckTypes: null,
      requireSlotMin: null,
      requireSlotMax: null,
      allowSplit: 0,
      requireInsurance: 0,
      otherRequirements: null,
      timeNegotiable: 1,
      freqDesc: null
    };
  }

  const rules = reactive<FormRules>({
    contactName: [{ required: true, message: '请填写联系人', trigger: 'blur' }],
    contactPhone: [
      { required: true, message: '请填写联系电话', trigger: 'blur' },
      { pattern: phoneReg, message: '手机号格式不对，请检查', trigger: 'blur' }
    ]
  });

  /** 0/1 与复选框之间的转换 */
  const boolField = (
    key: 'allowSplit' | 'requireInsurance' | 'timeNegotiable'
  ) =>
    computed({
      get: () => form[key] === 1,
      set: (v: boolean) => (form[key] = v ? 1 : 0)
    });

  const allowSplit = boolField('allowSplit');
  const requireInsurance = boolField('requireInsurance');
  const timeNegotiable = boolField('timeNegotiable');

  const truckTypes = computed({
    get: () => form.requireTruckTypes ?? [],
    set: (v: string[]) => (form.requireTruckTypes = v.length ? v : null)
  });

  const isPrepay = computed(() => form.settleType === SettleType.PREPAY);
  const isLongTerm = computed(
    () => form.cooperationType === CooperationType.LONG_TERM
  );

  /** 试算给的是「发出去长什么样」，编辑时直接用挂牌本身 */
  const recap = computed(() => {
    if (isEdit.value && props.post) {
      const p = props.post;
      return {
        fromProvince: p.fromProvince,
        fromCity: p.fromCity,
        fromName: p.fromName,
        toProvince: p.toProvince,
        toCity: p.toCity,
        toName: p.toName,
        windowStart: p.windowStart,
        totalQuantity: p.totalQuantity,
        quantityUnit: p.quantityUnit
      };
    }
    const v = preview.value;
    return {
      fromProvince: v?.fromProvince ?? pickedTask.value?.origin,
      fromCity: v?.fromCity,
      fromName: v?.fromName,
      toProvince: v?.toProvince ?? pickedTask.value?.destination,
      toCity: v?.toCity,
      toName: v?.toName,
      windowStart: v?.windowStart ?? pickedTask.value?.plannedLoadTime,
      totalQuantity: v?.totalQuantity ?? pickedTask.value?.totalQuantity,
      quantityUnit: v?.quantityUnit
    };
  });

  const headline = computed(
    () => preview.value?.title || props.post?.title || ''
  );
  const blocked = computed(() => !!preview.value?.precheck?.blocked);
  const blockMessage = computed(
    () => preview.value?.precheck?.blockMessage || '这一单现在还发不了'
  );
  const needsReview = computed(
    () => !blocked.value && !!preview.value?.precheck?.needsReview
  );

  const showSubmit = computed(
    () => !!options.value?.hallEnabled && (isEdit.value || !!taskId.value)
  );

  const updateVisible = (v: boolean) => emit('update:visible', v);

  const loadOptions = async () => {
    try {
      options.value = await getPublishOptions();
      if (!isEdit.value) {
        form.validDays = options.value.defaultValidDays ?? DEFAULT_VALID_DAYS;
        form.visibilityLevel = options.value.defaultVisibilityLevel;
        form.contactVisibility = options.value.defaultContactVisibility;
        form.contactName = options.value.defaultContactName ?? '';
        form.contactPhone = options.value.defaultContactPhone ?? '';
      }
    } catch (e: any) {
      EleMessage.error({
        message: e?.message ?? '没能读取发布设置，请稍后再试',
        plain: true
      });
    }
  };

  const runPreview = async (id: number) => {
    previewLoading.value = true;
    try {
      preview.value = await previewCargo(id);
    } catch (e: any) {
      // 试算失败通常就是这一单不满足发布条件，文案本身就是给用户看的
      preview.value = null;
      taskId.value = null;
      EleMessage.error({
        message: e?.message ?? '这一单暂时发不了',
        plain: true
      });
    } finally {
      previewLoading.value = false;
    }
  };

  const onPickTask = (task: Task) => {
    if (!task.id) {
      return;
    }
    pickedTask.value = task;
    taskId.value = task.id;
    runPreview(task.id);
  };

  const resetTask = () => {
    taskId.value = null;
    pickedTask.value = null;
    preview.value = null;
  };

  const fillFromPost = (post: EcoPost) => {
    Object.assign(form, {
      contactName: post.contactName ?? '',
      contactPhone: post.contactPhone ?? '',
      contactBackup: post.contactBackup ?? null,
      validDays: DEFAULT_VALID_DAYS,
      cooperationType: post.cooperationType ?? CooperationType.ONCE,
      priceType: post.priceType ?? PriceType.NEGOTIABLE,
      priceAmount: post.priceAmount == null ? null : Number(post.priceAmount),
      priceIncludeTax: post.priceIncludeTax ?? 0,
      priceNegotiable: post.priceNegotiable ?? 1,
      visibilityLevel: post.visibilityLevel ?? VisibilityLevel.CERTIFIED,
      contactVisibility: post.contactVisibility ?? VisibilityLevel.NEGOTIATING,
      applyBlockRule: post.applyBlockRule ?? 1,
      extraBlockTenants: post.extraBlockTenants ?? null,
      title: post.title ?? null,
      settleType: post.settleType ?? null,
      prepayRatio: post.prepayRatio ?? null,
      requireTruckTypes: post.requireTruckTypes ?? null,
      requireSlotMin: post.requireSlotMin ?? null,
      requireSlotMax: post.requireSlotMax ?? null,
      allowSplit: post.allowSplit ?? 0,
      requireInsurance: post.requireInsurance ?? 0,
      otherRequirements: post.otherRequirements ?? null,
      timeNegotiable: post.timeNegotiable ?? 1,
      freqDesc: post.freqDesc ?? null
    });
  };

  const onOpen = async () => {
    Object.assign(form, emptyForm());
    preview.value = null;
    pickedTask.value = null;
    taskId.value = props.sourceTaskId ?? null;
    formRef.value?.clearValidate();

    await loadOptions();
    if (isEdit.value && props.post) {
      fillFromPost(props.post);
    } else if (taskId.value) {
      runPreview(taskId.value);
    }
  };

  const save = () => {
    formRef.value?.validate?.(async (valid) => {
      if (!valid) {
        return;
      }
      if (!isEdit.value && !taskId.value) {
        EleMessage.warning({ message: '请先选一单任务', plain: true });
        return;
      }
      loading.value = true;
      const tip = EleMessage.loading({
        message: isEdit.value ? '正在保存修改，请稍候…' : '正在发布，请稍候…',
        plain: true
      });
      try {
        if (isEdit.value && props.post?.id) {
          const { data, message } = await editCargoPost(props.post.id, form);
          EleMessage.success({
            message:
              message ||
              (data.requireReaudit
                ? '改动较大，这条信息会重新审核后再展示'
                : '已保存'),
            plain: true
          });
        } else {
          const { data, message } = await publishCargo({
            ...form,
            taskId: taskId.value as number
          });
          EleMessage.success({
            message:
              message ||
              (data.autoListed
                ? '已发布，同行现在就能看到'
                : '已提交，平台看过之后就会出现在大厅里'),
            plain: true
          });
        }
        updateVisible(false);
        emit('done');
      } catch (e: any) {
        EleMessage.error({
          message: e?.message ?? '没能提交，请稍后再试',
          plain: true
        });
      } finally {
        tip.close();
        loading.value = false;
      }
    });
  };

  /** 关掉时清干净，避免下次打开闪一眼上一条的数据 */
  watch(
    () => props.visible,
    (v) => {
      if (!v) {
        preview.value = null;
        pickedTask.value = null;
        taskId.value = null;
      }
    }
  );
</script>

<style lang="scss" scoped>
  .eco-publish__step-tip {
    margin: 0 0 10px;
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .eco-publish__source {
    padding: 14px;
    border-radius: 8px;
    background: var(--el-fill-color-lighter);
  }

  .eco-publish__source-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .eco-publish__source-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
  }

  .eco-publish__headline {
    margin-bottom: 10px;
    font-size: 15px;
    font-weight: 600;
    line-height: 1.4;
    color: var(--el-text-color-primary);
  }

  .eco-publish__facts {
    margin: 12px 0;
    padding: 0;
    list-style: none;

    li {
      display: flex;
      justify-content: space-between;
      padding: 4px 0;
      font-size: 13px;
      color: var(--el-text-color-regular);

      b {
        font-weight: 600;
        color: var(--el-text-color-primary);
      }
    }
  }

  .eco-publish__privacy {
    margin: 10px 0 0;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-text-color-secondary);
  }

  .eco-publish__range {
    display: flex;
    align-items: center;
    gap: 6px;

    :deep(.el-input-number) {
      flex: 1;
    }
  }

  .eco-publish__range-sep {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }
</style>
