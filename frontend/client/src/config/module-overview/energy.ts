import type { ModuleOverviewConfig } from './types';
import heroEnergy from '@/assets/overview/hero-energy.svg';

const energy: ModuleOverviewConfig = {
  key: 'energy',
  title: '能源中心',
  positioning:
    '能源中心统一管理油、气、电的账户、消费流水与对账，帮车队看清钱在哪、花在哪。',
  description:
    '把供应商账户、能源卡、充值和加油/加气/充电流水收拢到一本账。油补是付给司机的补贴，这里记的是付给供应商的能源费，两笔钱不重复。',
  heroIllustration: heroEnergy,
  accentColor: '#2f8f7d',
  moduleCards: [
    { path: '/energy/account', icon: 'money', desc: '看清各供应商账户余额与沉淀资金' },
    { path: '/energy/card', icon: 'list', desc: '管理能源卡并绑定车辆、司机' },
    { path: '/energy/recharge', icon: 'money', desc: '登记向供应商的充值入账' },
    { path: '/energy/consumption', icon: 'list', desc: '归集加油、加气、充电流水' },
    { path: '/energy/connector', icon: 'box', desc: 'Excel 导入或对接供应商账单' },
    { path: '/energy/recon', icon: 'contract', desc: '账户余额与消费流水对账' },
    { path: '/energy/exception', icon: 'shield', desc: '异常加注与未匹配流水' },
    { path: '/energy/analysis', icon: 'chart', desc: '单车成本与资金效率' },
    { path: '/energy/supplier', icon: 'people', desc: '维护能源供应商与站点' },
    { path: '/energy/setting', icon: 'settings', desc: '能源商品、车辆档案与风控阈值' }
  ],
  quickActions: [
    { title: '能源账户', path: '/energy/account', primary: true },
    { title: '能源消费', path: '/energy/consumption' }
  ],
  tips: [
    '先建供应商和账户，再发卡、充值，消费流水才能自动扣账',
    '司机垫付的加油只进台账，不扣能源账户，避免和任务费用单重复计成本'
  ]
};

export default energy;
