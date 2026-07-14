<!-- Banner 编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="640"
    :title="isUpdate ? '修改 Banner' : '新建 Banner'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      @submit.prevent=""
    >
      <el-form-item label="标题" prop="title">
        <el-input
          clearable
          :maxlength="100"
          v-model="form.title"
          placeholder="内部标题/运营备注名"
        />
      </el-form-item>

      <el-form-item label="图片" prop="image_url">
        <div class="banner-upload">
          <el-image
            v-if="form.image_url"
            :src="form.image_url"
            fit="cover"
            class="banner-upload__preview"
          />
          <el-upload
            action=""
            accept="image/*"
            :show-file-list="false"
            :before-upload="handleUpload"
          >
            <el-button>{{
              form.image_url ? '重新上传' : '上传图片'
            }}</el-button>
          </el-upload>
          <div class="banner-upload__tip"
            >建议尺寸 {{ BANNER_IMG_W }} × {{ BANNER_IMG_H }} px（宽高比
            {{
              BANNER_RATIO_LABEL
            }}，与客户端展示区一致），重要内容居中、两侧留白；支持
            jpg/png，≤10MB。上传后按展示区等比裁切、不变形。</div
          >
        </div>
      </el-form-item>

      <el-form-item label="跳转方式" prop="link_type">
        <el-radio-group v-model="form.link_type">
          <el-radio value="none">只看不跳</el-radio>
          <el-radio value="external">跳转外链</el-radio>
          <el-radio value="internal">站内路由</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="form.link_type !== 'none'"
        label="跳转地址"
        prop="link_url"
      >
        <el-input
          clearable
          :maxlength="500"
          v-model="form.link_url"
          :placeholder="
            form.link_type === 'external'
              ? 'https:// 开头的完整链接'
              : '/ 开头的站内路由，如 /dashboard/workplace'
          "
        />
      </el-form-item>

      <el-form-item v-if="form.link_type === 'external'" label="打开方式">
        <el-switch
          v-model="form.open_in_new_tab"
          :active-value="1"
          :inactive-value="0"
          active-text="新标签打开"
          inactive-text="当前页打开"
        />
      </el-form-item>

      <el-form-item label="投放范围" prop="target_type">
        <el-radio-group v-model="form.target_type" @change="onTargetTypeChange">
          <el-radio value="all">全部客户</el-radio>
          <el-radio value="version">按产品版本</el-radio>
          <el-radio value="tenant">指定租户</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="form.target_type === 'version'"
        label="选择版本"
        prop="target_values"
      >
        <el-select
          multiple
          v-model="form.target_values"
          placeholder="选择产品版本"
          class="ele-fluid"
        >
          <el-option
            v-for="opt in versionOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item
        v-if="form.target_type === 'tenant'"
        label="选择租户"
        prop="target_values"
      >
        <el-select
          multiple
          filterable
          remote
          reserve-keyword
          v-model="form.target_values"
          :remote-method="searchTenants"
          :loading="tenantLoading"
          placeholder="搜索并选择租户"
          class="ele-fluid"
        >
          <el-option
            v-for="opt in tenantOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="排序号" prop="sort_order">
        <el-input-number
          :min="0"
          :max="9999"
          v-model="form.sort_order"
          controls-position="right"
          placeholder="越小越靠前"
          class="ele-fluid"
        />
      </el-form-item>

      <el-form-item label="生效时间">
        <el-date-picker
          v-model="schedule"
          type="datetimerange"
          value-format="YYYY-MM-DD HH:mm:ss"
          range-separator="至"
          start-placeholder="开始（不填=不限）"
          end-placeholder="结束（不填=不限）"
          class="ele-fluid"
        />
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input
          :rows="3"
          type="textarea"
          :maxlength="255"
          v-model="form.remark"
          placeholder="选填"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => closeModal() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, reactive, watch } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, useModal } from 'ele-admin-plus';
  import { useFormData } from '@/utils/use-form-data';
  import { uploadFile } from '@/api/system/file';
  import {
    addBanner,
    updateBanner,
    getVersionOptions,
    getTenantOptions
  } from '@/api/promotion';
  import type { Banner, BannerOption } from '@/api/promotion/model';

  // 客户端展示区高度固定 216px，宽高比 5:1，推荐上传 1080×216
  const BANNER_IMG_W = 1080;
  const BANNER_IMG_H = 216;
  const BANNER_RATIO = BANNER_IMG_W / BANNER_IMG_H;
  const BANNER_RATIO_LABEL = '5:1';

  const props = defineProps<{ data?: Banner | null }>();
  const emit = defineEmits<{ (e: 'done'): void }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);

  const [form, , assignFields] = useFormData<Banner>({
    id: void 0,
    title: '',
    image_url: '',
    link_type: 'none',
    link_url: '',
    open_in_new_tab: 1,
    target_type: 'all',
    target_values: [],
    sort_order: 0,
    start_at: null,
    end_at: null,
    remark: ''
  });

  const schedule = ref<[string, string] | null>(null);

  const versionOptions = ref<BannerOption[]>([]);
  const tenantOptions = ref<BannerOption[]>([]);
  const tenantLoading = ref(false);

  const rules = reactive<FormRules>({
    title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
    image_url: [{ required: true, message: '请上传图片', trigger: 'change' }],
    link_url: [
      {
        validator: (_r, value, cb) => {
          if (form.link_type === 'none') return cb();
          if (!value) return cb(new Error('请输入跳转地址'));
          if (form.link_type === 'external' && !/^https?:\/\//.test(value)) {
            return cb(new Error('外链需以 http(s):// 开头'));
          }
          if (form.link_type === 'internal' && !value.startsWith('/')) {
            return cb(new Error('站内路由需以 / 开头'));
          }
          cb();
        },
        trigger: 'blur'
      }
    ],
    target_values: [
      {
        validator: (_r, value, cb) => {
          if (form.target_type !== 'all' && (!value || !value.length)) {
            return cb(new Error('请至少选择一项投放目标'));
          }
          cb();
        },
        trigger: 'change'
      }
    ]
  });

  // 校验图片宽高比是否接近展示区（5:1），偏差过大提示但不阻断
  const checkRatio = (file: File) => {
    return new Promise<void>((resolve) => {
      const url = URL.createObjectURL(file);
      const img = new Image();
      img.onload = () => {
        URL.revokeObjectURL(url);
        const ratio = img.width / img.height;
        if (Math.abs(ratio - BANNER_RATIO) / BANNER_RATIO > 0.15) {
          EleMessage.warning({
            message: `图片宽高比 ${ratio.toFixed(2)}:1 与展示区(${BANNER_RATIO_LABEL})差异较大，建议上传 ${BANNER_IMG_W}×${BANNER_IMG_H} px 以避免裁切`,
            plain: true
          });
        }
        resolve();
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        resolve();
      };
      img.src = url;
    });
  };

  const handleUpload = async (file: File) => {
    if (file.size / 1024 / 1024 > 10) {
      EleMessage.error({ message: '图片不能超过 10MB', plain: true });
      return false;
    }
    await checkRatio(file);
    const load = EleMessage.loading({ message: '上传中..', plain: true });
    uploadFile(file, void 0, void 0, 'banner')
      .then((res) => {
        load.close();
        form.image_url = res.url;
        formRef.value?.validateField?.('image_url');
        EleMessage.success({ message: '上传成功', plain: true });
      })
      .catch((e) => {
        load.close();
        EleMessage.error({ message: e.message, plain: true });
      });
    return false;
  };

  const onTargetTypeChange = () => {
    form.target_values = [];
  };

  const searchTenants = (keyword: string) => {
    tenantLoading.value = true;
    getTenantOptions(keyword)
      .then((list) => {
        tenantOptions.value = list;
      })
      .finally(() => {
        tenantLoading.value = false;
      });
  };

  watch(
    () => schedule.value,
    (val) => {
      form.start_at = val?.[0] || null;
      form.end_at = val?.[1] || null;
    }
  );

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const payload: Partial<Banner> = {
        title: form.title,
        image_url: form.image_url,
        link_type: form.link_type,
        link_url: form.link_type === 'none' ? null : form.link_url,
        open_in_new_tab: form.open_in_new_tab,
        target_type: form.target_type,
        target_values: form.target_type === 'all' ? null : form.target_values,
        sort_order: form.sort_order ?? 0,
        start_at: form.start_at,
        end_at: form.end_at,
        remark: form.remark
      };
      const req = isUpdate.value
        ? updateBanner(form.id!, payload)
        : addBanner(payload);
      req
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg as string, plain: true });
          emit('done');
          closeModal();
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  getVersionOptions().then((list) => {
    versionOptions.value = list;
  });
  getTenantOptions().then((list) => {
    tenantOptions.value = list;
  });

  if (props.data) {
    assignFields({
      ...props.data,
      target_values: props.data.target_values || []
    });
    if (props.data.start_at || props.data.end_at) {
      schedule.value = [props.data.start_at || '', props.data.end_at || ''];
    }
    isUpdate.value = true;
  }
</script>

<style lang="scss" scoped>
  .banner-upload {
    width: 100%;

    /* 预览按客户端展示区比例（5:1）渲染，所见即所得 */
    &__preview {
      width: 100%;
      max-width: 520px;
      aspect-ratio: 1080 / 216;
      border-radius: 6px;
      margin-bottom: 8px;
      display: block;
      border: 1px solid var(--el-border-color);
    }

    &__tip {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }
</style>
