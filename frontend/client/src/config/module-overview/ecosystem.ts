import type { ModuleOverviewConfig } from './types';

/** 服务平台总览配置 */
const ecosystem: ModuleOverviewConfig = {
  key: 'ecosystem',
  title: '服务平台',
  positioning:
    '服务平台连接货源、运力与增值服务，通过货源大厅、运力大厅与服务大厅，帮助企业对外拓展合作与资源交易。',
  description:
    '在这里对外协同：发布与获取货源，对接与匹配社会运力，并获取平台提供的各类增值服务，拓展业务合作边界。',
  heroIcon: 'box',
  accentColor: '#e8590c',
  workflow: [
    {
      title: '发布货源',
      desc: '发布与获取货源信息',
      icon: 'cargo',
      path: '/ecosystem/cargo-hall'
    },
    {
      title: '匹配运力',
      desc: '对接与匹配社会运力',
      icon: 'capacityHall',
      path: '/ecosystem/capacity-hall'
    },
    {
      title: '增值服务',
      desc: '获取平台各类增值服务',
      icon: 'service',
      path: '/ecosystem/service-hall'
    }
  ],
  moduleCards: [
    {
      path: '/ecosystem/cargo-hall',
      icon: 'cargo',
      desc: '发布与获取货源信息'
    },
    {
      path: '/ecosystem/capacity-hall',
      icon: 'capacityHall',
      desc: '对接与匹配社会运力'
    },
    {
      path: '/ecosystem/service-hall',
      icon: 'service',
      desc: '获取平台增值服务'
    }
  ],
  quickActions: [
    { title: '货源大厅', path: '/ecosystem/cargo-hall', primary: true },
    { title: '运力大厅', path: '/ecosystem/capacity-hall' }
  ],
  tips: [
    '货源与运力大厅可帮助在业务高峰期快速补充资源',
    '对外交易前建议完善企业与承运商资质信息'
  ]
};

export default ecosystem;
