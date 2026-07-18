import type { ModuleOverviewConfig } from './types';
import heroCapacity from '@/assets/overview/hero-capacity.svg';

/** 运力中心总览配置 */
const capacity: ModuleOverviewConfig = {
  key: 'capacity',
  title: '运力中心',
  positioning:
    '运力中心统一纳管自有、承运商与社会三类运力，维护车辆、司机、挂车档案及证照合规，为运营调度提供稳定可用的运力底座。',
  description:
    '在这里登记并审核各类运力资源，完善车辆与人员档案，持续监控证照到期与合规状态，确保调度环节始终有合规、可用的运力。',
  heroIllustration: heroCapacity,
  accentColor: '#7048e8',
  moduleCards: [
    {
      path: '/capacity/self-capacity',
      icon: 'vehicle',
      desc: '管理自有车辆、司机、挂车档案与变更记录'
    },
    {
      path: '/capacity/carrier-capacity',
      icon: 'carrier',
      desc: '管理承运商提供的运力及其审批'
    },
    {
      path: '/capacity/social-capacity',
      icon: 'social',
      desc: '维护社会零散运力资源池'
    },
    {
      path: '/capacity/compliance',
      icon: 'shield',
      desc: '监控车辆与人员证照到期与合规状态'
    }
  ],
  quickActions: [
    { title: '自有运力', path: '/capacity/self-capacity/list', primary: true },
    { title: '证照监控', path: '/capacity/compliance' }
  ],
  tips: [
    '车辆、司机、挂车信息完善后才能在调度中被分配',
    '关注「证照监控」的到期提醒，避免合规风险'
  ]
};

export default capacity;
