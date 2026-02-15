<!-- 搜索表单 -->
<template>
  <ele-card :body-style="{ paddingBottom: '2px' }">
    <el-form label-width="72px" @keyup.enter="search" @submit.prevent="">
      <el-row :gutter="8">
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label="用户账号">
            <el-input
              clearable
              v-model.trim="form.username"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label="组织机构">
            <el-input
              clearable
              v-model.trim="form.organizationName"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col v-if="searchExpand" :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label="手机号">
            <el-input
              clearable
              v-model.trim="form.phone"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col v-if="searchExpand" :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label="邮箱">
            <el-input
              clearable
              v-model.trim="form.email"
              placeholder="请输入"
            />
          </el-form-item>
        </el-col>
        <el-col v-if="searchExpand" :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label="创建时间">
            <el-date-picker
              unlink-panels
              type="daterange"
              v-model="dateRange"
              range-separator="-"
              value-format="YYYY-MM-DD"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              class="ele-fluid"
            />
          </el-form-item>
        </el-col>
        <el-col :lg="8" :md="12" :sm="12" :xs="24">
          <el-form-item label-width="16px">
            <el-button type="primary" @click="search">查询</el-button>
            <el-button @click="reset">重置</el-button>
            <el-link
              type="primary"
              underline="never"
              @click="toggleExpand"
              style="margin-left: 12px"
            >
              <template v-if="searchExpand">
                <span>收起</span>
                <el-icon style="vertical-align: -1px">
                  <ArrowUp />
                </el-icon>
              </template>
              <template v-else>
                <span>展开</span>
                <el-icon style="vertical-align: -2px">
                  <ArrowDown />
                </el-icon>
              </template>
            </el-link>
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { ArrowDown, ArrowUp } from '@/components/icons';
  import { useFormData } from '@/utils/use-form-data';
  import type { UserParam } from '@/api/system/user/model';

  const emit = defineEmits<{
    (e: 'search', where?: UserParam): void;
  }>();

  /** 表单数据 */
  const [form, resetFields] = useFormData<UserParam>({
    username: '',
    organizationName: '',
    phone: '',
    email: ''
  });

  /** 日期范围 */
  const dateRange = ref<[string, string]>(['', '']);

  /** 搜索表单是否展开 */
  const searchExpand = ref(false);

  /** 搜索 */
  const search = () => {
    const [d1, d2] = dateRange.value ?? [];
    emit('search', {
      ...form,
      createTimeStart: d1 ? `${d1} 00:00:00` : '',
      createTimeEnd: d2 ? `${d2} 23:59:59` : ''
    });
  };

  /**  重置 */
  const reset = () => {
    resetFields();
    dateRange.value = ['', ''];
    search();
  };

  /** 搜索展开/收起 */
  const toggleExpand = () => {
    searchExpand.value = !searchExpand.value;
  };
</script>
