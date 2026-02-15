<template>
  <ele-page plain :multi-card="false">
    <ele-card style="border-radius: 0">
      <ele-text type="heading" size="lg">复杂表单</ele-text>
      <ele-text type="placeholder" style="margin-top: 6px">
        复杂表单常见于一次性输入和提交大批量数据的场景。
      </ele-text>
    </ele-card>
    <ele-page>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        :scroll-to-error="true"
        @submit.prevent=""
      >
        <ele-card
          header="仓库信息"
          :body-style="{ padding: '24px 20px 8px 2px' }"
        >
          <el-row :gutter="12">
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="仓库名" prop="name">
                <el-input
                  maxlength="40"
                  clearable
                  v-model="form.name"
                  placeholder="请输入仓库名"
                />
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="仓库域名" prop="url">
                <el-input clearable v-model="form.url" placeholder="请输入">
                  <template #prepend>https://</template>
                  <template #append>.com</template>
                </el-input>
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="仓库管理员" prop="administrator">
                <el-select
                  clearable
                  v-model="form.administrator"
                  placeholder="请选择仓库管理员"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="1" label="SunSmile" />
                  <el-option value="2" label="Jasmine" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="审批人" prop="approver">
                <el-select
                  clearable
                  v-model="form.approver"
                  placeholder="请选择审批人"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="1" label="SunSmile" />
                  <el-option value="2" label="Jasmine" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="生效时间" prop="datetime">
                <el-date-picker
                  type="datetime"
                  v-model="form.datetime"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  placeholder="请选择生效时间"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                />
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="仓库类型" prop="type">
                <el-select
                  clearable
                  v-model="form.type"
                  placeholder="请选择仓库类型"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="private" label="私密" />
                  <el-option value="public" label="公开" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </ele-card>
        <ele-card
          header="任务信息"
          :body-style="{ padding: '24px 20px 8px 2px' }"
        >
          <el-row :gutter="12">
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="任务名" prop="task">
                <el-input
                  clearable
                  v-model="form.task"
                  placeholder="请输入任务名"
                />
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="任务表述" prop="description">
                <el-input
                  clearable
                  v-model="form.description"
                  placeholder="请输入任务表述"
                />
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="执行人" prop="executor">
                <el-select
                  clearable
                  v-model="form.executor"
                  placeholder="请选择执行人"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="1" label="SunSmile" />
                  <el-option value="2" label="Jasmine" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="责任人" prop="officer">
                <el-select
                  clearable
                  v-model="form.officer"
                  placeholder="请选择责任人"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="1" label="SunSmile" />
                  <el-option value="2" label="Jasmine" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="提醒时间" prop="reminder">
                <el-time-picker
                  is-range
                  range-separator="-"
                  v-model="form.reminder"
                  start-placeholder="开始时间"
                  end-placeholder="结束时间"
                  value-format="HH:mm:ss"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                />
              </el-form-item>
            </el-col>
            <el-col :lg="8" :md="12" :sm="12" :xs="24">
              <el-form-item label="任务类型" prop="taskType">
                <el-select
                  clearable
                  v-model="form.taskType"
                  placeholder="请选择任务类型"
                  class="ele-fluid"
                  :popper-options="{ strategy: 'fixed' }"
                >
                  <el-option value="1" label="私密" />
                  <el-option value="2" label="公开" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </ele-card>
        <ele-card header="选择成员">
          <div
            ref="userTableWrapRef"
            style="overflow: auto"
            :class="[
              'user-table-wrap',
              { 'is-ping-left': isPingLeft },
              { 'is-ping-right': isPingRight }
            ]"
            @scroll="handleUserTableScroll"
          >
            <ele-table style="min-width: 580px; table-layout: fixed">
              <colgroup>
                <col width="60px" />
                <col />
                <col />
                <col />
                <col width="100px" />
              </colgroup>
              <thead>
                <tr>
                  <th class="user-table-index"></th>
                  <th>用户名</th>
                  <th>工号</th>
                  <th>所属部门</th>
                  <th class="user-table-action">操作</th>
                </tr>
              </thead>
              <tbody style="--ele-table-padding: 6px 8px">
                <tr v-for="(row, index) in form.users" :key="row.key">
                  <td class="user-table-index">{{ index + 1 }}</td>
                  <td>
                    <el-form-item
                      label-width="0px"
                      :prop="'users.' + index + '.name'"
                      :rules="{
                        required: true,
                        message: '请输入用户名',
                        type: 'string',
                        trigger: 'blur'
                      }"
                      class="pro-form-error-popper"
                      style="margin-bottom: 0"
                    >
                      <el-input
                        clearable
                        v-model="row.name"
                        placeholder="请输入用户名"
                      />
                    </el-form-item>
                  </td>
                  <td>
                    <el-form-item
                      label-width="0px"
                      :prop="'users.' + index + '.number'"
                      :rules="{
                        required: true,
                        message: '请输入工号',
                        type: 'string',
                        trigger: 'blur'
                      }"
                      class="pro-form-error-popper"
                      style="margin-bottom: 0"
                    >
                      <el-input
                        clearable
                        v-model="row.number"
                        placeholder="请输入工号"
                      />
                    </el-form-item>
                  </td>
                  <td>
                    <el-form-item
                      label-width="0px"
                      :prop="'users.' + index + '.department'"
                      :rules="{
                        required: true,
                        message: '请选择部门',
                        type: 'string',
                        trigger: 'change'
                      }"
                      class="pro-form-error-popper"
                      style="margin-bottom: 0"
                    >
                      <el-select
                        clearable
                        v-model="row.department"
                        placeholder="请选择部门"
                        class="ele-fluid"
                        :popper-options="{ strategy: 'fixed' }"
                      >
                        <el-option value="研发部" label="研发部" />
                        <el-option value="测试部" label="测试部" />
                        <el-option value="产品部" label="产品部" />
                      </el-select>
                    </el-form-item>
                  </td>
                  <td class="user-table-action">
                    <el-link
                      type="danger"
                      underline="never"
                      @click="removeUser(row, index)"
                    >
                      删除
                    </el-link>
                  </td>
                </tr>
                <tr v-if="!form.users || !form.users.length">
                  <td colspan="5" style="text-align: center">
                    <ele-text style="padding: 4px 0" type="secondary">
                      暂无数据
                    </ele-text>
                  </td>
                </tr>
              </tbody>
            </ele-table>
          </div>
          <el-button
            :icon="PlusOutlined"
            style="margin-top: 16px; width: 100%"
            @click="addUser"
          >
            <span style="padding-top: 1px">新增成员</span>
          </el-button>
        </ele-card>
      </el-form>
    </ele-page>
    <!-- 底部工具栏 -->
    <ele-bottom-bar teleported>
      <ele-text v-if="validMsg" type="danger" :icon="CloseCircleOutlined">
        <span>{{ validMsg }}</span>
      </ele-text>
      <template #extra>
        <el-button type="primary" :loading="loading" @click="submit">
          提交
        </el-button>
      </template>
    </ele-bottom-bar>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import type { FormInstance, FormRules } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import { CloseCircleOutlined, PlusOutlined } from '@/components/icons';
  import { useFormData } from '@/utils/use-form-data';
  import type { UserItem } from '@/api/example/model';
  import { listAddedUsers } from '@/api/example';

  defineOptions({ name: 'FormAdvanced' });

  /** 加载状态 */
  const loading = ref(false);

  /** 表单数据类型 */
  interface FormData {
    name?: string;
    url?: string;
    administrator?: string;
    approver?: string;
    datetime?: string;
    type?: string;
    task?: string;
    description?: string;
    executor?: string;
    officer?: string;
    reminder?: [string, string];
    taskType?: string;
    users: UserItem[];
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const [form, resetFields] = useFormData<FormData>({
    name: '',
    url: '',
    administrator: void 0,
    approver: void 0,
    datetime: '',
    type: void 0,
    task: '',
    description: '',
    executor: void 0,
    officer: void 0,
    reminder: void 0,
    taskType: void 0,
    users: []
  });

  /** 表单验证规则 */
  const rules = reactive<FormRules>({
    name: [
      {
        required: true,
        message: '请输入仓库名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    url: [
      {
        required: true,
        message: '请输入仓库域名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    administrator: [
      {
        required: true,
        message: '请选择仓库管理员',
        type: 'string',
        trigger: 'change'
      }
    ],
    approver: [
      {
        required: true,
        message: '请选择审批人',
        type: 'string',
        trigger: 'change'
      }
    ],
    datetime: [
      {
        required: true,
        message: '请选择生效时间',
        type: 'string',
        trigger: 'blur'
      }
    ],
    type: [
      {
        required: true,
        message: '请选择仓库类型',
        type: 'string',
        trigger: 'change'
      }
    ],
    task: [
      {
        required: true,
        message: '请输入任务名',
        type: 'string',
        trigger: 'blur'
      }
    ],
    description: [
      {
        required: true,
        message: '请输入任务表述',
        type: 'string',
        trigger: 'blur'
      }
    ],
    executor: [
      {
        required: true,
        message: '请选择执行人',
        type: 'string',
        trigger: 'change'
      }
    ],
    officer: [
      {
        required: true,
        message: '请选择责任人',
        type: 'string',
        trigger: 'change'
      }
    ],
    reminder: [
      {
        required: true,
        message: '请选择提醒时间',
        type: 'array',
        trigger: 'change'
      }
    ],
    taskType: [
      {
        required: true,
        message: '请选择任务类型',
        type: 'string',
        trigger: 'change'
      }
    ]
  });

  /** 表单验证失败提示信息 */
  const validMsg = ref('');

  /** 表单提交 */
  const submit = () => {
    formRef.value?.validate?.((valid, obj) => {
      if (!valid) {
        const errors = obj ? Object.keys(obj).length : 0;
        validMsg.value = ` 共有 ${errors} 项校验不通过`;
        return;
      }
      validMsg.value = '';
      loading.value = true;
      setTimeout(() => {
        loading.value = false;
        EleMessage.success({ message: '提交成功', plain: true });
        resetFields();
      }, 1000);
    });
  };

  /** 添加 */
  const addUser = () => {
    form.users.push({
      key: `${Date.now()}-${form.users.length}`,
      number: '',
      name: '',
      department: void 0
    });
  };

  /** 删除 */
  const removeUser = (_row: UserItem, index: number) => {
    form.users.splice(index, 1);
  };

  /** 查询已添加 */
  listAddedUsers()
    .then((data) => {
      form.users = data;
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });

  /** 选择成员表格容器 */
  const userTableWrapRef = ref<HTMLDivElement | null>(null);

  /** 选择成员表格左侧列是否固定状态 */
  const isPingLeft = ref(false);

  /** 选择成员表格右侧列是否固定状态 */
  const isPingRight = ref(false);

  /** 选择成员表格滚动事件 */
  const handleUserTableScroll = (e: MouseEvent) => {
    checkUserTablePing(e.currentTarget as any);
  };

  /** 计算选择成员表格列固定状态 */
  const checkUserTablePing = (wrapEl: HTMLDivElement) => {
    const scrollLeft = wrapEl.scrollLeft;
    isPingLeft.value = scrollLeft > 1;
    const sw = wrapEl.scrollWidth - wrapEl.clientWidth - 1;
    isPingRight.value = sw > 1 && scrollLeft < sw;
  };

  onMounted(() => {
    userTableWrapRef.value && checkUserTablePing(userTableWrapRef.value);
  });
</script>

<style lang="scss" scoped>
  .user-table-wrap {
    :deep(.user-table-index) {
      text-align: center;
      position: sticky;
      left: 0;
      z-index: 98;
    }

    &.is-ping-left :deep(.user-table-index) {
      backdrop-filter: var(--ele-table-fixed-backdrop-filter);

      &::before {
        content: '';
        width: 10px;
        position: absolute;
        top: 0;
        bottom: -1px;
        right: -10px;
        box-shadow: var(--ele-table-fixed-left-shadow);
        transition: box-shadow 0.2s;
        pointer-events: none;
      }

      &::after {
        display: none;
      }
    }

    :deep(.user-table-action) {
      text-align: center;
      position: sticky;
      right: 0;
      z-index: 98;
    }

    &.is-ping-right :deep(.user-table-action) {
      backdrop-filter: var(--ele-table-fixed-backdrop-filter);

      &::before {
        content: '';
        width: 10px;
        position: absolute;
        top: 0;
        bottom: -1px;
        left: -10px;
        box-shadow: var(--ele-table-fixed-right-shadow);
        transition: box-shadow 0.2s;
        pointer-events: none;
      }
    }
  }
</style>
