<template>
  <ele-card header="使用案例">
    <el-form label-width="80px" style="max-width: 320px">
      <el-form-item label="甲方">
        <el-input clearable v-model="form.partyA" />
      </el-form-item>
      <el-form-item label="乙方">
        <el-input clearable v-model="form.partyB" />
      </el-form-item>
      <el-form-item label="房屋地址">
        <el-input clearable v-model="form.address" />
      </el-form-item>
      <el-form-item label="打印位置">
        <el-select class="ele-fluid" v-model="option2.target">
          <el-option value="_iframe" label="子窗口" />
          <el-option value="_self" label="当前窗口" />
        </el-select>
      </el-form-item>
      <el-form-item label="始终显示">
        <el-radio-group v-model="option2.static">
          <el-radio :value="false" label="否" />
          <el-radio :value="true" label="是" />
        </el-radio-group>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handlePrint2">打印</el-button>
      </el-form-item>
    </el-form>
    <contract-content
      ref="contractRef"
      :data="contractData"
      :is-static="option2.static"
      :target="option2.target"
    />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref, reactive, nextTick } from 'vue';
  import type {
    PrintDirection,
    PrintOrientation,
    PrintTarget
  } from 'ele-admin-plus/es/ele-printer/types';
  import type { Project, Contract } from '@/api/example/model';
  import ContractContent from './contract-content.vue';
  import dayjs from 'dayjs';

  interface Option {
    direction?: PrintDirection;
    orientation?: PrintOrientation;
    margin: string;
    title: string;
    target: PrintTarget;
    static: boolean;
  }

  /** 项目进度数据 */
  const projectList = ref<Project[]>([]);

  /** 查询项目进度 */
  const queryProjectList = () => {
    projectList.value = [
      {
        id: '1',
        projectName: '项目000000001',
        status: 0,
        startDate: '2020-03-01',
        endDate: '2020-06-01',
        progress: 30,
        money: 3
      },
      {
        id: '2',
        projectName: '项目000000002',
        status: 0,
        startDate: '2020-03-01',
        endDate: '2020-08-01',
        progress: 10,
        money: 5
      },
      {
        id: '3',
        projectName: '项目000000003',
        status: 1,
        startDate: '2020-01-01',
        endDate: '2020-05-01',
        progress: 60,
        money: 2
      },
      {
        id: '4',
        projectName: '项目000000004',
        status: 1,
        startDate: '2020-06-01',
        endDate: '2020-10-01',
        progress: 0,
        money: 4
      },
      {
        id: '5',
        projectName: '项目000000005',
        status: 2,
        startDate: '2020-03-01',
        endDate: '2020-07-01',
        progress: 100,
        money: 1
      },
      {
        id: '6',
        projectName: '项目000000006',
        status: 3,
        startDate: '2020-02-01',
        endDate: '2020-06-01',
        progress: 100,
        money: 6
      }
    ];
  };

  queryProjectList();

  /** 表单数据 */
  const form = reactive({
    partyA: 'XX房屋租赁有限公司',
    partyB: '张三',
    address: 'XX省XX市XX区XX街道XX小区18栋一单元1104室'
  });

  /** 打印参数 */
  const option2 = reactive<Pick<Option, 'target' | 'static'>>({
    target: '_iframe',
    static: false
  });

  /** 获取合同数据 */
  const getContractData = () => {
    return {
      ...form,
      date: dayjs().format('YYYY-MM-DD'),
      projects: [
        ...projectList.value,
        ...projectList.value,
        ...projectList.value,
        ...projectList.value
      ].map((d, i) => {
        return { ...d, id: `${d.id}_${i}`, projectName: d.projectName + i };
      })
    };
  };

  /** 合同组件 */
  const contractRef = ref<InstanceType<typeof ContractContent> | null>(null);

  /** 合同数据 */
  const contractData = ref<Contract | null>(getContractData());

  /** 打印合同 */
  const handlePrint2 = () => {
    contractData.value = getContractData();
    nextTick(() => {
      contractRef.value && contractRef.value.print();
    });
  };
</script>
