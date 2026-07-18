import type { ModuleOverviewConfig } from './types';

/** 日志中心总览配置 */
const logCenter: ModuleOverviewConfig = {
  key: 'log-center',
  title: '日志中心',
  positioning:
    '日志中心记录系统操作与登录行为，为安全审计、问题追溯与合规检查提供完整的行为轨迹。',
  description:
    '在这里查看用户的关键操作记录与账号登录记录，便于安全审计、异常排查与合规留痕。',
  heroIcon: 'list',
  accentColor: '#495057',
  workflow: [
    {
      title: '操作记录',
      desc: '追溯用户关键操作',
      icon: 'log',
      path: '/log-center/operation-log'
    },
    {
      title: '登录记录',
      desc: '查看账号登录行为',
      icon: 'login',
      path: '/log-center/login-log'
    }
  ],
  moduleCards: [
    {
      path: '/log-center/operation-log',
      icon: 'log',
      desc: '追溯用户关键操作记录'
    },
    {
      path: '/log-center/login-log',
      icon: 'login',
      desc: '查看账号登录行为记录'
    }
  ],
  quickActions: [
    { title: '操作记录', path: '/log-center/operation-log', primary: true },
    { title: '登录记录', path: '/log-center/login-log' }
  ],
  tips: [
    '出现异常操作时，可通过操作记录快速定位责任人与时间',
    '登录记录有助于发现异常登录并加强账号安全'
  ]
};

export default logCenter;
