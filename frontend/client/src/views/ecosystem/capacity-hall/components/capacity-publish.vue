<!--
  发布 / 编辑运力挂牌

  与货源不同的是：车、司机、板位来自运力档案，但**当前所在地和期望流向必须用户
  填**——运力档案里没有实时位置，而位置与流向正是找车方的第一决策依据。填完位置
  才能试算出标题与线路，所以试算在这两项变化后再跑。

  司机真名与手机号不会发到大厅：对外只显示「王师傅」，车牌默认打码。
-->
<template>
  <el-dialog
    :title="isEdit ? '编辑运力' : '发布空闲运力'"
    :model-value="visible"
    width="1000px"
    draggable
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    @update:model-value="updateVisible"
    @open="onOpen"
  >
    <el-alert
      v-if="options && !options.hallEnabled"
      type="warning"
      :closable="false"
      show-icon
      :title="options.disabledReason || '当前还不能发布到大厅，请联系管理员'"
    />

    <template v-else>
      <div v-if="!isEdit && !capacityId" class="eco-publish__step">
        <p class="eco-publish__step-tip">
          先选一台可接单的车，车型、板位、证照会自动带过来。
        </p>
        <capacity-picker @pick="onPickCapacity" />
      </div>

      <el-row v-else :gutter="16">
        <el-col :md="9" :xs="24">
          <div class="eco-publish__source" v-loading="previewLoading">
            <div class="eco-publish__source-head">
              <span class="eco-publish__source-title">这台车</span>
              <el-button
                v-if="!isEdit"
                link
                type="primary"
                size="small"
                @click="resetCapacity"
              >
                换一台
              </el-button>
            </div>

            <div class="eco-publish__headline">
              {{ headline || '填好所在地和流向后，这里显示标题' }}
            </div>

            <ul class="eco-publish__facts">
              <li>
                <span>车牌</span>
                <b>{{ plateText }}</b>
              </li>
              <li>
                <span>司机</span>
                <b>{{ driverText }}</b>
              </li>
              <li v-if="recap.totalQuantity">
                <span>板位</span>
                <b>{{ recap.totalQuantity }} 台</b>
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
              司机姓名只显示姓氏，手机号不会发到大厅；车牌默认打码，需要露出可以在下面勾选。
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
            <el-divider content-position="left">车在哪、想往哪跑</el-divider>
            <el-row :gutter="12">
              <el-col :md="12" :xs="24">
                <el-form-item label="当前所在" prop="fromRegionId">
                  <eco-region-select
                    v-model="form.fromRegionId"
                    placeholder="选到市就够了"
                    @change="schedulePreview"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :xs="24">
                <el-form-item label="可用时间" prop="windowStart">
                  <el-date-picker
                    v-model="form.windowStart"
                    class="ele-fluid"
                    type="datetime"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    placeholder="什么时候能装"
                    @change="schedulePreview"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="期望流向">
                  <div class="eco-publish__direction">
                    <el-checkbox
                      v-model="anyDirection"
                      label="哪都能去"
                      @change="schedulePreview"
                    />
                    <eco-region-select
                      v-if="!anyDirection"
                      v-model="form.toRegionIds"
                      multiple
                      placeholder="想跑的省或市，可多选"
                      @change="schedulePreview"
                    />
                  </div>
                </el-form-item>
              </el-col>
              <el-col :md="12" :xs="24">
                <el-form-item label="接货半径">
                  <el-input-number
                    v-model="form.pickupRadius"
                    class="ele-fluid"
                    :min="0"
                    :max="500"
                    :controls="false"
                    placeholder="愿意空驶多少公里"
                  />
                </el-form-item>
              </el-col>
              <el-col :md="12" :xs="24">
                <el-form-item label="板位">
                  <el-input-number
                    v-model="form.slotCount"
                    class="ele-fluid"
                    :min="1"
                    :max="30"
                    :controls="false"
                    placeholder="档案里没有时手填"
                    @change="schedulePreview"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <eco-publish-fields
              :form="form"
              :options="options ?? {}"
              :show-valid-days="!isEdit"
              @patch="(p) => Object.assign(form, p)"
            />

            <el-divider content-position="left">还能补充的</el-divider>
            <el-row :gutter="12">
              <el-col :md="12" :xs="24">
                <el-form-item label="结算要求">
                  <el-select
                    v-model="form.settleRequire"
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
              <el-col :md="12" :xs="24">
                <el-form-item label="发票类型">
                  <el-input
                    v-model="form.invoiceType"
                    :maxlength="50"
                    :disabled="!canInvoice"
                    placeholder="如：增值税专用发票"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="其他">
                  <el-checkbox v-model="canInvoice" label="能开发票" />
                  <el-checkbox v-model="hasInsurance" label="有货物运输险" />
                  <el-checkbox v-model="platePublic" label="公开完整车牌" />
                  <el-checkbox
                    v-model="keepListedAfterDeal"
                    label="谈成一单后继续展示"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="24">
                <el-form-item label="服务承诺">
                  <el-input
                    v-model="form.servicePromise"
                    type="textarea"
                    :rows="2"
                    :maxlength="500"
                    show-word-limit
                    placeholder="如：准时到场、随车拍照回传。这里不要写电话或微信，会被拦下来"
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
    editCapacityPost,
    getPublishOptions,
    previewCapacity,
    publishCapacity
  } from '@/api/ecosystem/post';
  import type {
    EcoCapacityForm,
    EcoPublishOptions,
    EcoPublishPreview
  } from '@/api/ecosystem/post/model';
  import type { EcoPost } from '@/api/ecosystem/hall/model';
  import type { Capacity } from '@/api/capacity/self-capacity/list/model';
  import {
    CooperationType,
    DEFAULT_VALID_DAYS,
    PriceType,
    VisibilityLevel
  } from '@/config/ecosystem/enums';
  import EcoPublishFields from '@/views/ecosystem/components/eco-publish-fields.vue';
  import EcoRegionSelect from '@/views/ecosystem/components/eco-region-select.vue';
  import CapacityPicker from './capacity-picker.vue';

  const props = defineProps<{
    visible: boolean;
    /** 传了就跳过选车，用于从运力列表直接发布 */
    sourceCapacityId?: number | null;
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
  const capacityId = ref<number | null>(null);
  const picked = ref<Capacity | null>(null);

  const form = reactive<EcoCapacityForm>(emptyForm());

  function emptyForm(): EcoCapacityForm {
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
      fromRegionId: null,
      toRegionIds: [],
      anyDirection: 0,
      windowStart: null,
      windowEnd: null,
      departureReadyAt: null,
      pickupRadius: null,
      keepListedAfterDeal: 0,
      settleRequire: null,
      slotCount: null,
      platePublic: 0,
      goodAtCategories: null,
      canInvoice: 0,
      invoiceType: null,
      hasInsurance: 0,
      servicePromise: null
    };
  }

  const rules = reactive<FormRules>({
    contactName: [{ required: true, message: '请填写联系人', trigger: 'blur' }],
    contactPhone: [
      { required: true, message: '请填写联系电话', trigger: 'blur' },
      { pattern: phoneReg, message: '手机号格式不对，请检查', trigger: 'blur' }
    ],
    fromRegionId: [
      {
        required: true,
        message: '请选择车现在的位置，找车的人靠它判断是否顺路',
        trigger: 'change'
      }
    ],
    windowStart: [
      { required: true, message: '请选择什么时候能装车', trigger: 'change' }
    ]
  });

  const boolField = (
    key:
      | 'anyDirection'
      | 'canInvoice'
      | 'hasInsurance'
      | 'platePublic'
      | 'keepListedAfterDeal'
  ) =>
    computed({
      get: () => form[key] === 1,
      set: (v: boolean) => (form[key] = v ? 1 : 0)
    });

  const anyDirection = boolField('anyDirection');
  const canInvoice = boolField('canInvoice');
  const hasInsurance = boolField('hasInsurance');
  const platePublic = boolField('platePublic');
  const keepListedAfterDeal = boolField('keepListedAfterDeal');

  /** 不能开票就没有票种可填，清掉避免留下一个矛盾的值 */
  watch(canInvoice, (v) => {
    if (!v) {
      form.invoiceType = null;
    }
  });

  const recap = computed(() => {
    if (isEdit.value && props.post) {
      return {
        totalQuantity: props.post.slotCount ?? props.post.totalQuantity
      };
    }
    return {
      totalQuantity: preview.value?.totalQuantity ?? form.slotCount ?? undefined
    };
  });

  const plateText = computed(() => {
    if (isEdit.value && props.post) {
      return props.post.plateNumber || props.post.plateMasked || '—';
    }
    return picked.value?.plateNumber || '—';
  });

  const driverText = computed(() => {
    if (isEdit.value && props.post) {
      return props.post.driverDisplay || '—';
    }
    return picked.value?.driverName || '—';
  });

  const headline = computed(
    () => preview.value?.title || props.post?.title || ''
  );
  const blocked = computed(() => !!preview.value?.precheck?.blocked);
  const blockMessage = computed(
    () => preview.value?.precheck?.blockMessage || '这台车现在还发不了'
  );
  const needsReview = computed(
    () => !blocked.value && !!preview.value?.precheck?.needsReview
  );

  const showSubmit = computed(
    () => !!options.value?.hallEnabled && (isEdit.value || !!capacityId.value)
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

  /**
   * 试算
   *
   * 位置、流向、时间、板位改一处就要重算标题，所以合成一个防抖调用。
   * 没选位置时不发请求：后端会以「地址不完整」拒绝，用户还在填的过程中，
   * 弹一句红字只会让人以为自己填错了。
   */
  let timer: ReturnType<typeof setTimeout> | null = null;

  const schedulePreview = () => {
    if (timer) {
      clearTimeout(timer);
    }
    timer = setTimeout(runPreview, 350);
  };

  const runPreview = async () => {
    const id = capacityId.value;
    if (!id || !form.fromRegionId) {
      return;
    }
    previewLoading.value = true;
    try {
      preview.value = await previewCapacity({
        capacityId: id,
        fromRegionId: form.fromRegionId,
        toRegionIds: form.toRegionIds,
        anyDirection: form.anyDirection,
        windowStart: form.windowStart,
        windowEnd: form.windowEnd,
        slotCount: form.slotCount
      });
    } catch (e: any) {
      preview.value = null;
      EleMessage.error({
        message: e?.message ?? '这台车暂时发不了',
        plain: true
      });
    } finally {
      previewLoading.value = false;
    }
  };

  const onPickCapacity = (capacity: Capacity) => {
    if (!capacity.id) {
      return;
    }
    picked.value = capacity;
    capacityId.value = capacity.id;
    schedulePreview();
  };

  const resetCapacity = () => {
    capacityId.value = null;
    picked.value = null;
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
      // 所在地与流向是发布时选的，详情接口按区划代码翻回了地区 ID
      fromRegionId: post.fromRegionId ?? null,
      toRegionIds: post.toRegionIds ?? [],
      anyDirection: post.anyDirection ?? 0,
      windowStart: post.windowStart ?? null,
      windowEnd: post.windowEnd ?? null,
      departureReadyAt: post.departureReadyAt ?? null,
      pickupRadius: post.pickupRadius ?? null,
      keepListedAfterDeal: post.keepListedAfterDeal ?? 0,
      settleRequire: post.settleRequire ?? null,
      slotCount: post.slotCount ?? null,
      platePublic: post.platePublic ?? 0,
      goodAtCategories: post.goodAtCategories ?? null,
      canInvoice: post.canInvoice ?? 0,
      invoiceType: post.invoiceType ?? null,
      hasInsurance: post.hasInsurance ?? 0,
      servicePromise: post.servicePromise ?? null
    });
  };

  const onOpen = async () => {
    Object.assign(form, emptyForm());
    preview.value = null;
    picked.value = null;
    capacityId.value = props.sourceCapacityId ?? null;
    formRef.value?.clearValidate();

    await loadOptions();
    if (isEdit.value && props.post) {
      fillFromPost(props.post);
      if (!props.post.fromRegionId) {
        EleMessage.warning({
          message: '这条挂牌原来选的位置已经查不到了，请重新选一次所在地',
          plain: true
        });
      }
    }
  };

  const save = () => {
    formRef.value?.validate?.(async (valid) => {
      if (!valid) {
        return;
      }
      if (!isEdit.value && !capacityId.value) {
        EleMessage.warning({ message: '请先选一台车', plain: true });
        return;
      }
      if (!form.anyDirection && !form.toRegionIds.length) {
        EleMessage.warning({
          message: '请选一下想跑的方向，或者勾上「哪都能去」',
          plain: true
        });
        return;
      }
      loading.value = true;
      const tip = EleMessage.loading({
        message: isEdit.value ? '正在保存修改，请稍候…' : '正在发布，请稍候…',
        plain: true
      });
      try {
        if (isEdit.value && props.post?.id) {
          const { data, message } = await editCapacityPost(props.post.id, form);
          EleMessage.success({
            message:
              message ||
              (data.requireReaudit
                ? '改动较大，这条信息会重新审核后再展示'
                : '已保存'),
            plain: true
          });
        } else {
          const { data, message } = await publishCapacity({
            ...form,
            capacityId: capacityId.value as number
          });
          EleMessage.success({
            message:
              message ||
              (data.autoListed
                ? '已发布，找车的同行现在就能看到'
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

  watch(
    () => props.visible,
    (v) => {
      if (!v) {
        if (timer) {
          clearTimeout(timer);
          timer = null;
        }
        preview.value = null;
        picked.value = null;
        capacityId.value = null;
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

  .eco-publish__direction {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;

    :deep(.el-cascader) {
      flex: 1;
    }
  }
</style>
