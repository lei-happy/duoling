import type { ModuleOverviewConfig } from './types';
import heroOperation from '@/assets/overview/hero-operation.svg';

/** 运营调度总览配置 */
const operation: ModuleOverviewConfig = {
  key: 'operation',
  title: '运营调度',
  positioning:
    '运营调度是货物运输的作业中枢，串联“计划受理 - 配载建单 - 派车调度 - 在途监控 - 回单签收”的全流程，让每一单货都可建、可调、可控、可交付。',
  description:
    '在这里集中处理来自客户的运输需求：把计划配载成运输任务，为任务分配车辆与司机，跟踪在途轨迹并完成回单签收，形成从接单到交付的作业闭环。',
  heroIllustration: heroOperation,
  heroAspectRatio: 4,
  accentColor: '#3f7cff',
  workflow: [
    {
      title: '计划受理',
      desc: '录入或批量导入客户计划，进入计划池待配载',
      icon: 'waybill',
      path: '/operation/waybill'
    },
    {
      title: '配载建单',
      desc: '将计划手动或智能配载，生成运输任务单',
      icon: 'stowage',
      path: '/operation/task-create'
    },
    {
      title: '派车调度',
      desc: '在调度工作台为任务分配车辆与司机并下发',
      icon: 'dispatch',
      path: '/operation/task-workbench'
    },
    {
      title: '在途监控',
      desc: '实时跟踪车辆位置与运输进度，处理异常',
      icon: 'tracking',
      path: '/operation/tracking'
    },
    {
      title: '回单签收',
      desc: '上传确认回单，完成交付并归档待结算',
      icon: 'receipt',
      path: '/operation/receipt'
    }
  ],
  moduleCards: [
    {
      path: '/operation/waybill',
      icon: 'waybill',
      desc: '集中管理客户计划，支持新建、批量导入与计划池筛选'
    },
    {
      path: '/operation/stowage',
      icon: 'stowage',
      desc: '手动或智能配载，把计划生成运输任务单'
    },
    {
      path: '/operation/task-workbench',
      icon: 'dispatch',
      desc: '一站式完成派车、跟踪与异常处理'
    },
    {
      path: '/operation/tracking',
      icon: 'tracking',
      desc: '实时掌握车辆位置与运输进度'
    },
    {
      path: '/operation/receipt',
      icon: 'receipt',
      desc: '上传并确认回单，完成交付闭环'
    },
    {
      path: '/operation/completed-task',
      icon: 'completed',
      desc: '归档已完成任务，衔接后续费用结算'
    },
    {
      path: '/operation/task',
      icon: 'task',
      desc: '查看全部调度任务单及其状态流转'
    },
    {
      path: '/operation/alert-rule',
      icon: 'bell',
      desc: '设置各阶段超时多久提醒，可按客户、线路、车型分别放宽或收紧'
    }
  ],
  quickActions: [
    {
      title: '新建计划',
      path: '/operation/waybill?action=create',
      icon: 'waybill',
      primary: true
    },
    { title: '配载建单', path: '/operation/task-create', icon: 'stowage' },
    { title: '调度工作台', path: '/operation/task-workbench', icon: 'dispatch' }
  ],
  tips: [
    '首次使用建议先在「客商中心」维护客户与承运商信息',
    '大批量计划可通过计划中心的「批量导入」快速录入',
    '配载完成后在「调度工作台」统一派车，效率更高'
  ]
};

export default operation;
