<template>
  <div>
    <el-form ref="formRef" :model="form" label-width="0px" @submit.prevent="">
      <div style="padding: 6px 0 12px 0">
        <el-button
          :icon="PlusOutlined"
          type="primary"
          class="ele-btn-icon"
          @click="add"
        >
          新增一行
        </el-button>
        <el-button type="primary" @click="submit">提交</el-button>
      </div>
      <ele-data-table
        row-key="key"
        :columns="columns"
        :data="form.users"
        cell-class-name="editable-table-cell"
        class="editable-table"
      >
        <template #name="{ row, $index }">
          <el-form-item
            :prop="'users.' + $index + '.name'"
            :rules="{
              required: true,
              message: '请输入用户名',
              type: 'string',
              trigger: 'blur'
            }"
            class="form-error-popper"
            style="margin-bottom: 0"
          >
            <el-input
              v-if="row.isEdit"
              clearable
              v-model="row.name"
              placeholder="请输入用户名"
            />
            <div v-else class="editable-cell-text">{{ row.name }}</div>
          </el-form-item>
        </template>
        <template #number="{ row, $index }">
          <el-form-item
            :prop="'users.' + $index + '.number'"
            :rules="{
              required: true,
              message: '请输入工号',
              type: 'string',
              trigger: 'blur'
            }"
            class="form-error-popper"
            style="margin-bottom: 0"
          >
            <el-input
              v-if="row.isEdit"
              clearable
              v-model="row.number"
              placeholder="请输入工号"
            />
            <div v-else class="editable-cell-text">{{ row.number }}</div>
          </el-form-item>
        </template>
        <template #department="{ row, $index }">
          <el-form-item
            :prop="'users.' + $index + '.department'"
            :rules="{
              required: true,
              message: '请选择部门',
              type: 'string',
              trigger: 'change'
            }"
            class="form-error-popper"
            style="margin-bottom: 0"
          >
            <el-select
              v-if="row.isEdit"
              clearable
              v-model="row.department"
              placeholder="请选择部门"
              class="ele-fluid"
            >
              <el-option value="研发部" label="研发部" />
              <el-option value="测试部" label="测试部" />
              <el-option value="产品部" label="产品部" />
            </el-select>
            <div v-else class="editable-cell-text">{{ row.department }}</div>
          </el-form-item>
        </template>
        <template #action="{ row, $index }">
          <div style="display: inline; align-items: center">
            <el-link
              v-if="row.isEdit"
              type="success"
              underline="never"
              @click="done(row)"
            >
              完成
            </el-link>
            <el-link v-else type="primary" underline="never" @click="edit(row)">
              编辑
            </el-link>
            <el-divider direction="vertical" style="margin: 0 8px" />
            <el-link
              type="danger"
              underline="never"
              @click="remove(row, $index)"
            >
              删除
            </el-link>
          </div>
        </template>
      </ele-data-table>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive } from 'vue';
  import type { FormInstance } from 'element-plus';
  import { EleMessage } from 'ele-admin-plus';
  import type { Columns } from 'ele-admin-plus/es/ele-pro-table/types';
  import { PlusOutlined } from '@/components/icons';
  import type { UserItem } from '@/api/example/model';
  import { listAddedUsers } from '@/api/example';
  interface FormData {
    users: UserItem[];
  }

  /** 表单实例 */
  const formRef = ref<FormInstance | null>(null);

  /** 表单数据 */
  const form = reactive<FormData>({
    users: []
  });

  /** 表格列配置 */
  const columns = ref<Columns>([
    {
      type: 'index',
      columnKey: 'index',
      width: 50,
      align: 'center'
    },
    {
      columnKey: 'name',
      label: '用户名',
      minWidth: 120,
      slot: 'name'
    },
    {
      columnKey: 'number',
      label: '工号',
      minWidth: 120,
      slot: 'number'
    },
    {
      columnKey: 'department',
      label: '所属部门',
      minWidth: 120,
      slot: 'department'
    },
    {
      columnKey: 'action',
      label: '操作',
      width: 120,
      align: 'center',
      slot: 'action'
    }
  ]);

  /** 表单提交 */
  const submit = () => {
    formRef.value?.validate?.((valid, obj) => {
      if (!valid) {
        const errors = obj ? Object.keys(obj).length : 0;
        EleMessage.error({ message: `有 ${errors} 项校验不通过`, plain: true });
        return;
      }
      EleMessage.success({ message: '提交成功', plain: true });
    });
  };

  /** 添加 */
  const add = () => {
    form.users.push({
      key: `${Date.now()}-${form.users.length}`,
      number: '',
      name: '',
      department: void 0,
      isEdit: true
    });
  };

  /** 删除 */
  const remove = (_row: UserItem, index: number) => {
    form.users.splice(index, 1);
  };

  /** 编辑 */
  const edit = (row: UserItem) => {
    row.isEdit = true;
  };

  /** 完成 */
  const done = (row: UserItem) => {
    row.isEdit = false;
  };

  // 查询已添加
  listAddedUsers()
    .then((data) => {
      form.users = data;
    })
    .catch((e) => {
      EleMessage.error({ message: e.message, plain: true });
    });
</script>

<style lang="scss" scoped>
  .editable-table :deep(.editable-table-cell) {
    position: static;

    & > .cell {
      overflow: visible;
    }
  }

  .editable-cell-text {
    width: 100%;
    min-height: 32px;
    box-sizing: border-box;
  }

  .form-error-popper.is-error .editable-cell-text {
    border: 1px dashed var(--el-color-danger);
    border-radius: var(--el-border-radius-base);
  }

  /* 表单验证气泡形式 */
  .form-error-popper.el-form-item > :deep(.el-form-item__content) {
    & > .el-form-item__error {
      position: absolute;
      left: 0;
      top: auto;
      bottom: calc(100% + 6px);
      width: max-content;
      color: #fff;
      font-size: 12px;
      background: var(--el-color-danger);
      transition: all 0.2s;
      padding: 10px;
      border-radius: 4px;
      z-index: 999;
      transform: none;
      opacity: 0;
      visibility: hidden;
      pointer-events: none;

      &:after {
        content: '';
        border: 6px solid transparent;
        border-top-color: var(--el-color-danger);
        position: absolute;
        left: 12px;
        bottom: -11px;
      }
    }

    &:hover > .el-form-item__error {
      opacity: 1;
      visibility: visible;
      pointer-events: all;
    }
  }

  /* 第一行气泡显示在下 */
  .editable-table :deep(tbody > tr:first-child) {
    .el-form-item > .el-form-item__content > .el-form-item__error {
      bottom: auto;
      top: calc(100% + 6px);

      &:after {
        top: -11px;
        bottom: auto;
        border-bottom-color: var(--el-color-danger);
        border-top-color: transparent;
      }
    }

    /* 只有一行时气泡显示在右 */
    &:last-child {
      .el-form-item > .el-form-item__content > .el-form-item__error {
        top: 50%;
        right: auto;
        left: calc(100% + 6px);
        transform: translateY(-50%);

        &:after {
          top: auto;
          left: -11px;
          border-bottom-color: transparent;
          border-right-color: var(--el-color-danger);
        }
      }

      /* 最后一个单元格气泡显示在左 */
      & > td:last-child {
        .el-form-item > .el-form-item__content > .el-form-item__error {
          left: auto;
          right: calc(100% + 6px);

          &:after {
            left: auto;
            right: -11px;
            border-right-color: transparent;
            border-left-color: var(--el-color-danger);
          }
        }
      }
    }
  }
</style>
