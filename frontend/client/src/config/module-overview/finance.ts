import type { ModuleOverviewConfig } from './types';
import heroFinance from '@/assets/overview/hero-finance.svg';

/** 财务结算总览配置 */
const finance: ModuleOverviewConfig = {
  key: 'finance',
  title: '财务结算',
  positioning:
    '财务结算围绕应收、应付、对账、发票与利润展开，衔接运营与计费数据，完成从费用确认到收付款与利润分析的资金闭环。',
  description:
    '在这里处理任务应付费用、管理客户应收账款，与客户及承运商对账核销，开具管理发票，并分析收入成本与利润，形成完整资金闭环。',
  heroIllustration: heroFinance,
  accentColor: '#099268',
  moduleCards: [
    {
      path: '/finance/cashier-workbench',
      icon: 'money',
      desc: '看钱在哪、批量打款与到账认领'
    },
    {
      path: '/finance/invoice-workbench',
      icon: 'invoice',
      desc: '盯待开票与待收票的缺口'
    },
    {
      path: '/finance/recon-workbench',
      icon: 'reconcile',
      desc: '按客户看待对账运单与差异'
    },
    {
      path: '/finance/customer-recon',
      icon: 'reconcile',
      desc: '与客户核对运单与金额'
    },
    {
      path: '/finance/customer-settlement',
      icon: 'money',
      desc: '确认应收金额并登记收款'
    },
    {
      path: '/finance/customer-invoice',
      icon: 'invoice',
      desc: '按结算单开销项票与红冲'
    },
    {
      path: '/finance/ar-aging',
      icon: 'receivable',
      desc: '看欠款账龄与信用预警'
    },
    {
      path: '/finance/carrier-recon',
      icon: 'reconcile',
      desc: '与承运商核对任务与成本'
    },
    {
      path: '/finance/carrier-settlement',
      icon: 'payable',
      desc: '确认应付金额并登记付款'
    },
    {
      path: '/finance/vendor-invoice',
      icon: 'invoice',
      desc: '登记进项票并核销到结算单'
    },
    {
      path: '/finance/driver-payroll',
      icon: 'driver',
      desc: '算自有司机提成与实发工资'
    },
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
      path: '/finance/fund-flow',
      icon: 'money',
      desc: '查收付款流水与银行流水号'
    },
    {
      path: '/finance/bank-account',
      icon: 'money',
      desc: '维护收付账户与账面余额'
    },
    {
      path: '/finance/profit',
      icon: 'profit',
      desc: '按财务确认口径核算收入成本毛利'
    }
  ],
  quickActions: [
    { title: '出纳工作台', path: '/finance/cashier-workbench', primary: true },
    { title: '客户对账单', path: '/finance/customer-recon' },
    { title: '客户结算单', path: '/finance/customer-settlement' },
    { title: '经营核算', path: '/finance/profit' }
  ],
  tips: [
    '费用数据来自运营与计费，建议在结算前完成任务归档',
    '对账核销后再开具发票，账目更清晰',
    '经营核算只认已确认的收入与已审批的成本，与经营驾驶舱的理论毛利口径不同'
  ]
};

export default finance;
