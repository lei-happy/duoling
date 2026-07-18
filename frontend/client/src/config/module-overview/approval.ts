import type { ModuleOverviewConfig } from './types';
import heroApproval from '@/assets/overview/hero-approval.svg';

/** 审批中心总览配置 */
const approval: ModuleOverviewConfig = {
  key: 'approval',
  title: '审批中心',
  positioning:
    '审批中心集中处理各业务发起的审批流转，提供我的待办、我的申请与审批记录，保障关键操作合规、可追溯。',
  description:
    '在这里统一发起与处理审批：查看待我审批的事项、跟踪我发起的申请进度，并可追溯全部历史审批记录，让关键决策留痕合规。',
  heroIllustration: heroApproval,
  accentColor: '#4263eb',
  moduleCards: [
    {
      path: '/approval/pending',
      icon: 'pending',
      desc: '处理待我审批的事项'
    },
    {
      path: '/approval/initiated',
      icon: 'initiated',
      desc: '查看我发起的审批申请及进度'
    },
    {
      path: '/approval/history',
      icon: 'history',
      desc: '追溯全部审批流转记录'
    }
  ],
  quickActions: [
    { title: '我的待办', path: '/approval/pending', primary: true },
    { title: '我的申请', path: '/approval/initiated' }
  ],
  tips: [
    '审批流程可在「企业配置 - 审批配置」中自定义',
    '关注「我的待办」及时处理，避免流程阻塞'
  ]
};

export default approval;
