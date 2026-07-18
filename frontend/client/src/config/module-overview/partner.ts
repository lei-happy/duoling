import type { ModuleOverviewConfig } from './types';
import heroPartner from '@/assets/overview/hero-partner.svg';

/** 客商中心总览配置 */
const partner: ModuleOverviewConfig = {
  key: 'partner',
  title: '客商中心',
  positioning:
    '客商中心集中管理客户、承运商、供应商与经销商门店等业务伙伴档案与合作关系，是业务往来与结算的主数据源头。',
  description:
    '在这里建立并维护各类业务伙伴的基础档案、联系人与合作状态，支持承运商邀请协同与互联客户对接，为运单、计费与结算提供准确的主数据。',
  heroIllustration: heroPartner,
  accentColor: '#e14b8a',
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
