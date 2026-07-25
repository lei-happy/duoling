<!--
  发布弹层的公共项：联系方式、展示时长、合作方式、报价、公开范围

  两个大厅的源单侧完全不同（任务单 / 运力档案），但「怎么联系我、展示多久、多少钱、
  给谁看」是同一套。抽出来的主要目的不是省代码，是让两个大厅的默认值与措辞一致：
  公开范围这种选项一旦两边说法不同，用户就会以为两个大厅的规则不一样。

  改动通过 `patch` 事件回给父组件，不直接改传进来的表单对象：表单归发布弹层所有，
  这里只是它的一段界面。
-->
<template>
  <div class="eco-fields">
    <el-divider content-position="left">怎么联系我</el-divider>
    <el-row :gutter="12">
      <el-col :md="8" :xs="24">
        <el-form-item label="联系人" prop="contactName">
          <el-input
            v-model="contactName"
            :maxlength="50"
            placeholder="对方看到的联系人"
          />
        </el-form-item>
      </el-col>
      <el-col :md="8" :xs="24">
        <el-form-item label="联系电话" prop="contactPhone">
          <el-input
            v-model="contactPhone"
            :maxlength="20"
            placeholder="能接到同行电话的号码"
          />
        </el-form-item>
      </el-col>
      <el-col :md="8" :xs="24">
        <el-form-item label="备用联系" prop="contactBackup">
          <el-input
            v-model="contactBackup"
            :maxlength="20"
            placeholder="选填，如微信同号"
          />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">展示与合作</el-divider>
    <el-row :gutter="12">
      <el-col v-if="showValidDays" :md="12" :xs="24">
        <el-form-item label="展示天数" prop="validDays">
          <el-radio-group v-model="validDays">
            <el-radio-button v-for="d in dayOptions" :key="d" :value="d">
              {{ d }} 天
            </el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :md="12" :xs="24">
        <el-form-item label="合作方式" prop="cooperationType">
          <el-radio-group v-model="cooperationType">
            <el-radio
              v-for="item in options.cooperationTypes || []"
              :key="item.value"
              :value="item.value"
            >
              {{ item.label }}
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">报价</el-divider>
    <el-row :gutter="12">
      <el-col :md="8" :xs="24">
        <el-form-item label="计价方式" prop="priceType">
          <el-select v-model="priceType" class="ele-fluid">
            <el-option
              v-for="item in options.priceTypes || []"
              :key="item.value"
              :value="item.value"
              :label="item.label"
            />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :md="8" :xs="24">
        <el-form-item label="金额" prop="priceAmount">
          <el-input-number
            v-model="priceAmount"
            class="ele-fluid"
            :min="1"
            :max="9999999"
            :precision="2"
            :controls="false"
            :disabled="priceDisabled"
            :placeholder="priceDisabled ? '面议不用填' : priceUnitHint"
          />
        </el-form-item>
      </el-col>
      <el-col :md="8" :xs="24">
        <el-form-item label="其他">
          <el-checkbox v-model="includeTax" label="含税" />
          <el-checkbox v-model="negotiable" label="可议价" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">给谁看</el-divider>
    <el-form-item label="公开范围">
      <div class="eco-fields__visibility">
        <el-radio-group v-model="visibility">
          <el-radio value="recommend">推荐</el-radio>
          <el-radio value="urgent">急单</el-radio>
        </el-radio-group>
        <div class="eco-fields__hint">{{ visibilityHint }}</div>
      </div>
    </el-form-item>
  </div>
</template>

<script lang="ts" setup>
  import { computed } from 'vue';
  import {
    PriceType,
    VALID_DAYS_FALLBACK,
    VisibilityLevel
  } from '@/config/ecosystem/enums';
  import type {
    EcoPostFormBase,
    EcoPublishOptions
  } from '@/api/ecosystem/post/model';

  const props = withDefaults(
    defineProps<{
      /** 只读：当前表单值 */
      form: EcoPostFormBase;
      /** /publish/options 的下发内容：可选项与默认值 */
      options: Partial<EcoPublishOptions>;
      /**
       * 编辑时传 false
       *
       * 有效期只有「延长展示」一条修改路径，编辑改不了它。留在表单里，用户选了
       * 30 天、保存成功、展示时间却没变，只会以为系统没保存。
       */
      showValidDays?: boolean;
    }>(),
    { showValidDays: true }
  );

  const emit = defineEmits<{
    (e: 'patch', patch: Partial<EcoPostFormBase>): void;
  }>();

  /** 每个输入框都是「读 props、写 patch」，表单对象始终由父组件持有 */
  function field<K extends keyof EcoPostFormBase>(key: K) {
    return computed({
      get: () => props.form[key],
      set: (v: EcoPostFormBase[K]) => emit('patch', { [key]: v } as any)
    });
  }

  const contactName = field('contactName');
  const contactPhone = field('contactPhone');
  const contactBackup = field('contactBackup');
  const validDays = field('validDays');
  const cooperationType = field('cooperationType');
  const priceType = computed({
    get: () => props.form.priceType,
    set: (v: number) =>
      // 切到面议就清掉已填金额，避免留下「面议 + 12000」这种自相矛盾的组合
      emit('patch', {
        priceType: v,
        ...(v === PriceType.NEGOTIABLE ? { priceAmount: null } : {})
      })
  });
  const priceAmount = field('priceAmount');

  const dayOptions = computed(() =>
    props.options.validDaysOptions?.length
      ? props.options.validDaysOptions
      : VALID_DAYS_FALLBACK
  );

  const priceDisabled = computed(
    () => props.form.priceType === PriceType.NEGOTIABLE
  );

  const priceUnitHint = computed(() => {
    switch (props.form.priceType) {
      case PriceType.PER_UNIT:
        return '每台多少钱';
      case PriceType.PER_KM:
        return '每公里多少钱';
      default:
        return '整车包多少钱';
    }
  });

  /** 0/1 与复选框之间的转换收在这里，表单里保持后端要的 0/1 */
  const includeTax = computed({
    get: () => props.form.priceIncludeTax === 1,
    set: (v: boolean) => emit('patch', { priceIncludeTax: v ? 1 : 0 })
  });

  const negotiable = computed({
    get: () => props.form.priceNegotiable === 1,
    set: (v: boolean) => emit('patch', { priceNegotiable: v ? 1 : 0 })
  });

  /**
   * 公开范围合成一个二选一
   *
   * 后端是「企业名可见范围」+「联系方式可见范围」两个字段，但让用户分别选这两项
   * 只会得到大量默认值——他关心的是「正常发」还是「急着要车，电话随便打」。
   * 界面上只给这两档，字段值在这里映射。
   */
  const visibility = computed({
    get: () =>
      props.form.contactVisibility === VisibilityLevel.CERTIFIED
        ? 'urgent'
        : 'recommend',
    set: (v: string) =>
      emit('patch', {
        visibilityLevel: VisibilityLevel.CERTIFIED,
        contactVisibility:
          v === 'urgent'
            ? VisibilityLevel.CERTIFIED
            : VisibilityLevel.NEGOTIATING
      })
  });

  const visibilityHint = computed(() =>
    visibility.value === 'urgent'
      ? '认证同行可以直接看到你的电话，联系会快一些，但打进来的电话也会多一些。'
      : '认证同行先在大厅里看到这条信息，对方表达合作意向后你们才互相看到联系方式。'
  );
</script>

<style lang="scss" scoped>
  .eco-fields {
    :deep(.el-divider__text) {
      font-size: 13px;
      font-weight: 600;
      color: var(--el-text-color-regular);
      background-color: var(--el-bg-color-overlay);
    }

    :deep(.el-divider--horizontal) {
      margin: 4px 0 18px;
    }
  }

  .eco-fields__visibility {
    line-height: 1.5;
  }

  .eco-fields__hint {
    margin-top: 2px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
</style>
