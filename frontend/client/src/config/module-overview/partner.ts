import type { ModuleOverviewConfig } from './types';

/** 客商中心总览配置 */
const partner: ModuleOverviewConfig = {
  key: 'partner',
  title: '客商中心',
  positioning:
    '客商中心集中管理客户、承运商、供应商与经销商门店等业务伙伴档案与合作关系，是业务往来与结算的主数据源头。',
  description:
    '在这里建立并维护各类业务伙伴的基础档案、联系人与合作状态，支持承运商邀请协同与互联客户对接，为运单、计费与结算提供准确的主数据。',
  heroIcon: 'people',
  accentColor: '#0ca678',
  workflow: [
    {
      title: '建立档案',
      desc: '录入客户与承运商基础信息',
      icon: 'customer',
      path: '/partner/customer'
    },
    {
      title: '邀请协同',
      desc: '邀请承运商入驻并激活协同',
      icon: 'carrier',
      path: '/partner/carrier'
    },
    {
      title: '互联对接',
      desc: '打通互联客户的互通订单',
      icon: 'link',
      path: '/partner/inbound'
    },
    {
      title: '门店维护',
      desc: '维护经销商收发货门店网点',
      icon: 'store',
      path: '/partner/dealer'
    }
  ],
  moduleCards: [
    {
      path: '/partner/customer',
      icon: 'customer',
      desc: '管理客户档案、联系人与合作状态'
    },
    {
      path: '/partner/carrier',
      icon: 'carrier',
      desc: '管理承运商并支持邀请激活协同'
    },
    {
      path: '/partner/inbound',
      icon: 'link',
      desc: '对接互联客户的互通订单'
    },
    {
      path: '/partner/dealer',
      icon: 'store',
      desc: '维护经销商门店等收发货网点'
    }
  ],
  quickActions: [
    { title: '客户管理', path: '/partner/customer', primary: true },
    { title: '承运商管理', path: '/partner/carrier' }
  ],
  tips: [
    '客户与承运商信息是运单与结算的基础，建议尽早维护完整',
    '承运商可通过「邀请激活」快速入驻协同'
  ]
};

export default partner;
