import type { ModuleOverviewConfig } from './types';
import heroBilling from '@/assets/overview/hero-billing.svg';

/** 计费中心总览配置 */
const billing: ModuleOverviewConfig = {
  key: 'billing',
  title: '计费中心',
  positioning:
    '计费中心维护运价合同、成本政策与费用模板，配置计费规则与运输线路，是运费收入与承运成本自动核算的规则中枢。',
  description:
    '在这里沉淀计费规则：维护运输线路与里程，签订客户运价合同与承运商合同，配置成本核算政策与费用模板，让计划产生的收入与成本可自动计算。',
  heroIllustration: heroBilling,
  accentColor: '#f08c00',
  moduleCards: [
    {
      path: '/billing/contract',
      icon: 'contract',
      desc: '管理客户运价合同与计费规则'
    },
    {
      path: '/billing/route',
      icon: 'route',
      desc: '维护运输线路及里程基础数据'
    },
    {
      path: '/billing/cost-policy',
      icon: 'money',
      desc: '配置承运成本核算政策'
    },
    {
      path: '/billing/carrier-contract',
      icon: 'contract',
      desc: '管理承运商运价合同'
    },
    {
      path: '/billing/fee-template',
      icon: 'template',
      desc: '定义可复用的费用项模板'
    }
  ],
  quickActions: [
    { title: '运价合同', path: '/billing/contract', primary: true },
    { title: '成本政策', path: '/billing/cost-policy' }
  ],
  tips: [
    '先维护线路与里程，运价合同与成本政策才能准确计算',
    '费用模板可减少重复配置，提高建单效率'
  ]
};

export default billing;
