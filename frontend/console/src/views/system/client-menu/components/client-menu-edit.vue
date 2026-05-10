<!-- 客户端菜单编辑弹窗 -->
<template>
  <ele-modal
    form
    :width="780"
    :title="isUpdate ? '修改客户端菜单' : '添加客户端菜单'"
    :loading="loading"
    v-bind="modalProps"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      :validate-on-rule-change="false"
      @submit.prevent=""
    >
      <el-row :gutter="16">
        <el-col :sm="12" :xs="24">
          <el-form-item label="上级菜单" prop="parentId">
            <client-menu-select v-model="form.parentId" />
          </el-form-item>
          <el-form-item label="菜单名称" prop="title">
            <el-input
              clearable
              :maxlength="20"
              v-model="form.title"
              placeholder="请输入菜单名称"
            />
          </el-form-item>
          <el-form-item label="功能编码" prop="featureCode">
            <el-select
              v-model="form.featureCode"
              placeholder="请选择或输入功能编码"
              clearable
              filterable
              allow-create
              class="ele-fluid"
            >
              <el-option
                v-for="f in featureOptions"
                :key="f.featureCode"
                :label="`${f.featureCode} - ${f.featureName}`"
                :value="f.featureCode!"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item label="菜单类型" prop="menuType">
            <el-radio-group
              v-model="form.menuType"
              @change="handleMenuTypeChange"
            >
              <el-radio :value="0" label="目录" />
              <el-radio :value="1" label="菜单" />
              <el-radio :value="2" label="按钮" />
            </el-radio-group>
          </el-form-item>
          <el-form-item label="打开方式">
            <el-radio-group
              v-model="form.openType"
              :disabled="form.menuType === 0 || form.menuType === 2"
              @change="handleOpenTypeChange"
            >
              <el-radio :value="0" label="组件" />
              <el-radio :value="1" label="内嵌" />
              <el-radio :value="2" label="外链" />
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider style="margin: 8px 0 22px 0; opacity: 0.6" />
      <el-row :gutter="16">
        <el-col :sm="12" :xs="24">
          <el-form-item label="菜单图标" prop="icon">
            <el-input
              clearable
              :maxlength="50"
              v-model="form.icon"
              :disabled="form.menuType === 2"
              placeholder="如 CarOutlined"
            >
              <template v-if="form.icon" #prefix>
                <menu-icon-preview :icon="form.icon" />
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="path">
            <template #label>
              <ele-tooltip
                v-if="form.openType === 2"
                content="需要以`http://`、`https://`、`//`开头"
                placement="top-start"
                :popper-options="{
                  modifiers: [
                    { name: 'offset', options: { offset: [-12, 10] } }
                  ]
                }"
              >
                <el-icon
                  :size="15"
                  style="align-self: center; margin-right: 4px; cursor: help"
                >
                  <QuestionCircleOutlined style="opacity: 0.6" />
                </el-icon>
              </ele-tooltip>
              <span>{{ form.openType === 2 ? '外链地址' : '路由地址' }}</span>
            </template>
            <el-input
              clearable
              :maxlength="100"
              v-model="form.path"
              :disabled="form.menuType === 2"
              :placeholder="
                form.openType === 2 ? '请输入外链地址' : '如 /resource/vehicle'
              "
            />
          </el-form-item>
          <el-form-item prop="component">
            <template #label>
              <ele-tooltip
                v-if="form.openType === 1"
                content="需要以`http://`、`https://`、`//`开头"
                placement="top-start"
                :popper-options="{
                  modifiers: [
                    { name: 'offset', options: { offset: [-12, 10] } }
                  ]
                }"
              >
                <el-icon
                  :size="15"
                  style="align-self: center; margin-right: 4px; cursor: help"
                >
                  <QuestionCircleOutlined style="opacity: 0.6" />
                </el-icon>
              </ele-tooltip>
              <span>{{ form.openType === 1 ? '内嵌地址' : '组件路径' }}</span>
            </template>
            <el-input
              clearable
              :maxlength="100"
              v-model="form.component"
              :disabled="
                form.menuType === 0 ||
                form.menuType === 2 ||
                form.openType === 2
              "
              :placeholder="
                form.openType === 1
                  ? '请输入内嵌地址'
                  : '如 /resource/vehicle/index'
              "
            />
          </el-form-item>
        </el-col>
        <el-col :sm="12" :xs="24">
          <el-form-item label="权限标识" prop="authority">
            <el-input
              clearable
              v-model="form.authority"
              placeholder="如 resource:vehicle"
              :disabled="
                form.menuType === 0 ||
                (form.menuType === 1 && form.openType === 2)
              "
            />
          </el-form-item>
          <el-form-item label="排序号" prop="sortNumber">
            <el-input-number
              :min="0"
              :max="CLIENT_MENU_SORT_ORDER_MAX"
              v-model="form.sortNumber"
              placeholder="请输入排序号"
              controls-position="right"
              class="ele-fluid"
            />
          </el-form-item>
          <el-form-item label="是否展示">
            <el-switch
              inline-prompt
              active-text="是"
              inactive-text="否"
              :model-value="form.hide === 0"
              :disabled="form.menuType === 2"
              @change="updateHideValue"
            />
            <ele-tooltip
              content="选择不展示只注册路由不显示在客户端侧边栏"
              :popper-style="{ maxWidth: '240px' }"
            >
              <el-icon :size="15" style="margin-left: 16px; cursor: help">
                <QuestionCircleOutlined style="opacity: 0.6" />
              </el-icon>
            </ele-tooltip>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <btn-items
        :items="[
          { preset: 'cancel', onClick: () => handleCancel() },
          { preset: 'save', onClick: () => save() }
        ]"
      />
    </template>
  </ele-modal>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage, isExternalLink, useModal } from 'ele-admin-plus';
  import { QuestionCircleOutlined } from '@/components/icons';
  import { useFormData } from '@/utils/use-form-data';
  import MenuIconPreview from '@/components/IconSelect/components/menu-icon.vue';
  import ClientMenuSelect from './client-menu-select.vue';
  import { addClientMenu, updateClientMenu } from '@/api/system/client-menu';
  import { listFeatures } from '@/api/product';
  import type { ClientMenu } from '@/api/system/client-menu/model';
  import type { ProductFeature } from '@/api/product/model';

  const props = defineProps<{
    data?: ClientMenu | null;
    parentId?: number;
  }>();

  const emit = defineEmits<{
    (e: 'done'): void;
  }>();

  const { modalProps, closeModal } = useModal();

  const isUpdate = ref(false);
  const loading = ref(false);
  const formRef = ref<FormInstance | null>(null);
  const featureOptions = ref<ProductFeature[]>([]);

  /** 与后端 sys_menu.sort_order（SmallInteger）一致，超出会写入失败 */
  const CLIENT_MENU_SORT_ORDER_MAX = 32767;

  const [form, _resetFields, assignFields] = useFormData<ClientMenu>({
    menuId: void 0,
    parentId: props.parentId,
    title: '',
    menuType: 0,
    openType: 0,
    icon: '',
    path: '',
    component: '',
    authority: '',
    sortNumber: void 0,
    hide: 0,
    featureCode: ''
  });

  const rules = computed<FormRules>(() => {
    const obj: FormRules = {
      title: [
        {
          required: true,
          type: 'string',
          message: '请输入菜单名称',
          trigger: 'blur'
        }
      ],
      sortNumber: [
        {
          required: true,
          type: 'number',
          message: '请输入排序号',
          trigger: 'blur'
        },
        {
          type: 'number',
          min: 0,
          max: CLIENT_MENU_SORT_ORDER_MAX,
          message: `排序号范围为 0～${CLIENT_MENU_SORT_ORDER_MAX}`,
          trigger: 'blur'
        }
      ]
    };
    if (form.menuType !== 2) {
      obj.path = [
        {
          required: true,
          type: 'string',
          message: form.openType === 2 ? '请输入外链地址' : '请输入路由地址',
          trigger: 'blur'
        },
        {
          type: 'string',
          validator: (_rule: any, value: string, callback: any) => {
            if (value) {
              if (form.openType === 2) {
                if (!isExternalLink(value)) {
                  callback('请输入正确的链接地址');
                  return;
                }
              } else {
                if (value === '/') {
                  callback('路由地址不能为 /');
                  return;
                }
                if (!value.startsWith('/')) {
                  callback('路由地址需要以 / 开头');
                  return;
                }
              }
            }
            callback();
          },
          trigger: 'blur'
        }
      ];
      if (form.menuType === 1 && form.openType !== 2) {
        obj.component = [
          {
            required: true,
            type: 'string',
            message:
              form.openType === 1 ? '请输入内嵌地址' : '请输入组件路径',
            trigger: 'blur'
          },
          {
            type: 'string',
            validator: (_rule: any, value: string, callback: any) => {
              if (value) {
                if (form.openType === 1) {
                  if (!isExternalLink(value)) {
                    callback('请输入正确的链接地址');
                    return;
                  }
                }
              }
              callback();
            },
            trigger: 'blur'
          }
        ];
      }
    }
    return obj;
  });

  const handleCancel = () => {
    closeModal();
  };

  const save = () => {
    formRef.value?.validate?.((valid) => {
      if (!valid) return;
      loading.value = true;
      const saveOrUpdate = isUpdate.value ? updateClientMenu : addClientMenu;
      saveOrUpdate({
        ...form,
        menuType: form.menuType === 2 ? 1 : 0,
        parentId: form.parentId || 0
      })
        .then((msg) => {
          loading.value = false;
          EleMessage.success({ message: msg, plain: true });
          handleCancel();
          emit('done');
        })
        .catch((e) => {
          loading.value = false;
          EleMessage.error({ message: e.message, plain: true });
        });
    });
  };

  const handleMenuTypeChange = () => {
    if (form.menuType === 0) {
      form.authority = '';
      form.openType = 0;
      form.component = '';
    } else if (form.menuType === 1) {
      if (form.openType === 2) {
        form.authority = '';
      }
    } else {
      form.openType = 0;
      form.icon = '';
      form.path = '';
      form.component = '';
      form.hide = 0;
    }
    formRef.value?.clearValidate?.();
  };

  const handleOpenTypeChange = () => {
    if (form.openType === 2) {
      form.component = '';
      form.authority = '';
    }
    formRef.value?.clearValidate?.();
  };

  const updateHideValue = (value: boolean) => {
    form.hide = value ? 0 : 1;
  };

  const isDirectory = (d: ClientMenu) => {
    return !!d.children?.length && !d.component;
  };

  onMounted(() => {
    listFeatures()
      .then((list) => {
        featureOptions.value = list;
      })
      .catch(() => {});
  });

  if (props.data) {
    const isExternal = isExternalLink(props.data.path);
    const isInner = isExternalLink(props.data.component);
    const menuType =
      props.data.menuType === 1 ? 2 : isDirectory(props.data) ? 0 : 1;
    assignFields({
      ...props.data,
      menuType,
      openType: isExternal ? 2 : isInner ? 1 : 0,
      parentId: props.data.parentId === 0 ? void 0 : props.data.parentId
    });
    isUpdate.value = true;
  }
</script>
