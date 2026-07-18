import type { ModuleOverviewConfig } from './types';

/** 财务结算总览配置 */
const finance: ModuleOverviewConfig = {
  key: 'finance',
  title: '财务结算',
  positioning:
    '财务结算围绕应收、应付、对账、发票与利润展开，衔接运营与计费数据，完成从费用确认到收付款与利润分析的资金闭环。',
  description:
    '在这里处理任务应付费用、管理客户应收账款，与客户及承运商对账核销，开具管理发票，并分析收入成本与利润，形成完整资金闭环。',
  heroIcon: 'money',
  accentColor: '#099268',
  workflow: [
    {
      title: '应收管理',
      desc: '管理客户应收账款',
      icon: 'receivable',
      path: '/finance/receivable'
    },
    {
      title: '费用结算',
      desc: '集中处理任务应付费用',
      icon: 'money',
      path: '/operation/task-finance-workbench'
    },
    {
      title: '对账核销',
      desc: '与客户、承运商对账核销',
      icon: 'reconcile',
      path: '/finance/reconciliation'
    },
    {
      title: '发票开具',
      desc: '开具与管理发票',
      icon: 'invoice',
      path: '/finance/invoice'
    },
    {
      title: '利润分析',
      desc: '分析收入、成本与利润',
      icon: 'profit',
      path: '/finance/profit'
    }
  ],
  moduleCards: [
    {
      path: '/operation/task-finance-workbench',
      icon: 'money',
      desc: '集中处理任务应付费用'
    },
    {
      path: '/operation/task-finance',
      icon: 'list',
      desc: '查看应付费用单台账'
    },
    {
      path: '/finance/receivable',
      icon: 'receivable',
      desc: '管理客户应收账款'
    },
    {
      path: '/finance/reconciliation',
      icon: 'reconcile',
      desc: '与客户、承运商对账核销'
    },
    {
      path: '/finance/invoice',
      icon: 'invoice',
      desc: '开具与管理发票'
    },
    {
      path: '/finance/profit',
      icon: 'profit',
      desc: '分析收入、成本与利润'
    }
  ],
  quickActions: [
    { title: '应收管理', path: '/finance/receivable', primary: true },
    { title: '对账中心', path: '/finance/reconciliation' }
  ],
  tips: [
    '费用数据来自运营与计费，建议在结算前完成任务归档',
    '对账核销后再开具发票，账目更清晰'
  ]
};

export default finance;
